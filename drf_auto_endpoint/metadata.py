from collections import defaultdict

from django.utils.module_loading import import_string

from rest_framework.metadata import SimpleMetadata, BaseMetadata

from .utils import get_languages, get_field_dict
from .app_settings import settings
from .adapters import GETTER


class AutoMetadataMixin(object):

    def root_metadata(self, metadata, view):
        from .router import router
        rv = {
            'endpoints': [k for k in router._endpoints.keys()]
        }

        applications = defaultdict(lambda: [])
        for url, endpoint in router._endpoints.items():
            if endpoint.list_me:
                applications[endpoint.application_name].append({
                    'name': endpoint.model_name,
                    'singular': endpoint.singular_model_name,
                    'endpoint': url
                })
        rv['applications'] = [
            {
                'name': k,
                'models': v
            } for k, v in applications.items()

        ]
        rv['languages'] = get_languages()

        adapter = import_string(settings.METADATA_ADAPTER)()
        metadata.update(adapter.render_root(rv))
        return metadata

    def get_field_dict(self, *args, **kwargs):
        return get_field_dict(*args, **kwargs)

    def determine_metadata(self, request, view):

        try:
             metadata = super(AutoMetadataMixin, self).determine_metadata(request, view)
        except NotImplementedError:
            metadata = {}
        except AttributeError:
            metadata = {}

        root_view_names = ['APIRootView', 'APIRoot']
        if view.__class__.__name__ in root_view_names or view in root_view_names:
            return self.root_metadata(metadata, view)

        serializer = view.get_serializer_class()

        try:
            serializer_instance = view.get_serializer()
        except Exception:
            # Custom viewset is expecting something we can't guess
            serializer_instance = serializer()
        endpoint = None
        if hasattr(view, 'endpoint'):
            endpoint = view.endpoint
        else:
            if hasattr(serializer.Meta, 'model'):
                from .endpoints import Endpoint
                endpoint = Endpoint(serializer.Meta.model, viewset=view)

        adapter = import_string(settings.METADATA_ADAPTER)()
        if endpoint is None:
            fields_metadata = []

            for field in serializer_instance.fields.keys():
                if field in {'id', '__str__'}:
                    continue

                instance_field = serializer_instance.fields[field]
                type_ = settings.WIDGET_MAPPING.get(instance_field.__class__.__name__)

                if type_ is None:
                    raise NotImplementedError()

                field_metadata = self.get_field_dict(field, serializer)

                fields_metadata.append(field_metadata)

                for meta_info in adapter.metadata_info:
                    if meta_info.attr == 'fields':
                        metadata['fields'] = fields_metadata,
                    elif meta_info.attr == 'fieldsets':
                        metadata['fieldsets'] = [{
                            'title': None,
                            'fields': [
                                {'key': field}
                                for field in serializer_instance.fields.keys()
                                if field != 'id' and field != '__str__'
                            ]
                        }]
                    else:
                        metadata[meta_info.attr] = meta_info.default
        else:
            for meta_info in adapter.metadata_info:
                try:
                    if meta_info.attr_type == GETTER:
                        method = getattr(endpoint, 'get_{}'.format(meta_info.attr))
                        try:
                            metadata[meta_info.attr] = method(request)
                        except TypeError:
                            metadata[meta_info.attr] = method()
                    else:
                        metadata[meta_info.attr] = getattr(endpoint, meta_info.attr, meta_info.default)
                except AttributeError:
                    metadata[meta_info.attr] = meta_info.default

        return adapter(metadata)


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutoMetadata(AutoMetadataMixin, BaseMetadata):
    pass


class RootViewMetadata(SimpleMetadata):
    pass
