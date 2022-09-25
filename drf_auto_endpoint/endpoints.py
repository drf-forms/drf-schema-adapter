try:
    from collections import Iterable
except ImportError:
    from collections.abc import Iterable
import json
import os

from django.db.models.fields.related import ForeignKey
from django.conf import settings as django_settings
from django.urls import reverse
from django.utils.module_loading import import_string

from inflector import Inflector

from .factories import serializer_factory, viewset_factory
from .utils import get_languages, get_field_dict
from .app_settings import settings

try:
    from modeltranslation.translator import translator

except ImportError:
    class Translator(object):
        def get_registered_models(self, abstract=True):
            return []

    translator = Translator()


def get_all_field_names(model):
    return [
        field.name
        for field in model._meta.get_fields()
        if not hasattr(field, 'field') or getattr(field, 'related_name', None) is not None
    ]


class EndpointMetaClass(type):

    def __new__(cls, name, bases, attrs):
        new_class = super(EndpointMetaClass, cls).__new__(cls, name, bases, attrs)
        inflector = None

        processed = []

        black_list = dir(BaseEndpoint)
        model = getattr(new_class, 'model', None)

        for base in reversed(new_class.__mro__):
            for key, value in list(base.__dict__.items()):
                if key not in black_list and key not in processed and hasattr(value, 'wizard') and value.wizard:
                    if getattr(value, 'action_kwargs', {}).get('params', {}).get('model', None) is None:

                        if model is not None:
                            if inflector is None:
                                inflector_language = import_string(settings.INFLECTOR_LANGUAGE)
                                inflector = Inflector(inflector_language)

                            getattr(new_class, key).action_kwargs['params']['model'] = '{}/{}/{}'.format(
                                model._meta.app_label.lower().replace('_', '-'),
                                inflector.pluralize(model._meta.model_name.lower()),
                                value.__name__
                            )

                            processed.append(key)

                    if getattr(value, 'action_kwargs', {}).get('params', {}).get('fieldsets', None) is None \
                            and getattr(new_class, 'model', None) is not None and hasattr(value, 'serializer'):

                        fieldsets_path = os.path.join(
                            django_settings.BASE_DIR,
                            new_class._fieldsets_location,
                            new_class.__module__.rsplit('.', 1)[0],
                            'fieldsets.json'
                        )

                        try:
                            with open(fieldsets_path, 'r') as f:
                                fieldsets = json.load(f)
                                value.action_kwargs['params']['fieldsets'] = \
                                    fieldsets['{}_{}'.format(new_class.model.__name__, key)]
                        except FileNotFoundError:
                            pass
                        except KeyError:
                            pass

                        if getattr(value, 'action_kwargs', {}).get('params', {}).get('fieldsets', None) is None:
                            value.action_kwargs = getattr(value, 'action_kwargs', {})
                            value.action_kwargs['params'] = value.action_kwargs.get('params', {})
                            value.action_kwargs['params']['fieldsets'] = [
                                {'name': field}
                                for field in value.serializer().fields.keys()
                            ]

        if getattr(new_class, 'fieldset_name', None) is not None:
            fieldsets_path = os.path.join(
                django_settings.BASE_DIR,
                new_class.__module__.rsplit('.', 1)[0],
                'fieldsets.json'
            )
            try:
                with open(fieldsets_path, 'r') as f:
                    fieldsets = json.load(f)
                    new_class.fieldsets = fieldsets[new_class.fieldset_name]
            except FileNotFoundError:
                pass
            except KeyError:
                pass

        if new_class.fieldsets is None and new_class.model is not None:
            fieldsets_path = os.path.join(
                django_settings.BASE_DIR,
                new_class.__module__.rsplit('.', 1)[0],
                'fieldsets.json'
            )
            try:
                with open(fieldsets_path, 'r') as f:
                    fieldsets = json.load(f)
                    new_class.fieldsets = fieldsets[new_class.model.__name__]
            except FileNotFoundError:
                pass
            except KeyError:
                pass

        return new_class


