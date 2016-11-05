import os

from django.conf import settings as django_settings
from django.template.loader import render_to_string

from export_app import settings


class BaseAdapter(object):

    def __init__(self, context, application_name, model_name):
        self.context = context
        self.application_name = application_name
        self.model_name = model_name

    def write_to_file(self, context):
        raise NotImplemented("You need to implement your Adapter")


class EmberAdapter(BaseAdapter):
    def write_to_file(self):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'app', 'models', 'base', self.application_name)
        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'app', 'models', self.application_name)
        test_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'tests', 'unit', 'models', self.application_name)

        filename = '{}.js'.format(self.model_name)
        test_filename = '{}-test.js'.format(self.model_name)

        for directory in (base_target_dir, target_dir, test_target_dir):
            if not os.path.exists(directory):
                os.makedirs(directory)

        with open(os.path.join(base_target_dir, filename), 'w') as f:
            output = render_to_string(self.base_template_name, self.context)
            f.write(output)

        if not os.path.exists(os.path.join(target_dir, filename)):
            with open(os.path.join(target_dir, filename), 'w') as f:
                output = render_to_string(self.template_name, self.context)
                f.write(output)

            # if the actual model doesn't exist we assume the test doesn't exist either
            # and vice-versa
            with open(os.path.join(test_target_dir, test_filename), 'w') as f:
                output = render_to_string(self.test_template_name, self.context)
                f.write(output)
