# LevIT's DRF Auto-endpoint

`drf_auto_endpoint` is a library used to make it as straight-forward to declare an API endpoint
as it is to declare a new `ModelAdmin` in Django.

## Installation

So far, `drf_auto_endpoint` is only compatible with python 3.5, Django 1.9 and DRF 3.3.
It probably also works with other version of python 3.3+ and Django 1.8+, it just hasn't been
tested with those yet.

### With pip

`pip install drf_auto_endpoint`

### From source

Within the source directory:

`python setup.py install`

## Usage

First of all you'll need to import the default EndpointRouter in your urls.py file.

`from drf_auto_endpoint.router import router`

As well as add its urls to your `urlpatterns` in `urls.py`, the same way you would with DRF's
`DefaultRouter`.

```
urlpatterns = [
    ...
    url(r'^api/', include(router.urls)),
    ...
]
``` 

### Prototyping

The quickest way to get a working endpoint is to register a model with the router. Register accepts
an optional keyword argument for the `url` associated to that endpoint. By default the url for an
endpoint willbe `app_label/verbose_name_plural`

```
from drf_auto_endpoint.router import router
from my_app.models import MyModel, OtherModel

router.register(MyModel)
router.register(OtherModel, url='my_custom_url')

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
```

#### Options

When registering a Model with the router, you can also pass several keyword arguments:

- `read_only`: Boolean, indicates whether this endpoint should be read_only or not
- `fieldsets`: a tuple containing the list of fieldsets to use. A fieldset has 2 properties,
a `title` and a list of `fields` (by default, every field from the model will be used).
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

### Custom Enpoint's

As with Django's `ModelAdmin` class you can also define your own `Endpoint` class and register it
with the router instead of registering a model.

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

router.register(endpoint=MyModelEndpoint)

urlpatterns = [
    url(r'^api/', include(router.urls)),
]
```

## MetaData

This package also provides an `AutoMetadata` and a `MinimalAutoMetadata` class. Those 
classes can be used in place of the default DRF metadata class.

To use it, change you DRF settings to include

```
REST_FRAMEWORK = {
    'DEFAULT_METADATA_CLASS': 'drf_auto_endpoint.metadata.AutoMetadata',
}
```

Those MetaData classes will provide extra information about the fields provided by the
serializer and hint the client application on how to use and display those fields.

As an example, see the extra output these classes provide for the sample model `Product`.

```
  "fields": [
    {
      "read_only": true,
      "name": "id",
      "label": "Id",
      "widget": "number",
      "extra": {}
    },
    {
      "read_only": false,
      "name": "name",
      "label": "Name",
      "widget": "text",
      "extra": {}
    },
    {
      "read_only": false,
      "name": "category",
      "label": "Category",
      "widget": "foreignkey",
      "extra": {
        "related_model": "sample/category"
      }
    },
    {
      "read_only": false,
      "name": "product_type",
      "label": "Product_Type",
      "widget": "select",
      "extra": {
        "choices": [
          {
            "value": "s",
            "label": "Sellable"
          },
          {
            "value": "r",
            "label": "Rentable"
          }
        ]
      }
    },
    {
      "read_only": true,
      "name": "__str__",
      "label": "Product",
      "widget": "text",
      "extra": {}
    }
  ],
  "list_display": [
    "__str__"
  ],
  "filter_fields": [],
  "search_enabled": false,
  "ordering_fields": [],
  "needs": [
    {
      "singular": "category",
      "app": "sample",
      "plural": "categories"
    }
  ],
  "fieldsets": [
    {
      "title": null,
      "fields": [
        {
          "name": "name"
        },
        {
          "name": "category"
        },
        {
          "name": "product_type"
        }
      ]
    }
  ]
```

## ToDo

- [ ] Python 2.7 compatibility
- [x] Python 3.4 compatibility
- [ ] Django 1.10 compatibility
- [ ] Write better documentation
- [x] Provide a wrapper for `ModelSerializer` and `ModelViewSet`
- [x] Add custom options for filter, search and order
- [ ] Enable admin-like registration mechanism
- [x] Provide a `Metadata` class to provide meta-information (like list_display) on `OPTION` calls
- [x] Add `choices` (only for non-foreign-keys) and `related_model` to the `Metadata` class
- [ ] Add languages information when django-model-translation is installed

---

License information available [here](LICENSE.md).

Contributors code of conduct is available [here](COC.md). Note that this COC **will** be enforced.