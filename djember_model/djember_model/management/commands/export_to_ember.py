import os

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings as django_settings

from djember_model import settings
from djember_model.base import SerializerExporter, ModelNotFoundException


class Command(SerializerExporter, BaseCommand):
    help = 'Export DRF serializer definition to an EmberJS model definition'
    base_template_name = 'djember_model/ember_model_base.js'
    template_name = 'djember_model/ember_model.js'
    test_template_name = 'djember_model/ember_model_test.js'

    def add_arguments(self, parser):
        parser.add_argument('model_endpoint', nargs='+')
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

            base_target_dir = os.path.join(django_settings.BASE_DIR, settings.EMBER_APPLICATION_PATH,
                                           'app', 'models', 'base', application_name)
            target_dir = os.path.join(django_settings.BASE_DIR, settings.EMBER_APPLICATION_PATH,
                                      'app', 'models', application_name)
            test_target_dir = os.path.join(django_settings.BASE_DIR, settings.EMBER_APPLICATION_PATH,
                                           'tests', 'unit', 'models', application_name)

            filename = '{}.js'.format(model_name)
            test_filename = '{}-test.js'.format(model_name)

            for directory in (base_target_dir, target_dir, test_target_dir):
                if not os.path.exists(directory):
                    os.makedirs(directory)

            with open(os.path.join(base_target_dir, filename), 'w') as f:
                output = render_to_string(self.base_template_name, context)
                f.write(output)

            if not os.path.exists(os.path.join(target_dir, filename)):
                with open(os.path.join(target_dir, filename), 'w') as f:
                    output = render_to_string(self.template_name, context)
                    f.write(output)

                # if the actual model doesn't exist we assume the test doesn't exist either
                # and vice-versa
                with open(os.path.join(test_target_dir, test_filename), 'w') as f:
                    output = render_to_string(self.test_template_name, context)
                    f.write(output)


