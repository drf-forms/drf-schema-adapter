from rest_framework.metadata import SimpleMetadata, BaseMetadata


class AutoMetadataMixin:

    def determine_metadata(self, request, view):
        from drf_auto_endpoint.app_settings import settings

        try:
            metadata = super(AutoMetadataMixin, self).determine_metadata(request, view)
        except NotImplementedError:
            metadata = {}

        if not hasattr(view, 'endpoint'):
            serializer_instance = view.serializer_class()
            metadata['fields'] = []
            for field in view.serializer_class.Meta.fields:
                instance_field = serializer_instance.fields[field]
                if field == 'id':
                    continue
                widget = None
                extra = {}
                if getattr(instance_field, 'choices', None) is not None:
                    widget = settings.WIDGET_MAPPING['choice']
                    extra['choices'] = [
                        {
                            'label': v,
                            'value': k,
                        } for k, v in instance_field.choices.items()
                    ]
                metadata['fields'].append({
                    'name': field,
                    'label': field.title(),
                    'widget': widget if widget is not None else \
                        settings.WIDGET_MAPPING[instance_field.__class__.__name__],
                    'extra': extra
                })
            metadata.update({
                'list_display': ['__str__', ],
                'filter_fields': [],
                'search_fields': [],
                'ordering_fields': [],
                'fieldsets': [{'title': None, 'fields': [
                    field
                    for field in view.serializer_class.Meta.fields
                    if field != 'id' and field != '__str__'
                ]}]
            })
            return metadata

        for prop in ['fields', 'list_display', 'filter_fields', 'search_enabled', 'ordering_fields',
                     'needs', 'fieldsets']:
            metadata[prop] = getattr(view.endpoint, 'get_{}'.format(prop))()

        return metadata


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutoMetadata(AutoMetadataMixin, BaseMetadata):
    pass
