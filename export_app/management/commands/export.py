from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class Command(SerializerExporterWithFields, BaseCommand):
    help = 'Export DRF serializer definition to an EmberJS model definition'

    def add_arguments(self, parser):
        parser.add_argument('model_endpoint', nargs='+')
        parser.add_argument('--adapter_name', default=settings.ADAPTER)
        parser.add_argument('--target_app', default=None,
                            help='force all relationships to the target_app instead of the model\'s app')

    def handle(self, *args, **options):
        target_app = options['target_app']
        adapter_name = options['adapter_name']
        if '.' not in adapter_name:
            adapter_name = 'export_app.adapters.{}'.format(adapter_name)
        Adapter = import_string(adapter_name)
        adapter = Adapter()

        for endpoint in options['model_endpoint']:
            try:
                model, serializer_instance, model_name, application_name = \
                    self.get_serializer_for_basename(endpoint)
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
            }

            adapter.write_to_file(application_name, model_name, context)
