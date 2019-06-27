from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class Command(SerializerExporterWithFields, BaseCommand):
    help = 'Export DRF serializer definition to a frontend model definition'

    def add_arguments(self, parser):
        parser.add_argument('model_endpoint', nargs='*',
                            help="The shorthand url(s) of the endpoint(s) for which you'd like to"
                                 " export models. Eg: 'sample/products'")
        parser.add_argument('--all', default=False, action='store_true',
                            help="Export all models corresponding to endpoints registered with your router")
        parser.add_argument('--adapter_name', default=settings.ADAPTER,
                            help='Defaults to {}'.format(settings.ADAPTER))
        parser.add_argument('--target_app', default=None,
                            help='Force all relationships to the target_app instead of the model\'s app')
        parser.add_argument('--router', default=None,
                            help='Defaults to {}'.format(settings.ROUTER_PATH))
        parser.add_argument('--noinput', default=False, action='store_true')

    def handle(self, *args, **options):
        target_app = options['target_app']
        adapter_name = options['adapter_name']
        if '.' not in adapter_name:
            adapter_name = 'export_app.adapters.{}'.format(adapter_name)
        Adapter = import_string(adapter_name)
        adapter = Adapter()

        excludes = settings.EXCLUDE
        if isinstance(excludes, dict):
            excludes = excludes.get(adapter_name.rsplit('.', 1)[-1], [])

        if options['router'] is not None:
            self.router = import_string(options['router'])
        endpoints = options['model_endpoint']

        if len(endpoints) == 0 and not options['all']:
            self.print_help('drf_auto_endpoint', 'export')
            return
        elif options['all'] and len(endpoints) > 0:
            raise CommandError('You need to specify either model_endpoint(s) or use --all but you '
                               'cannot use both at the same time')
        elif options['all']:
            endpoints = getattr(self.router, '_endpoints', {}).keys()

        for endpoint in endpoints:
            if endpoint not in excludes:
                endpoint_instance = self.get_endpoint_for_basename(endpoint)
                if adapter_name == settings.ADAPTER and \
                        getattr(endpoint_instance, 'default_export_adapter', None) is not None:
                    local_adapter_name = endpoint_instance.default_export_adapter.__name__
                    local_adapter = endpoint_instance.default_export_adapter()
                else:
                    local_adapter_name = adapter_name
                    local_adapter = adapter
                print('Exporting {} using {}'.format(endpoint, local_adapter_name))
                try:
                    if local_adapter.works_with in ['serializer', 'both']:
                        model, serializer_instance, model_name, application_name = \
                            self.get_serializer_for_basename(endpoint)

                        class BogusViewSet(object):
                            pagination_class = None

                        viewset = BogusViewSet()
                    if local_adapter.works_with in ['viewset', 'both']:
                        viewset, model_name, application_name = \
                            self.get_viewset_for_basename(endpoint, dasherize=local_adapter.dasherize)
                        viewset = viewset()
                except ModelNotFoundException as e:
                    raise CommandError('No viewset found for {}'.format(e.model))

                fields, rels = [], []

                if local_adapter.requires_fields:
                    fields, rels = self.get_fields_for_model(model, serializer_instance, local_adapter,
                                                             target_app, endpoint=endpoint_instance)

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

                if local_adapter.works_with in ['serializer', 'both']:
                    base = None
                    if not settings.IGNORE_BASE and model and \
                            model.__bases__[0].__name__ != 'django.db.models.base' and \
                            model.__bases__[0].__name__ != 'Model' and len(model.__bases__) == 1 and \
                            not model.__bases__[0]._meta.abstract:
                        base = (
                            model.__bases__[0].__name__.lower(),
                            model.__bases__[0].__module__.split('.')[0].lower().replace('_', '-')
                        )
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
                        'base': base,
                    }

                    local_adapter.write_to_file(application_name, model_name, context, options['noinput'])
                else:
                    local_adapter.write_to_file(application_name, model_name, viewset, options['noinput'])

        adapter.rebuild_index()
