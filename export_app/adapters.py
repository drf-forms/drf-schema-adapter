import os
from collections import defaultdict

from django.conf import settings as django_settings
from django.template.loader import render_to_string

from export_app import settings


# from http://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python#3203659
class classproperty(object):

    def __init__(self, getter):
        self.getter= getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class BaseAdapter(object):

    FIELD_TYPE_MAPPING = {}
    DEFAULT_MAPPING = None

    requires_fields = False
    works_with = 'serializer'

    @classproperty
    def field_type_mapping(cls):
        default = cls.FIELD_TYPE_MAPPING
        default.update(settings.FIELD_TYPE_MAPPING)
        rv = defaultdict(lambda: cls.default_mapping)
        for k, v in default.items():
            rv[k] = v
        return rv

    @classproperty
    def default_mapping(cls):
        rv = settings.DEFAULT_MAPPING
        if rv is None:
            return cls.DEFAULT_MAPPING
        return rv

    def write_to_file(self, application_name, model_name, context):
        raise NotImplemented("You need to implement your Adapter")

    def create_dirs(self, *args):
        for directory in args:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def write_file(self, context, target_dir, filename, template, overwrite='confirm'):
        target_file = os.path.join(target_dir, filename)
        if os.path.exists(target_file):
            if not overwrite:
                return
            if overwrite == 'confirm':
                answer = 'anything else'
                while answer.lower() not in ('', 'yes', 'y', 'no', 'n'):
                    answer = input('{} already exists, do you want to overwrite it? [y/N] '.format(
                        target_file
                    ))
                    if answer.lower() in ('', 'no', 'n'):
                        return
        with open(target_file, 'w') as f:
            output = render_to_string(template, context)
            f.write(output)

    def write_files(self, context, files):
        self.create_dirs(*[file[0] for file in files])
        for file in files:
            self.write_file(context, *file)


class EmberAdapter(BaseAdapter):

    FIELD_TYPE_MAPPING = {
        'BooleanField': 'boolean',
        'NullBooleanField': 'boolean',
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'ListField': None,
        'DictField': None,
        'JSONField': None,
        'PrimaryKeyRelatedField': 'belongsTo',
        'ManyRelatedField': 'hasMany',
    }
    DEFAULT_MAPPING = 'string'
    requires_fields = True

    base_template_name = 'export_app/ember_model_base.js'
    template_name = 'export_app/ember_model.js'
    test_template_name = 'export_app/ember_model_test.js'
    dynamic_template_name = 'export_app/dynamic_model.js'

    def write_to_file(self, application_name, model_name, context):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'app', 'models', 'base', application_name)
        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'app', 'models', application_name)
        test_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'tests', 'unit', 'models', application_name)

        filename = '{}.js'.format(model_name)
        test_filename = '{}-test.js'.format(model_name)

        files = [
            (base_target_dir, filename, self.base_template_name, True),
            (target_dir, filename, self.template_name, False),
            (test_target_dir, test_filename, self.test_template_name)
        ]
        self.write_files(context, files)


class MetadataAdapter(BaseAdapter):

    works_with = 'viewset'

    def write_to_file(self, application_name, model_name, viewset):
        import json
        from drf_auto_endpoint.metadata import MinimalAutoMetadata

        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'data')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        filename = '{}-{}.json'.format(application_name, model_name)

        with open(os.path.join(target_dir, filename), 'w') as f:
            output = MinimalAutoMetadata().determine_metadata(None, viewset)
            json.dump(output, f, indent=2)


class MobxAxiosAdapter(BaseAdapter):

    works_with = 'both'
    requires_fields = True

    config_template_name = 'export_app/mobxaxios_config.js'
    base_model_template_name = 'export_app/mobxaxios_base_model.js'
    model_base_template_name = 'export_app/mobxaxios_model_base.js'
    model_template_name = 'export_app/mobxaxios_model.js'
    base_store_template_name = 'export_app/mobxaxios_base_store.js'
    store_template_name = 'export_app/mobxaxios_store.js'

    def write_to_file(self, application_name, model_name, context):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH)
        config_target_dir = os.path.join(base_target_dir, 'config')
        model_target_dir = os.path.join(base_target_dir, 'models')
        model_base_target_dir = os.path.join(model_target_dir, 'base')
        store_target_dir = os.path.join(base_target_dir, 'stores')

        filename = '{}{}.js'.format(application_name, model_name)

        files = [
            (config_target_dir, 'axios-config.js', self.config_template_name, False),
            (store_target_dir, '_base.js', self.base_store_template_name, True),
            (store_target_dir, filename, self.store_template_name),
            (model_base_target_dir, '_base.js', self.base_model_template_name, True),
            (model_base_target_dir, filename, self.model_base_template_name, True),
            (model_target_dir, filename, self.model_template_name, False)
        ]
        self.write_files(context, files)
