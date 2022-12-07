from collections import OrderedDict

from django.utils.module_loading import import_string

from rest_framework.routers import DefaultRouter

from .endpoints import Endpoint
from .app_settings import settings


class EndpointRouter(DefaultRouter):

    base_endpoint_class = Endpoint

    def __init__(self, *args, **kwargs):
        self._endpoints = OrderedDict()
        self._registry = {}
        super(EndpointRouter, self).__init__(*args, **kwargs)

    def register(self, model=None, endpoint=None, fields=None, permission_classes=None,
                 serializer=None, filterset_fields=None, read_only=False, viewset=None,
                 search_fields=None, ordering_fields=None, page_size=None, base_viewset=None,
                 base_name=None, fields_annotation=None, fielsets=None, base_serializer=None,
                 list_me=True, prefix='', **kwargs):

        if (endpoint is None or isinstance(endpoint, type)):
            extra = {}
            if base_viewset is not None:
                extra['base_viewset'] = base_viewset
            if base_serializer is not None:
                extra['base_serializer'] = base_serializer

            endpoint_kwargs = {
                'model': model,
                'fields': fields,
                'fieldsets': fielsets,
                'permission_classes': permission_classes,
                'serializer': serializer,
                'filterset_fields': filterset_fields,
                'read_only': read_only,
                'viewset': viewset,
                'search_fields': search_fields,
                'ordering_fields': ordering_fields,
                'fields_annotation': fields_annotation,
                'list_me': list_me
            }
            endpoint_kwargs.update(extra)

        if endpoint is None:
            endpoint = self.base_endpoint_class(**endpoint_kwargs)
        elif isinstance(endpoint, type):
            endpoint = endpoint(**endpoint_kwargs)

        url = endpoint.get_url() if 'url' not in kwargs else kwargs.pop('url')
        self._endpoints[url] = endpoint

        if base_name is None:
            base_name = url

        try:
            super(EndpointRouter, self).register(
                url,
                endpoint.get_viewset(),
                basename=prefix + base_name,
                **kwargs
            )
        except TypeError:
            # DRF < 3.10
            super(EndpointRouter, self).register(
                url,
                endpoint.get_viewset(),
                base_name=prefix + base_name,
                **kwargs
            )

    def override_registry_entry(self, endpoint):
        url = endpoint.get_url()
        self._endpoints[url] = endpoint

        new_registry = []
        for (prefix, viewset, base_name) in self.registry:
            if prefix == url:
                new_registry.append((url, endpoint.get_viewset(), base_name))
            else:
                new_registry.append((prefix, viewset, base_name))
        self.registry = new_registry

    def get_endpoint(self, url):
        return self._endpoints[url]

    def registerViewSet(self, *args, **kwargs):
        super(EndpointRouter, self).register(*args, **kwargs)


def register(wrapped=None, **kwargs):
    from drf_auto_endpoint.router import router as default_router

    def _endpoint_wrapper(endpoint_class):
        router = kwargs.pop('router', default_router)
        router.register(endpoint=endpoint_class(), **kwargs)
        return endpoint_class

    if wrapped is not None:
        return _endpoint_wrapper(wrapped)
    return _endpoint_wrapper


router = import_string(settings.ROUTER_CLASS)()
