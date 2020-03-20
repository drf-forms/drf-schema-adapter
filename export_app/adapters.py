import os
from collections import defaultdict

from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.utils.module_loading import import_string

from export_app import settings


try:
    input = raw_input
except NameError:
    pass


# from http://stackoverflow.com/questions/3203286/how-to-create-a-read-only-class-property-in-python#3203659
class classproperty(object):

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class BaseAdapter(object):

    FIELD_TYPE_MAPPING = {}
    DEFAULT_MAPPING = None

    requires_fields = False
    works_with = 'serializer'
    dasherize = False

    def __init__(self):
        assert not self.requires_fields or self.works_with != 'viewset', """
            Field information is provided by a serializer. Your adapter requires field information
            (requires_fields = True) and therefore also needs to "works_with" serializer.
            If you also require information from the viewset, please update "works_with" to "both"
            otherwise use "works_with = 'serializer'"
        """

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

    def write_to_file(self, application_name, model_name, context, force_overwrite=False):
        raise NotImplementedError("You need to implement your Adapter")

    def create_dirs(self, *args):
        for directory in args:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except FileExistsError:
                    # someone created the directory in the meantime
                    # tis can happen in parrallel tests
                    pass

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
        with open(target_file, 'w', encoding='utf-8') as f:
            output = render_to_string(template, context)
            f.write(output)

    def write_files(self, context, files):
        self.create_dirs(*[file[0] for file in files])
        for file in files:
            self.write_file(context, *file)

    def rebuild_index(self):
        pass

    @classmethod
    def adapt_fields_for_model(cls, fields, relationships):
        return fields, relationships


class EmberAdapter(BaseAdapter):

    FIELD_TYPE_MAPPING = {
        'BooleanField': 'boolean',
        'NullBooleanField': None,
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'ListField': None,
        'DictField': None,
        'JSONField': None,
        'PrimaryKeyRelatedField': 'belongsTo',
        'SlugRelatedField': 'belongsTo',
        'ManyRelatedField': 'hasMany',
        'DateField': 'nullable',
        'DateTimeField': 'nullable',
        'TimeField': 'nullable',
        'DurationField': 'duration',
        'UUIDField': 'nullable',
    }
    DEFAULT_MAPPING = 'string'
    requires_fields = True
    dasherize = True

    base_template_name = 'export_app/ember_model_base.js'
    template_name = 'export_app/ember_model.js'
    test_template_name = 'export_app/ember_model_test.js'
    dynamic_template_name = 'export_app/dynamic_model.js'

    def write_to_file(self, application_name, model_name, context, force_overwrite=False):
        context['application_name'] = context['application_name'].replace('_', '-')
        context['updir'] = context.get('updir', 1)
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'app', 'models', 'base', application_name.replace('_', '-'))
        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'app', 'models', application_name.replace('_', '-'))
        test_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                       'tests', 'unit', 'models', application_name.replace('_', '-'))

        filename = '{}.js'.format(model_name).replace('_', '-')
        test_filename = '{}-test.js'.format(model_name).replace('_', '-')

        files = [
            (base_target_dir, filename, self.base_template_name, True),
            (target_dir, filename, self.template_name, False),
            (test_target_dir, test_filename, self.test_template_name, 'confirm' if not force_overwrite else False)
        ]
        self.write_files(context, files)


class BaseMetadataAdapter(BaseAdapter):

    works_with = 'viewset'

    def render(self, data):
        from rest_framework.renderers import JSONRenderer

        renderer = JSONRenderer()
        return renderer.render(data)

    def get_metadata_from_viewset(self, viewset):

        if isinstance(viewset, dict):
            output = viewset
        else:
            MetadataClass = import_string(django_settings.REST_FRAMEWORK['DEFAULT_METADATA_CLASS'])
            output = MetadataClass().determine_metadata(None, viewset)

        return output

    def get_json(self, viewset):

        return self.render(self.get_metadata_from_viewset(viewset))


