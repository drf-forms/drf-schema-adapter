# Using DRF-Schema-Adapter with custom `ViewSet`'s

If you need to work with custom `ViewSet`'s, use can define one that will inherit from any of the
default `ModelViewSet` defined by DRF.
Unlike with "plain" DRF, you only have to define whever is not "standard" with your `ViewSet`.
**No need to define a serializer_class or a queryset**, DRF-Schema-Adapter will take care of those.


```python
# views.py

from rest_framework import viewsets

from .models import Category, Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super(ProductViewSet, self).retrieve(request, *args, **kwargs)
```

Once you have defined your partial `ViewSet`, you have to import it in `endpoints.py` and add it to
the endpoint as `base_viewset`

```python
# endpoints.py

...
from .views import ProductViewSet
...


@register
class ProductEndpoint(Endpoint):

    ...
    base_viewset = ProductViewSet
```

If you have a "full" `ViewSet` you want to use and so whish to totally disable DRF-Schema-Adapter's
`ViewSet` generation behaviour, you can pass a `viewset`to your `Endpoint` instead of a `base_viewset`.

```python
# endpoints.py

...
from .views import ProductViewSet
...


@register
class ProductEndpoint(Endpoint):

    ...
    viewset = ProductViewSet
```
