# Using DRF-Schema-Adapter with custom serializers

If you whish to use custom `Serializer`'s instead of the default one created by DRF-Schema-Adapter,
you first have to define one.

**You don't have to create a full `Serializer` with a `Meta` class**, you only need to declare
whatever will differ from the "default `Serializer`" created by DRF-Schema-Adapter.

If you want to use nested `Serializer`'s, you'll probably also want to take advantage of `serializer_factory`.

```python
from drf_auto_endpoint.factories import serializer_factory
from rest_framework import serializers

from .models import Category


class ProductSerializer(serializers.ModelSerializer):

    category = serializer_factory(model=Category, fields=('id', 'name'))()
```

Once you have a `Serializer`, you can import it and pass it as `base_serializer` to the `Endpoint`

```python
...
from .serializers import ProductSerializer
...


@register
class ProductEndpoint(Endpoint):

    ...
    base_serializer = ProductSerializer
```

If you have a "full `Serializer`" instead of a partial one like above, you can by-pass
DRF-Schema-Adapter's alltogether by passing the `Serializer`to the `Endpoint` as
`serializer` instead of `base_serializer`:

```python
...
from .serializers import ProductSerializer
...


@register
class ProductEndpoint(Endpoint):

    ...
    serializer = ProductSerializer
```
