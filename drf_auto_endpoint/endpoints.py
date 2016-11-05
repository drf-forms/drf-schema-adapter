from rest_framework import serializers, viewsets, relations

from inflector import Inflector, English

from .factories import serializer_factory, viewset_factory


def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields()]


class Endpoint:

    base_serializer = serializers.ModelSerializer
    base_viewset = viewsets.ModelViewSet
    base_readonly_viewset = viewsets.ReadOnlyModelViewSet

    model = None
    fields = None
    serializer = None

    fieldsets = None
    list_display = None

    permission_classes = None
    filter_fields = None
    search_fields = None
    ordering_fields = None
    page_size = None
    viewset = None

    read_only = False
    include_str = True

    inflector_language = English

    def __init__(self, model=None, **kwargs):
        self.inflector = Inflector(self.inflector_language)

        if model is not None:
            self.model = model

        arg_names = ('fields', 'serializer', 'permission_classes', 'filter_fields', 'search_fields',
                     'viewset', 'read_only', 'include_str', 'ordering_fields', 'page_size',
                     'base_viewset', 'fields_annotation', )
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
            if self.fieldsets is None:
                self.fields = tuple(get_all_field_names(self.model))
                if self.include_str:
                    self.fields += ('__str__', )
            else:
                self.fields = [
                    field['name'] if isinstance(field, dict) else field
                    for field in self.fieldsets
                ]

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
        from drf_auto_endpoint.app_settings import settings

        serializer_instance = self.get_serializer()()
        name = field['name'] if isinstance(field, dict) else field
        field_instance = serializer_instance.fields[name]
        rv = {
            'name': name,
            'label': name.title().replace('_', ' ') if name != '__str__' else \
                serializer_instance.Meta.model.__name__,
            'widget': settings.WIDGET_MAPPING[field_instance.__class__.__name__],
            'read_only': field_instance.read_only or name == '__str__',
            'extra': {},
        }

        if getattr(field_instance, 'choices', None) is not None:
            if isinstance(field_instance, (relations.PrimaryKeyRelatedField, relations.ManyRelatedField)):
                model_field = self.model._meta.get_field(field_instance.source)
                related_model = model_field.related_model
                rv['extra']['related_model'] = '{}/{}'.format(
                    related_model._meta.app_label,
                    related_model._meta.model_name.lower()
                )
            else:
                rv['widget'] = settings.WIDGET_MAPPING['choice']
                rv['extra']['choices'] = [
                    {
                        'label': v,
                        'value': k,
                    } for k, v in field_instance.choices.items()
                ]

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
                    'name': field
                }
                for field in self.get_fields_for_serializer()
                if field != 'id' and field != '__str__' ]
            }
        ]

    def get_list_display(self):
        if self.list_display is None:
            if '__str__' in self.get_fields_for_serializer():
                return ['__str__', ]
            return [self.get_fields()[0]['name']]
        return self.list_display

    def _get_endpoint_list(self, name):
        value = getattr(self, name, None)
        if value is None:
            return []
        return value

    def get_filter_fields(self):
        fields = self._get_endpoint_list('filter_fields')
        return fields

    def get_search_enabled(self):
        fields = self._get_endpoint_list('search_fields')
        if len(fields) > 0:
            return True
        return False

    def get_ordering_fields(self):
        fields = self._get_endpoint_list('ordering_fields')
        return fields

    def get_needs(self):
        related_models = [
            f.model
            if f.model and f.model != self.model
            else f.related_model if f.related_model else None
            for f in self.model._meta.get_fields()
            if ((f.one_to_many or f.one_to_one) and f.auto_created) or (f.many_to_one and f.related_model)
        ]
        return [
            {
                'app': model._meta.app_label,
                'singular': model._meta.model_name.lower(),
                'plural': self.inflector.pluralize(model._meta.model_name.lower()),
            } for model in related_models
        ]