class MetadataAdapter(BaseMetadataAdapter):

    def write_to_file(self, application_name, model_name, viewset, force_overwrite=False):

        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'data')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        filename = '{}-{}.json'.format(application_name, model_name)

        with open(os.path.join(target_dir, filename), 'wb') as f:
            f.write(self.get_json(viewset))


class MetadataES6Adapter(BaseMetadataAdapter):

    template_name = 'export_app/ember_metadata.js'
    index_template_name = 'export_app/ember_metadata_index.js'

    def walk_dir(self, base, ignore_index=False, prefix=''):
        from inflector import Inflector
        from django.utils.module_loading import import_string
        from drf_auto_endpoint.app_settings import settings as auto_settings

        inflector_language = import_string(auto_settings.INFLECTOR_LANGUAGE)
        inflector = Inflector(inflector_language)

        imports = []

        for item in os.listdir(base):
            filename = os.path.join(base, item)
            if os.path.isdir(filename):
                imports += self.walk_dir(filename, prefix=os.path.join(prefix, item.replace('_', '-')))
            elif item == 'index.js' and ignore_index:
                continue
            else:
                try:
                    base_name, extension = item.rsplit('.', 1)
                except ValueError:
                    # a file without extension
                    continue
                if extension != 'js':
                    continue
                imports.append((
                    os.path.join(prefix, inflector.pluralize(base_name)),
                    os.path.join(prefix, base_name).replace('/', '_').replace('-', '_'),
                    os.path.join('.', prefix.replace('-', '_'), base_name)
                ))
        return imports

    def rebuild_index(self):
        MetadataClass = import_string(django_settings.REST_FRAMEWORK['DEFAULT_METADATA_CLASS'])
        context = {}
        directory = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                 'app', 'data')
        context['items'] = self.walk_dir(directory, True)
        context['root_metadata'] = self.render(
            MetadataClass().determine_metadata(None, 'APIRootView')
        ).decode('utf-8')
        self.write_file(context, directory, 'index.js', self.index_template_name, True)

    def write_to_file(self, application_name, model_name, viewset, force_overwrite=False):
        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'app', 'data', application_name)

        self.create_dirs(target_dir)
        filename = '{}.js'.format(model_name)

        output = self.get_json(viewset)

        context = {
            'json': output.decode('utf-8')
        }

        self.write_file(context, target_dir, filename, self.template_name, True)


class MobxAxiosAdapter(BaseAdapter):

    works_with = 'both'
    requires_fields = True

    config_template_name = 'export_app/mobxaxios_config.js'
    base_model_template_name = 'export_app/mobxaxios_base_model.js'
    model_base_template_name = 'export_app/mobxaxios_model_base.js'
    model_template_name = 'export_app/mobxaxios_model.js'
    base_store_template_name = 'export_app/mobxaxios_base_store.js'
    store_template_name = 'export_app/mobxaxios_store.js'

    def write_to_file(self, application_name, model_name, context, force_overwrite=False):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH)
        config_target_dir = os.path.join(base_target_dir, 'config')
        model_target_dir = os.path.join(base_target_dir, 'models')
        model_base_target_dir = os.path.join(model_target_dir, 'base')
        store_target_dir = os.path.join(base_target_dir, 'stores')

        filename = '{}{}.js'.format(application_name, model_name)

        files = [
            (config_target_dir, 'axios-config.js', self.config_template_name, False),
            (store_target_dir, '_base.js', self.base_store_template_name, True),
            (store_target_dir, filename, self.store_template_name, 'confirm' if not force_overwrite else False),
            (model_base_target_dir, '_base.js', self.base_model_template_name, True),
            (model_base_target_dir, filename, self.model_base_template_name, True),
            (model_target_dir, filename, self.model_template_name, False)
        ]
        self.write_files(context, files)


