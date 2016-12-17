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
