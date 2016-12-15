# DRF-schema-adapter

**DRF-schema-adapter**'s goal is to provide a toolset to help you create fully dynamic clients from **[Django](https://www.djangoproject.com/)** and **[Django REST framework](http://www.django-rest-framework.org/)**. Given the right frontend tools it can even help you build a full-fledge admin.

## Compatibility

**DRF-schema-adapter** is compatible with python 2.7, 3.4 and 3.5 as well as Django 1.8+

## Installation

### With pip

`pip install drf_schema_adapter`

### From source

Within the source directory:

`python setup.py install`

## Basic usage

### Auto endpoints

Thanks to `drf_auto_endpoint`, **DRF-schema-adapter** helps you register endpints as easily as registering basic admin classes.

In order to register endpoints, you'll have to import `drf_auto_endpoint`'s router as well as the models you want to register inside your `urls.py`.

```
## urls.py

from drf_auto_endpoint.router import router
from my_app.models import MyModel, OtherModel

router.register(MyModel)
router.register(OtherModel, url='my_custom_url')

urlpatterns = [
    url(r'^api/', include(router.urls)),
]

```

For more information on `drf_auto_endpoint`'s router and how to customize endpoints, see [this section](drf_auto_endpoint/endpoint.md).

### Metadata

**DRF-schema-adapter** also comes with metadata classes and mixins for use with **[Django REST Framework](http://www.django-rest-framework.org/api-guide/metadata/)**. These classes and mixins provide extra informations about the api and its fields whe calling the `OPTIONS` method on an endpoint root.

Although these metadata classes and mixin work best with **DRF-schema-adapter**'s `Enpoint` classes, they are also compatible with regular DRF `ModelViewSet` and `ModelSerializer`.

To enable this extended metadata, you just have to configure it in your `settings.py`

```
## settings.py

...
REST_FRAMEWORK = {
    ...
    'DEFAULT_METADATA_CLASS': 'drf_auto_endpoint.metadata.AutoMetadata',
}
```

For more information about `drf_auto_endpoint`'s metadata and the available adapters, see [this section](drf_auto_endpoint/metadata.md).

### Exporting serializers definition to frontend models

One of the major burdens when writing applications with a backend and a javascript frontend is having to re-define, at least part of, your models/serialiers both on the frontend and backend.

Thanks to **DRF-schema-adapter**'s `export_app`, you can export those definition to your frontend framework, either "on-the-fly" or as concrete files. in order to do that, you'll first have to add `export_app` to your `INSTALLED_APPS` as well as your frontend appalication's root path.

```
## settings.py

INSTALLED_APPS = (
    ...
    'export_app',
)
EXPORTER_FRONT_APPLICATION_PATH = 'front'
```

Then, to export models corresponding to an enpoint you can now run:

`./mange.py export <endpoint_base_url>`

ex: `./manage.py export sample/products`

To export those models on-the-fly, you'll need to specify your frontend application module name instead of its path as well as add a new route to your `urls.py`

```
## settings.py

INSTALLED_APPS = (
    ...
    'exporter_app',
)
EXPORTER_FRONT_APPLICATION_NAME: 'my-app'
```

```
## urls.py
...
from exporter_app import urls as exporter_urls, settings as exporter_settings
...

urlpatterns = [
    ...
    url(r'^models/', include(exporter_urls, namespace=exporter_settings.URL_NAMESPACE)),
]
```

To know more about the configuration of `exporter_app` and the different adapters available, please see [this section](exporter_app/index.md)


---

License information available [here](LICENSE.md).

Contributors code of conduct is available [here](COC.md). Note that this COC **will** be enforced.
