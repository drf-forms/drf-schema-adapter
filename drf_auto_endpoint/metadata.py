from collections import defaultdict

from django.utils.module_loading import import_string

from rest_framework.fields import empty
from rest_framework.metadata import SimpleMetadata, BaseMetadata

from .utils import get_validation_attrs


class AutoMetadataMixin(object):

    def root_metadata(self, metadata, view):
        from .router import router
        rv = {
            'endpoints': [k for k in router._endpoints.keys()]
        }

        applications = defaultdict(lambda: [])
        for url, endpoint in router._endpoints.items():
            applications[endpoint.application_name].append({
                'name': endpoint.model_name,
                'endpoint': url
            })
        rv['applications'] = [
            {
                'name': k,
                'models': v
            } for k, v in applications.items()

        ]

        metadata.update(rv)
        return metadata

    def determine_metadata(self, request, view):
        from drf_auto_endpoint.app_settings import settings

        try:
             metadata = super(AutoMetadataMixin, self).determine_metadata(request, view)
        except NotImplementedError:
            metadata = {}
        except AttributeError:
            metadata = {}

        if view.__class__.__name__ == 'APIRootView':
            return self.root_metadata(metadata, view)


        serializer_instance = view.serializer_class()
        if not hasattr(view, 'endpoint'):
            fields_metadata = []

            for field in view.serializer_class.Meta.fields:
                if field in {'id', '__str__'}:
                    continue

                instance_field = serializer_instance.fields[field]
                type_ = settings.WIDGET_MAPPING.get(instance_field.__class__.__name__)

                if type_ is None:
                    raise NotImplementedError()

                field_metadata = {
                    'key': field,
                    'type': type_,
                    'read_only': False,
                    'ui': {
                        'label': field.title(),
                    },

                    'validation': {
                        'required': instance_field.required,
                    },
                    'extra': {}
                }

                default = instance_field.default

                if default and default != empty:
                    field_metadata['default'] = default

                if getattr(instance_field, 'choices', None):
                    field_metadata['choices'] = [{
                        'label': v,
                        'value': k,
                    } for k, v in instance_field.choices.items()]

                field_metadata['validation'].update(get_validation_attrs(instance_field))

                if type_ == 'foreignkey':
                    field_metadata['related_endpoint'] = field

                fields_metadata.append(field_metadata)
                metadata.update({
                    'list_display': ['__str__', ],
                    'filter_fields': [],
                    'search_fields': [],
                    'ordering_fields': [],
                    'fields': fields_metadata,
                    'fieldsets': [{'title': None, 'fields': [
                        field
                        for field in view.serializer_class.Meta.fields
                        if field != 'id' and field != '__str__'
                    ]}]
                })
        else:
            for prop in ['fields', 'list_display', 'filter_fields', 'search_enabled', 'ordering_fields',
                         'needs', 'fieldsets']:
                metadata[prop] = getattr(view.endpoint, 'get_{}'.format(prop))()

        adapter = import_string(settings.METADATA_ADAPTER)()
        return adapter(metadata)


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutoMetadata(AutoMetadataMixin, BaseMetadata):
    pass

class RootViewMetadata(SimpleMetadata):
    pass
