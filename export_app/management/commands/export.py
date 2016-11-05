from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporter, ModelNotFoundException


class Command(SerializerExporter, BaseCommand):
    help = 'Export DRF serializer definition to an EmberJS model definition'
    base_template_name = 'djember_model/ember_model_base.js'
    template_name = 'djember_model/ember_model.js'
    test_template_name = 'djember_model/ember_model_test.js'

    def add_arguments(self, parser):
        parser.add_argument('model_endpoint', nargs='+')
        parser.add_argument('--adapter_name', default=settings.EXPORTER_ADAPTER)
        parser.add_argument('--target_app', default=None,
                            help='force all relationships to the target_app instead of the model\'s app')

    def handle(self, *args, **options):
        target_app = options['target_app']
        for endpoint in options['model_endpoint']:
            try:
                model, serializer_instance, model_name, application_name = \
                    self.get_serializer_for_model(endpoint)
            except ModelNotFoundException as e:
                raise CommandError('No viewset found for {}'.format(e.model))

            fields, rels = self.get_fields_for_model(model, serializer_instance, target_app)

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
                'hasMany': hasMany
            }

            Adapter = import_string('exporter_app.{}'.format(settings.ADAPTER))
            adapter = Adapter(context, application_name, model_name)
            adapter.write_to_file()
