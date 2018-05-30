# Creating a custom MetaData adapter

When creating a custom adapter, the first thing you'll want to do is import the base class and tools you will need:

```python
from drf_auto_endpoint.adapters import BaseAdapter, MetaDataInfo, PROPERTY, GETTER
```

By default, the `BaseAdapter` produces a result containing only `fields`.
If you'd like to get more information like actions or languages, you'll have to override the
`metadata_info` property of the adapter.
`metadata_info` is a list of `MetaDataInfo` objects.
A `MetaDataInfo` object takes 3 arguments:

- the name of the property or method (as in get_&lt;name&gt;()) to call on the endpoint
- whether the name refers to a `PROPERTY` or a `GETTER`
- a default value (used to produce metadata on non-model endpoints or viewsets)

Here is a list of existing properties and getters that can be used:

- `'fields', GETTER, []`
- `'fieldsets', GETTER, []`
- `'list_display', GETTER, []`
- `'filter_fields', GETTER, []`
- `'languages', GETTER, []`
- `'ordering_fields', GETTER, []`
- `'needs', GETTER, []`
- `'list_editable', GETTER, []`
- `'sortable_by', GETTER, []`
- `'translated_fields', GETTER, []`
- `'custom_actions', GETTER, []`
- `'bulk_actions', GETTER, []`
- `'save_twice', PROPERTY, False`
- `'search_enabled', PROPERTY, False`

If you need more information, feel free to add properties and getters on your custom `Endpoint`.

Finally, if the output format of the default adapter doesn't suite you,
you will probably want to override the `adapt_field`, `render_root` or `render` method on your custom adapter.

### `adapt_field`

`adapt_field` is a class method that receives a "field-type" dictionary and output a "field-type" dictionary.
`adapt_field` is called on each field by `BaseAdapter.render`.

Example custom implementation:
```
from drf_auto_endpoint.adapters import BaseAdapter


class MyAdapter(BaseAdapter)
    @classmethod
    def adapt_field(cls, field):
        ui = field.pop('ui')
        field['display_name'] = ui['label']
        return field
```
The `render` method receives a raw dictionary as input and is expected to return a raw dictionary as output.


### `render`

`render` is the method used to adapt the default metadata output to your frontend's needs.
`BaseAdapter.render` only return the contend of `'fields'` so you will have to override it if you want
to get metadata_info other than `'fields'`.

Example custom implementation:
```
from drf_auto_endpoint.adapters import BaseAdapter


class MyAdapter(BaseAdapter)
    def render(self, config):
        config['fields'] = super(MyAdapter, self).render(config)
        return config
```

### `render_root`

`render_root` is similar to `render` but is only used to render metadata for the API root

Example custom implementation:
```
from drf_auto_endpoint.adapters import BaseAdapter


class MyAdapter(BaseAdapter)
    def render_root(self, config):
        config = super(MyAdapter, self).render(config)
        config['bogus'] = 'adapted'
        return config
```

### Full sample custom Endpoint and Adapter

```
from random import randint

from django.utils import timezone

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.adapters import BaseAdapter, MetaDataInfo, PROPERTY, GETTER


class CustomEndpoint(Endpoint):

    @property
    def silly_prop(self):
        return 'silly'

    def get_random_array(self):
        rv = []
        for i in range(randint(1, 10)):
            rv.append(randint(1, 100))
        return rv


class CustomAdapter(BaseAdapter):

    metadata_info = [
          MetaDataInfo('fields', GETTER, []),
          MetaDataInfo('list_display', GETTER, []),
          MetaDataInfo('filter_fields', GETTER, []),
          MetaDataInfo('search_enabled', PROPERTY, False),
          MetaDataInfo('silly_prop', PROPERTY, 'Not so silly after all'),
          MetaDataInfo('random_array', GETTER, []),
    ]

    @classmethod
    def adapt_field(cls, field):
        ui = field.pop('ui')
        field['display_name'] = ui['label']
        return field

    def render(self, config):
        config['fields'] = super(MyAdapter, self).render(config)
        config['silly_property'] = config.pop('silly_prop')
        return config

    def render_root(self, config):
        config = super(MyAdapter, self).render(config)
        config['rendered_at'] = timezone.now().strftime('%Y-%M-%d %H:%m:%S')
        return config
```

