from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class Command(SerializerExporterWithFields, BaseCommand):
    help = 'Export DRF serializer definition to a frontend model definition'

    def add_arguments(self, parser):
        parser.add_argument('wizard_endpoint', nargs='*',
                            help="The shorthand url(s) of the endpoint(s) for which you'd like to export models."
                                 " Eg: 'sample/products'")
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

        if options['router'] is not None:
            self.router = import_string(options['router'])
        endpoints = options['wizard_endpoint']

        if len(endpoints) == 0 and not options['all']:
            self.print_help('drf_auto_endpoint', 'export')
            return
        elif options['all'] and len(endpoints) > 0:
            raise CommandError('You need to specify either wizard_endpoint(s) or use --all but you'
                               ' cannot use both at the same time')
        elif options['all']:
            endpoints = []
            for path, endpoint in getattr(self.router, '_endpoints', {}).items():
                viewset = endpoint.get_viewset()
                for method in dir(viewset):
                    if hasattr(getattr(viewset, method), 'wizard') and getattr(viewset, method).wizard:
                        endpoints.append('{}/{}'.format(path, method))

        for endpoint in endpoints:
            print('Exporting {} using {}'.format(endpoint, adapter_name))
            base_name, method_name = endpoint.rsplit('/', 1)

            try:
                viewset, model_name, application_name = self.get_viewset_for_basename(base_name)
                serializer = getattr(viewset, method_name).serializer
                serializer_instance = serializer()
            except ModelNotFoundException as e:
                raise CommandError('No viewset found for {}'.format(e.model))

            fields, rels = [], []

            if adapter.requires_fields:
                fields, rels = self.get_fields_for_model(None, serializer_instance, adapter,
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

            base_name = 'wizard/{}'.format(base_name)
            context = {
                'endpoint': 'wizard/{}'.format(endpoint),
                'model_name': method_name,
                'application_name': base_name,
                'fields': fields,
                'rels': rels,
                'belongsTo': belongsTo,
                'hasMany': hasMany,
                'target_app': target_app,
                'api_base': settings.BACK_API_BASE,
                'pagination_container': None,
                'updir': 3,
            }

            print('writing {}/{}'.format(base_name, method_name))
            adapter.write_to_file(base_name, method_name, context, options['noinput'])