class Angular2Adapter(BaseAdapter):

    FIELD_TYPE_MAPPING = {
        'BooleanField': 'boolean',
        'NullBooleanField': 'boolean',
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'ListField': 'any',
        'DictField': 'any',
        'JSONField': 'any',
        'PrimaryKeyRelatedField': 'belongsTo',
        'ManyRelatedField': 'hasMany',
    }
    DEFAULT_MAPPING = 'string'
    requires_fields = True

    base_template_name = 'export_app/angular2_model_base.ts'
    template_name = 'export_app/angular2_model.ts'
    service_base_template_name = 'export_app/angular2_service_base.ts'
    service_template_name = 'export_app/angular2_service.ts'

    def write_to_file(self, application_name, model_name, context, force_overwrite=False):
        file_model_name = model_name
        context['application_name'] = context['application_name']
        context['updir'] = context.get('updir', 1)
        target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH,
                                  'app', 'models', application_name)

        base_filename = '{}.base.ts'.format(file_model_name)
        filename = '{}.ts'.format(file_model_name)
        service_base_filename = '{}.service.base.ts'.format(file_model_name)
        service_filename = '{}.service.ts'.format(file_model_name)

        files = [
            (target_dir, base_filename, self.base_template_name, True),
            (target_dir, service_base_filename, self.service_base_template_name, True),
            (target_dir, filename, self.template_name, False if force_overwrite else 'confirm'),
            (target_dir, service_filename, self.service_template_name, False if force_overwrite else 'confirm'),
        ]
        self.write_files(context, files)


class VuexORMAxiosAdapter(BaseAdapter):

    FIELD_TYPE_MAPPING = {
        'ListField': None,
        'DictField': None,
        'JSONField': None,
        'BooleanField': 'boolean',
        'NullBooleanField': 'boolean',
        'IntegerField': 'number',
        'DecimalField': 'number',
        'PrimaryKeyRelatedField': 'number',
        'SludRelatedField': 'string',
        'UUIDField': 'uid',
        'ManyRelatedField': None,
    }
    DEFAULT_MAPPING = 'string'

    works_with = 'both'
    requires_fields = True

    database_template_name = 'export_app/vuexorm_axios_database.js'
    base_model_template_name = 'export_app/vuexorm_axios_base_model.js'
    model_base_template_name = 'export_app/vuexorm_axios_model_base.js'
    model_template_name = 'export_app/vuexorm_axios_model.js'

    def write_to_file(self, application_name, model_name, context, force_overwrite=False):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH)
        base_model_target_dir = os.path.join(base_target_dir, 'models')
        model_target_dir = os.path.join(base_model_target_dir, application_name)

        filename = '{}.js'.format(model_name)

        files = [
            # (database_target_dir, 'database.js', self.database_template_name, True),
            (base_model_target_dir, 'Base.js', self.base_model_template_name, True),
            (os.path.join(model_target_dir, 'base'), filename, self.model_base_template_name, True),
            (model_target_dir, filename, self.model_template_name, False),
        ]

        self.write_files(context, files)

    def walk_dir(self, base, ignore_index=False, prefix=''):
        imports = []

        for item in os.listdir(base):
            filename = os.path.join(base, item)
            if os.path.isdir(filename):
                if item == 'base':
                    continue
                imports += self.walk_dir(filename, prefix=os.path.join(prefix, item.replace('_', '-')))
            elif item == 'Base.js':
                continue
            else:
                try:
                    base_name, extension = item.rsplit('.', 1)
                except ValueError:
                    # a file without extension
                    continue
                if extension != 'js':
                    continue
                imports.append((
                    os.path.join(prefix, base_name).replace('/', '_').replace('-', '_'),
                    os.path.join(prefix.replace('-', '_'), base_name)
                ))
        return imports

    def rebuild_index(self):
        base_target_dir = os.path.join(django_settings.BASE_DIR, settings.FRONT_APPLICATION_PATH)
        directory = os.path.join(base_target_dir, 'models')
        database_target_dir = os.path.join(base_target_dir, 'store')

        context = {
            'items': self.walk_dir(directory, True)
        }

        self.write_file(context, database_target_dir, 'database.js', self.database_template_name, True)
