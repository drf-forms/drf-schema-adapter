from django.utils.module_loading import import_string

from rest_framework.fields import empty
from rest_framework.metadata import SimpleMetadata, BaseMetadata


class AutoMetadataMixin(object):
    def determine_metadata(self, request, view):
        from drf_auto_endpoint.app_settings import settings

        serializer_instance = view.serializer_class()
        form_metadata = []

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

                'ui': {
                    'label': field.title(),
                },

                'validation': {
                    'required': instance_field.required
                }
            }

            default = instance_field.default

            if default and default != empty:
                field_metadata['default'] = default

            if getattr(instance_field, 'choices', None):
                field_metadata['choices'] = [{
                    'label': v,
                    'value': k,
                } for k, v in instance_field.choices.items()]

            if type_ == 'foreignkey':
                field_metadata['endpoint'] = field

            attrs_to_validation = {
                'min_length': 'min',
                'max_length': 'max',
                'min_value': 'min',
                'max_value': 'max'
            }
            for attr_name, validation_name in attrs_to_validation.items():
                if getattr(instance_field, attr_name, None):
                    field_metadata['validation'][validation_name] = getattr(instance_field, attr_name)

            if hasattr(view, 'endpoint'):
                annotation = view.endpoint.fields_annotation
                if annotation and field in annotation and 'placeholder' in annotation[field]:
                    field_metadata['ui']['placeholder'] = annotation[field]['placeholder']

            form_metadata.append(field_metadata)

        adapter = import_string(settings.METADATA_ADAPTER)()
        return adapter(form_metadata)


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutoMetadata(AutoMetadataMixin, BaseMetadata):
    pass
