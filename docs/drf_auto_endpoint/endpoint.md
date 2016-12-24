# The `Endpoint` class

As with Django's `ModelAdmin` class you can also define your own `Endpoint` class and register it
with the router instead of registering a model.
In simple terms, `Endpoint`'s are a wrapper around a DRF ViewSet and Serializer.

```
# my_app/endpoints.py
from drf_auto_endpoint.endpoints import Endpoint
from .models import MyModel

class MyModelEndpoint(Endpoint):

    model = MyModel
    read_only = True
    fields = ('id', 'name', 'category')
```

```
# urls.py
from drf_auto_endpoint.router import router
from my_app.endpoints import MyModelEndpoint

router.register(endpoint=MyModelEndpoint())

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
```

## Attributes

### `model`

The `Model` class the endpoint should represent

### `fields`

*defaults to all fields from the model*

A tuple or list of field that should be present. This is the same attribute as what you would give
to a `ModelSerializer`'s Meta class.

### `include_str`

*default:* `True`

Boolean indicated whether or not `__str__` should be included in the automatically-generated list of fields.

### `read_only`

*default:* `False`

Boolean indicating whether this `Endpoint` should be a read-only `Endpoint` or not.

### `permission_classes`

*default*: `None`

A list or tuple of permission classes to apply to th Endpoint.
Similar to the `permission_classes` attribute you would use on a
[DRF `ViewSet`](http://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy)

### `base_serializer`

*default*: `ModelSerializer`

`Endpoint`'s will automatically generate serializers based on `ModelSerialier`.
You can override this behavior and pass in your own `base_serializer` tha will be used to generate
the serializer associated with the `Endpoint`.

### `serializer`

*default:* `None`

Instead of letting the `Endpoint` automatically generate a serializer you can pass in a serializer class
of your own using the `serializer` attribute


### `base_viewset`

*default:* `ReadOnlyModelViewSet` *(if* `read_only = True` *) or* `ModelViewSet`

`Endpoint`'s will automatically generate viewsets based on `ModelViewSet` or `ReadOnlyModelViewSet`.
You can override this behavior and pass in your own `base_viewset` tha will be used to generate
the viewset associated with the `Endpoint`.

### `viewset`

*default:* `None`

Instead of letting the `Endpoint` automatically generate a viewset you can pass in a viewset class
of your own using the `viewset` attribute.

### `filter_fields`

*default:* `None`

A list or tuple containing a list of fields the `Endpoint` should be able to filter on.
Similar to the `filter_fields` attribute you would pass to a Viewset using a
[`DjangoFilterBackend`](http://www.django-rest-framework.org/api-guide/filtering/#djangofilterbackend)

### `search_fields`

*default:* `None`

A list or tuple containing a list of textual fields the `Endpoint` should be able to search on.
Similar to the `search_fields` attribute you would pass to a Viewset using a
[`SearchFilter` backend](http://www.django-rest-framework.org/api-guide/filtering/#searchfilter)

### `ordering_fields`

*default:* `None`

A list or tuple containing a list of fields the `Endpoint` should be able to sort on.
Similar to the `oredering_fields` attribute you would pass to a Viewset using an
[`OrderingFilter` backend](http://www.django-rest-framework.org/api-guide/filtering/#orderingfilter)

### `page_size`

*default:* `None`

An integer representing the number of records that should be present per result page.
Similiar to the `page_size` attribute you wouls pass to a viewset using
[`PageNumberPagination`](http://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination)

### `fieldsets` :warning: Only used by [metadata](./metadata.md)

*defaults to a single fieldset without title containing the same fields as the `fields` attribute*

A list or tuple containing the list of fieldsets to use. A fieldset has 2 properties,
a `title` and a list of `fields`. Somewhat similar to the
[`fieldsets` attribute of a `ModelAdmin` class](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets)
while more powerfull as you are free to describe any number of levels of nested records here.
