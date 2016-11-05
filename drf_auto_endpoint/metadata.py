from rest_framework.fields import empty
from rest_framework.metadata import SimpleMetadata, BaseMetadata


class AutoMetadataMixin:
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
                }
            }

            default = instance_field.default

            if default and default != empty:
                field_metadata['default'] = default

            if type_ == 'select':
                field_metadata['choices'] = [{
                    'label': v,
                    'value': k,
                } for k, v in instance_field.choices.items()]

            elif type == 'foreignkey':
                field_metadata['endpoint'] = field

            form_metadata.append(field_metadata)

        return form_metadata


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutoMetadata(AutoMetadataMixin, BaseMetadata):
    pass
