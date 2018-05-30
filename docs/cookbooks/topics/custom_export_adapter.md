# Creating a custom Export adapter

When creating a custom adapter, the firstthing you'll want to do is import the base class.

```python
from export_app.adapters import BaseAdapter
```

## `works_with`

An export adapter can work from the `Serializer`, the `ViewSet` or both. You can
customize that behaviour with the `works_with` property that can one of these 3 values:

- `serializer` (default)
- `viewset`
- `both`

Adapters that need field definition will usually work from the `Serializer` as it holds
all field-related information.
This is common when using a frontend that has at least a partial data layer.

Adapters that need routing information will usually work from the `ViewSet` as it holds
the url and other information like actions.
This is common when using a frontend that cannot map model names to routes.

Of course, sometimes you'll need both types of information, like with the `Angular2Adapter`.
Some adapters also need to work with the `ViewSet` because they will be calling on method
on that `ViewSet` like `BaseMetadataAdapter`, `MetadataAdapter` and `MetadataES6Adapter` that export the content produced by calls to the `OPTIONS` route of the `Endpoint`.

## Field types mapping

When working with a frontend that has at least a partial data layer, you'll probably want
to use some kind of mapping between DRF field types and frontend field types.

There are 2 properties you need to mind in order to do that:

- `DEFAULT_MAPPING` which is the default frontend field type you want to map to.
- `FIELD_TYPE_MAPPING` which is a dictionary. DRF type names are the keys while frontend type names are the values.

## `write_to_file`


