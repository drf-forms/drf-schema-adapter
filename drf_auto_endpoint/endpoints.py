from django.utils.module_loading import import_string

from rest_framework import serializers, viewsets, relations
from rest_framework.fields import empty

from inflector import Inflector, English

from .factories import serializer_factory, viewset_factory
from .utils import get_validation_attrs, get_languages
from .app_settings import settings

try:
    from modeltranslation.translator import translator

except ImportError:
    class Translator(object):
        def get_registered_models(self, abstract=True):
            return []


    translator = Translator()


def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields()]


class Endpoint(object):

    base_serializer = import_string(settings.BASE_SERIALIZER)
    base_viewset = import_string(settings.BASE_VIEWSET)
    base_readonly_viewset = import_string(settings.BASE_READONLY_VIEWSET)

    model = None
    fields = None
    serializer = None

    fieldsets = None
    list_display = None
    list_editable = None

    permission_classes = None
    filter_fields = None
    search_fields = None
    ordering_fields = None
    page_size = None
    viewset = None

    read_only = False
    include_str = True
    list_me = True

    save_twice = False
    sortable_by = None

    custom_actions = None
    bulk_actions = None

    inflector_language = English

    _translated_fields = None
    _translated_field_names = None
    _default_language_field_names = None

    def __init__(self, model=None, **kwargs):
        self.inflector = Inflector(self.inflector_language)

        if model is not None:
            self.model = model

        arg_names = ('fields', 'serializer', 'permission_classes', 'filter_fields', 'search_fields',
                     'viewset', 'read_only', 'include_str', 'ordering_fields', 'page_size',
                     'base_viewset', 'fields_annotation', 'fieldsets', 'base_serializer', 'list_me')
        for arg_name in arg_names:
            setattr(self, arg_name, kwargs.pop(arg_name, getattr(self, arg_name, None)))

        if len(kwargs.keys()) > 0:
            raise Exception('{} got an unexpected keyword argument: "{}"'.format(
                self.__class__.__name__,
                kwargs.keys()[0]
            ))

        if self.serializer is not None:
            assert self.fields is None, 'You cannot specify both fields and serializer'
        else:
            assert self.viewset is not None or self.model is not None, \
                'You need to specify at least a model or a viewset'
            self.get_serializer()

        if self.viewset is not None:
            for attr in ('permission_classes', 'filter_fields', 'search_fields', 'ordering_fields',
                         'page_size'):
                assert getattr(self, attr, None) is None, \
                    'You cannot specify both {} and viewset'.format(attr)
        else:
            self.get_viewset()

        if self.model is None:
            self.model = self.get_serializer().Meta.model

    def get_languages(self):
        return get_languages()

    @property
    def singular_model_name(self):
        return self.model._meta.model_name.lower()

    @property
    def model_name(self):
        return self.inflector.pluralize(self.singular_model_name)

    @property
    def application_name(self):
        return self.model._meta.app_label.lower()

    def get_fields_for_serializer(self):

        if self.fields is None:
            self.fields = tuple([f for f in get_all_field_names(self.model)
                                 if f not in self.default_language_field_names])
            if self.include_str:
                self.fields += ('__str__', )

        return self.fields

    def get_serializer(self):

        if self.serializer is None:
            if self.viewset is None:
                self.serializer = serializer_factory(self)
            else:
                self.serializer = self.viewset.serializer_class

        return self.serializer

    def get_base_viewset(self):
        return self.base_viewset if not self.read_only or self.base_viewset != viewsets.ModelViewSet \
            else self.base_readonly_viewset

    def get_viewset(self):

        if self.viewset is None:
            self.viewset = viewset_factory(self)

        return self.viewset

    def get_url(self):

        return '{}/{}'.format(
            self.application_name.replace('_','-'),
            self.model_name.replace('_','-')
        )

    def _get_field_dict(self, field):

        serializer_instance = self.get_serializer()()
        name = field['name'] if isinstance(field, dict) else field
        field_instance = serializer_instance.fields[name]
        read_only = name == '__str__'
        if not read_only and field_instance.read_only:
            if not isinstance(field_instance, serializers.ManyRelatedField):
                read_only = True

        rv = {
            'key': name,
            'type': settings.WIDGET_MAPPING[field_instance.__class__.__name__],
            'read_only': read_only,
            'ui': {
                'label': name.title().replace('_', ' ') if name != '__str__' else \
                    serializer_instance.Meta.model.__name__,
            },
            'validation': {
                'required': field_instance.required,
            },
            'extra': {},
            'translated': name in self.get_translated_fields()
        }

        default = field_instance.default

        if self.fields_annotation and name in self.fields_annotation and 'placeholder' in self.fields_annotation[name]:
            rv['ui']['placeholder'] = self.fields_annotation[name]['placeholder']

        if default and default != empty:
            rv['default'] = default

        if getattr(field_instance, 'choices', None) is not None:
            if isinstance(field_instance, (relations.PrimaryKeyRelatedField, relations.ManyRelatedField)):
                model_field = self.model._meta.get_field(field_instance.source)
                related_model = model_field.related_model
                rv['type'] = settings.WIDGET_MAPPING[model_field.__class__.__name__]
                if model_field.__class__.__name__ == 'ManyToManyRel':
                    rv['validation']['required'] = False
                rv['related_endpoint'] = '{}/{}'.format(
                    related_model._meta.app_label,
                    related_model._meta.model_name.lower()
                )
            else:
                rv['type'] = settings.WIDGET_MAPPING['choice']
                rv['choices'] = [
                    {
                        'label': v,
                        'value': k,
                    } for k, v in field_instance.choices.items()
                ]

        rv['validation'].update(get_validation_attrs(field_instance))

        if isinstance(field, dict):
            extra = rv['extra']
            extra.update(field.get('extra', {}))
            rv.update(field)
            rv['extra'] = extra

        return rv

    def get_fields(self):
        return [
            self._get_field_dict(field)
            for field in self.get_fields_for_serializer()
        ]

    def get_fieldsets(self):
        from drf_auto_endpoint.app_settings import settings

        if self.fieldsets is not None:
            return [
                {
                    'title': None,
                    'fields': [{
                        'name': field
                    }
                    if not isinstance(field, dict) else field
                    for field in self.fieldsets ]
                }
            ]
        return [
            {
                'title': None,
                'fields': [{
                    'key': field
                }
                for field in self.get_fields_for_serializer()
                if field != 'id' and field != '__str__' and \
                    field not in self.translated_field_names and \
                    self._get_field_dict(field)['type'][:6] != 'tomany']
            }
        ]

    def get_list_display(self):
        if self.list_display is None:
            if '__str__' in self.get_fields_for_serializer():
                return ['__str__', ]
            return [self.get_fields()[0]['key']]
        return self.list_display

    def _get_endpoint_list(self, name):
        value = getattr(self, name, None)
        if value is None:
            return []
        return value

    def get_filter_fields(self):
        fields = self._get_endpoint_list('filter_fields')
        return fields

    @property
    def search_enabled(self):
        fields = self._get_endpoint_list('search_fields')
        return len(fields) > 0

    def get_ordering_fields(self):
        fields = self._get_endpoint_list('ordering_fields')
        return fields

    def get_needs(self):
        related_models = [
            f.related_model
            if f.related_model
            else f.model if f.model and f.model != self.model else None
            for f in self.model._meta.get_fields()
            if f.is_relation and f.name in self.get_fields_for_serializer()
        ]
        return [
            {
                'app': model._meta.app_label,
                'singular': model._meta.model_name.lower(),
                'plural': self.inflector.pluralize(model._meta.model_name.lower()),
            } for model in related_models
        ]

    def get_list_editable(self):
        if self.list_editable is None:
            return []
        return self.list_editable

    def get_sortable_by(self):
        return self.sortable_by

    def get_translated_fields(self):
        if self._translated_fields is None:
            models = translator.get_registered_models()
            if self.model in models:
                options = translator.get_options_for_model(self.model)
                rv = [field for field in options.fields]
                self._translated_fields = rv
            else:
                self._translated_fields = []
        return self._translated_fields

    @property
    def translated_field_names(self):
        if self._translated_field_names is None:
            rv = []
            for field in self.get_translated_fields():
                for language in self.get_languages():
                    l = language.replace('-', '_')
                    rv.append('{}_{}'.format(field, l))
            self._translated_field_names = rv
        return self._translated_field_names

    @property
    def default_language_field_names(self):
        from django.conf import settings as django_settings
        if self._default_language_field_names is None:
            l = django_settings.LANGUAGE_CODE.replace('-', '_')
            rv = []
            for field in self.get_translated_fields():
                rv.append('{}_{}'.format(field, l))
            self._default_language_field_names = rv
        return self._default_language_field_names

    def get_custom_actions(self):
        if self.custom_actions is None:
            return []
        return self.custom_actions

    def get_bulk_actions(self):
        if self.bulk_actions is None:
            return []
        return self.bulk_actions