class BaseEndpoint(object):

    base_serializer = import_string(settings.BASE_SERIALIZER)
    base_viewset = import_string(settings.BASE_VIEWSET)
    base_readonly_viewset = import_string(settings.BASE_READONLY_VIEWSET)

    model = None
    fields = None
    exclude_fields = ()
    extra_fields = None
    foreign_key_as_list = False

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
    list_actions = None

    inflector_language = import_string(settings.INFLECTOR_LANGUAGE)

    _translated_fields = None
    _translated_field_names = None
    _default_language_field_names = None
    _fieldsets_location = ''

    def get_languages(self):
        return get_languages()

    @property
    def singular_model_name(self):
        try:
            return self.model._meta.model_name.lower()
        except AttributeError:
            return self.url.lower()

    @property
    def model_name(self):
        return self.inflector.pluralize(self.singular_model_name)

    def get_singular_full_name(self):

        return '{}/{}'.format(
            self.application_name.replace('_', '-'),
            self.singular_model_name.replace('_', '-')
        )

    @property
    def application_name(self):
        try:
            return self.model._meta.app_label.lower()
        except AttributeError:
            return ''

    def get_exclude_fields(self):
        return self.exclude_fields

    def get_fields_for_serializer(self):

        if self.fields is None:
            if self.serializer is not None:
                return self.serializer().fields.keys()

            self.fields = tuple([f for f in get_all_field_names(self.model)
                                 if f not in self.default_language_field_names and
                                 f not in self.get_exclude_fields()])
            if self.extra_fields is not None:
                self.fields += tuple(self.extra_fields)
            if self.include_str:
                self.fields += ('__str__', )

        return self.fields

    def get_serializer(self, data=None):

        if self.serializer is None:
            if self.viewset is None:
                self.serializer = serializer_factory(self)
            elif isinstance(self.viewset, type):
                viewset = self.viewset()
                self.serializer = viewset.get_serializer_class()
            else:
                self.serializer = self.viewset.get_serializer_class()

        if data is None:
           return self.serializer

        return self.serializer(data)

    def get_base_viewset(self):
        if not self.read_only:
            return self.base_viewset
        if '{}.{}'.format(self.base_readonly_viewset.__module__, self.base_readonly_viewset.__name__) \
                == settings.BASE_READONLY_VIEWSET and \
                '{}.{}'.format(self.base_viewset.__module__, self.base_viewset.__name__) \
                != settings.BASE_VIEWSET:
            return self.base_viewset
        return self.base_readonly_viewset

    def get_viewset(self):

        if self.viewset is None:
            self.viewset = viewset_factory(self)

        return self.viewset

    def get_url(self):

        if hasattr(self, 'url') and self.url is not None:
            return self.url

        return '{}/{}'.format(
            self.application_name.replace('_', '-'),
            self.model_name.replace('_', '-')
        )

    def _get_field_dict(self, field):
        foreign_key_as_list = (isinstance(self.foreign_key_as_list, Iterable) and field in self.foreign_key_as_list) \
            or (not isinstance(self.foreign_key_as_list, Iterable) and self.foreign_key_as_list)

        return get_field_dict(field, self.get_serializer(), self.get_translated_fields(),
                              self.fields_annotation, self.model, foreign_key_as_list=foreign_key_as_list)

    def get_fields(self):
        return [
            self._get_field_dict(field)
            for field in self.get_fields_for_serializer()
        ]

    def get_fieldsets(self):

        if django_settings.DEBUG:
            fieldsets_path = os.path.join(
                django_settings.BASE_DIR,
                self._fieldsets_location,
                self.__module__.rsplit('.', 1)[0],
                'fieldsets.json'
            )

            try:
                with open(fieldsets_path, 'r') as f:
                    fieldsets = json.load(f)
                    if hasattr(self, 'fieldset_name'):
                        self.fieldsets = fieldsets[self.fieldset_name]
                    else:
                        self.fieldsets = fieldsets[self.model.__name__]
            except FileNotFoundError:
                pass
            except KeyError:
                pass

        if self.fieldsets is not None:
            return [{'key': field} if not isinstance(field, dict)
                    else field
                    for field in self.fieldsets]

        return [{'key': field}
                for field in self.get_fields_for_serializer()
                if field != 'id' and field != '__str__' and
                field not in self.translated_field_names and
                self._get_field_dict(field).get('type', '')[:6] != 'tomany']

    def get_list_display(self):
        if self.list_display is None:
            if '__str__' in self.get_fields_for_serializer():
                return ['__str__', ]
            return [self.get_fields()[0]['key']]
        elif self.list_display == '__all__':
            return self.get_fields_for_serializer()
        return self.list_display

    def _get_endpoint_list(self, name, check_viewset_if_none=False):
        value = getattr(self, name, None)
        if value is None:
            if check_viewset_if_none:
                value = getattr(self.get_viewset(), name, None)
            if value is None:
                return []
        return value

    def get_filter_fields(self, check_viewset_if_none=True):
        fields = self._get_endpoint_list('filter_fields', check_viewset_if_none)
        return fields

    def get_search_fields(self, check_viewset_if_none=True):
        fields = self._get_endpoint_list('search_fields', check_viewset_if_none)
        return fields

    @property
    def search_enabled(self, check_viewset_if_none=True):
        fields = self.get_search_fields(check_viewset_if_none=True)
        return len(fields) > 0

    def get_ordering_fields(self, check_viewset_if_none=True):
        fields = self._get_endpoint_list('ordering_fields', check_viewset_if_none)
        return fields

    def get_needs(self):
        model_fields = [
            f
            for f in self.model._meta.get_fields()
            if f.is_relation and f.name in self.get_fields_for_serializer() and (
                not isinstance(f, ForeignKey) or
                self.foreign_key_as_list is False or (
                   isinstance(self.foreign_key_as_list, Iterable) and
                   f.name not in self.foreign_key_as_list
                )
            )
        ]
        related_models = [
            f.related_model
            if f.related_model and f.related_model != self.model
            else f.model if f.model and f.model != self.model else None
            for f in model_fields
        ]
        return [
            {
                'app': model._meta.app_label,
                'singular': model._meta.model_name.lower(),
                'plural': self.inflector.pluralize(model._meta.model_name.lower()),
            } for model in related_models if model is not None
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
                    lang = language.replace('-', '_')
                    rv.append('{}_{}'.format(field, lang))
            self._translated_field_names = rv
        return self._translated_field_names

    @property
    def default_language_field_names(self):
        from django.conf import settings as django_settings
        if self._default_language_field_names is None:
            lang = django_settings.LANGUAGE_CODE.replace('-', '_')
            rv = []
            for field in self.get_translated_fields():
                rv.append('{}_{}'.format(field, lang))
            self._default_language_field_names = rv
        return self._default_language_field_names

    def _verb_for_action(self, action):
        if hasattr(action, 'bind_to_methods'):
            # DRF38
            verb = action.bind_to_methods[0]
        else:
            verb = list(action.mapping.keys())[0]
        return verb

    def get_custom_actions(self):
        rv = []
        viewset = self.get_viewset()

        for action_name in dir(viewset):
            try:
                action = getattr(viewset, action_name)
            except AttributeError:
                continue
            if getattr(action, 'action_type', None) == 'custom':
                custom_action = {
                    'url': reverse('{}-{}'.format(self.get_url(), action.__name__.lower().replace('_', '-')),
                                   kwargs={getattr(viewset, 'lookup_field', 'pk'): ':id'}),
                    'verb': self._verb_for_action(action),
                }
                custom_action.update(action.action_kwargs)
                rv.append(custom_action)

        if self.custom_actions is not None:
            rv += self.custom_actions

        return rv

    def get_bulk_actions(self):
        rv = []
        viewset = self.get_viewset()

        for action_name in dir(viewset):
            try:
                action = getattr(viewset, action_name)
            except AttributeError:
                continue
            if getattr(action, 'action_type', None) == 'bulk':
                bulk_action = {
                    'url': reverse('{}-{}'.format(self.get_url(), action.__name__.lower())),
                    'verb': self._verb_for_action(action),
                }
                bulk_action.update(action.action_kwargs)
                rv.append(bulk_action)

        if self.bulk_actions is not None:
            rv += self.bulk_actions

        return rv

    def get_list_actions(self):
        rv = []
        viewset = self.get_viewset()

        for action_name in dir(viewset):
            try:
                action = getattr(viewset, action_name)
            except AttributeError:
                continue
            if getattr(action, 'action_type', None) == 'list':
                list_action = {
                    'url': reverse('{}-{}'.format(self.get_url(), action.__name__.lower())),
                    'verb': self._verb_for_action(action),
                }
                list_action.update(action.action_kwargs)
                rv.append(list_action)

        if self.list_actions is not None:
            rv += self.list_actions

        return rv


class Endpoint(BaseEndpoint, metaclass=EndpointMetaClass):

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
                list(kwargs.keys())[0]
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
            try:
                self.model = self.get_serializer().Meta.model
            except Exception:
                pass
