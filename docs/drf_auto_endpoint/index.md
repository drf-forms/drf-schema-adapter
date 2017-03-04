# `drf_auto_endpoint`

`drf_auto_endpoint`'s main feature is to provide a router on which you can register `Model`'s directly.
Not unlike `Model`'s directly in **Django** admin.'

Registering a `Model` on the router implicitely creates an [`Endpoint`](./endpoint.md) which in turn uses
factory methods to create a `ModelViewSet` and a `ModelSerializer` corresponding to the registered `Model`.

This is great for prototyping but as your application progresses you'll probably want to customie those endpoints.
Some customization can be done passing parameters directly to the router when registering models.

- `read_only`: boolean, indicates whether this endpoint should be read_only or not
- `fields`: a list of fields that will be available on the endpoint
- `base_serializer`: a base serializer class to use instead of the default (`ModelSerialier`)
- `serializer`: a custom serializer call that will be used to create the endpoint.
- `include_str`: a boolean indicating whether or not `__str__` should be added to the serialier's fields list
- `fieldsets`: a tuple containing the list of fields.
[metadata](./metadata.md).
- `filter_fields`: a tuple containing a list of fields on which the endpoint will accept filtering
- `search_fields`: a tuple containing a list of fields on which the endpoint will accept searching
(text fields only)
- `ordering_fields`: a tuple containing a list of fields on which the endpoint will accept ordering
- `page_size`: the number of records to render at once (automatically activates pagination)
- `permission_classes`: a tuple containing the list of DRF permission classes to use
- `url`: the base url for the viewset
- `viewset`: the viewset class to use instead of the auto-generated one
- `base_viewset`: a base viewset class to use instead of the defaults (`ModelViewSet` or
`ReadOnlyModelViewSet`)
- `fields_annotation`: a dictionary with fieldnames as keys and annotation dictionaries as values
Right now, the only annotation type which are supported are `placeholder` and `help`
- `list_me`: a Boolean value indicating whether or not that endpoint should be listed in the APIRoot's metadata

Now passing too many parameters to the router in your `urls.py` is usually not the best practice and when
your endpoints start getting more complex, we recommend using a [custom `Endpoint` class](./endpoint.md)
