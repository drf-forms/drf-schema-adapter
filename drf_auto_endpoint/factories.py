from rest_framework import filters, pagination, serializers
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.reverse_related import ManyToOneRel


def serializer_factory(endpoint):

    from .app_settings import settings

    meta_attrs = {
        'model': endpoint.model,
        'fields': endpoint.get_fields_for_serializer()
    }
    meta_parents = (object, )
    if hasattr(endpoint.base_serializer, 'Meta'):
        meta_parents = (endpoint.base_serializer.Meta, ) + meta_parents

    Meta = type('Meta', meta_parents, meta_attrs)

    cls_name = '{}Serializer'.format(endpoint.model.__name__)
    cls_attrs = {
        'Meta': Meta,
    }

    for meta_field in meta_attrs['fields']:
        try:
            model_field = endpoint.model._meta.get_field(meta_field)
            if isinstance(model_field, ManyToOneRel):
                cls_attrs[meta_field] = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
        except FieldDoesNotExist:
            #  This is not a field, it's a property
            pass

    return type(cls_name, (endpoint.base_serializer, ), cls_attrs)


def viewset_factory(endpoint):

    base_viewset = endpoint.get_base_viewset()

    cls_name = '{}ViewSet'.format(endpoint.model.__name__)
    tmp_cls_attrs = {
        'serializer_class': endpoint.get_serializer(),
        'queryset': endpoint.model.objects.all(),
        'endpoint': endpoint,
        '__doc__': base_viewset.__doc__
    }

    cls_attrs = {
        key: value
        for key, value in tmp_cls_attrs.items() if key == '__doc__' or
        getattr(base_viewset, key, None) is None
    }

    if endpoint.permission_classes is not None:
        cls_attrs['permission_classes'] = endpoint.permission_classes

    filter_backends = getattr(endpoint.get_base_viewset(), 'filter_backends', ())
    if filter_backends is None:
        filter_backends = []
    else:
        filter_backends = list(filter_backends)

    for filter_type, backend in (
        ('filter_fields', filters.DjangoFilterBackend),
        ('search_fields', filters.SearchFilter),
        ('ordering_fields', filters.OrderingFilter),
    ):

        if getattr(endpoint, filter_type, None) is not None:
            filter_backends.append(backend)
            cls_attrs[filter_type] = getattr(endpoint, filter_type)

    if len(filter_backends) > 0:
        cls_attrs['filter_backends'] = filter_backends

    if endpoint.page_size is not None:
        cls_attrs['page_size'] = endpoint.page_size
        cls_attrs['pagination_class'] = pagination.PageNumberPagination

    return type(cls_name, (endpoint.get_base_viewset(),), cls_attrs)
