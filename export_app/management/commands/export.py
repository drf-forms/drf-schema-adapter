from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string
from django.conf import settings as django_settings

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class Command(SerializerExporterWithFields, BaseCommand):
    help = 'Export DRF serializer definition to a frontend model definition'

    def add_arguments(self, parser):
        parser.add_argument('model_endpoint', nargs='*',
                            help="The shorthand url(s) of the endpoint(s) for which you'd like to export models. Eg: 'sample/products'")
        parser.add_argument('--all', default=False, action='store_true',
                            help="Export all models corresponding to endpoints registered with your router")
        parser.add_argument('--adapter_name', default=settings.ADAPTER,
                            help='Defaults to {}'.format(settings.ADAPTER))
        parser.add_argument('--target_app', default=None,
                            help='Force all relationships to the target_app instead of the model\'s app')
        parser.add_argument('--router', default=None,
                            help='Defaults to {}'.format(settings.ROUTER_PATH))

    def handle(self, *args, **options):
        target_app = options['target_app']
        adapter_name = options['adapter_name']
        if '.' not in adapter_name:
            adapter_name = 'export_app.adapters.{}'.format(adapter_name)
        Adapter = import_string(adapter_name)
        adapter = Adapter()

        if options['router'] is not None:
            self.router = import_string(options['router'])
        endpoints = options['model_endpoint']

        if len(endpoints) == 0 and not options['all']:
            self.print_help('drf_auto_endpoint', 'export')
            return
        elif options['all'] and len(endpoints) > 0:
            raise CommandError('You need to specify either model_endpoint(s) or use --all but you cannot use both at the same time')
        elif options['all']:
            endpoints = getattr(self.router, '_endpoints', {}).keys()

        for endpoint in endpoints:
            print('Exporting {} using {}'.format(endpoint, adapter_name))
            try:
                if adapter.works_with in ['serializer', 'both']:
                    model, serializer_instance, model_name, application_name = \
                        self.get_serializer_for_basename(endpoint)

                    class BogusViewSet(object):
                        pagination_class = None

                    viewset = BogusViewSet()
                if adapter.works_with in ['viewset', 'both']:
                    viewset, model_name, application_name = self.get_viewset_for_basename(endpoint)
            except ModelNotFoundException as e:
                raise CommandError('No viewset found for {}'.format(e.model))

            fields, rels = [], []

            if adapter.requires_fields:
                fields, rels = self.get_fields_for_model(model, serializer_instance, adapter,
                                                         target_app)

            belongsTo = False
            hasMany = False

            for rel in rels:
                if rel['type'] == 'belongsTo':
                    belongsTo = True
                    if hasMany:
                        break
                else:
                    hasMany = True
                    if belongsTo:
                        break

            if adapter.works_with in ['serializer', 'both']:
                context = {
                    'endpoint': endpoint,
                    'model_name': model_name,
                    'application_name': application_name,
                    'fields': fields,
                    'rels': rels,
                    'belongsTo': belongsTo,
                    'hasMany': hasMany,
                    'target_app': target_app,
                    'api_base': settings.BACK_API_BASE,
                    'pagination_container': 'result' if getattr(viewset, '.pagination_class', None) \
                        is not None or getattr(django_settings, 'REST_FRAMEWORK', {}). \
                        get('DEFAULT_PAGINATION_CLASS', None) is not None else None
                }

                adapter.write_to_file(application_name, model_name, context)
            else:
                adapter.write_to_file(application_name, model_name, viewset)
