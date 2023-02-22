# DRF-schema-adapter ![Build Status](https://github.com/drf-forms/drf-schema-adapter/actions/workflows/test.yml/badge.svg?branch=master)

`drf-schema-adapter` is a set of tools used to make it as straight-forward to declare an API endpoint
as it is to declare a new `ModelAdmin` in Django and export the corresponding definition to frontend
frameworks and libraries.

## Compatibility Matrix

**DRF-schema-adapter** is compatible with the following matrix

|                 | Py 3.8       | Py 3.9       | Py 3.10      | Py 3.11      |
| --------------- | ------------ | ------------ | ------------ | ------------ |
| **Django 3.2**  | DRF 3.12+    | DRF 3.12+    | N/A          | N/A          |
| **Django 4.0**  | DRF 3.12+    | DRF 3.12+    | DRF 3.12+    | N/A          |
| **Django 4.1**  | DRF 3.12+    | DRF 3.12+    | DRF 3.12+    | DRF 3.12+    |

:warning: For Python 2.7 or Django 1.x support, please use versions 1.x or prior
:warning: For Django Version 3.1 or prior, use version 2.x

:warning: For Python 3.11 compatibility, you will have (for now) to install Inflector directly from the repo:
```bash
pip install git+https://github.com/ixmatus/inflector@ef5c19dc2aa8df5e6b4c452ff2d9b54ec41a04a8#egg=Inflector
```

## Installation

### With pip

```bash
pip install drf-schema-adapter
```

If you are using python 3.11, you will have to also install Inflector directly from the repo, pending the release of Inflector 3.0.2

```bash
pip install git+https://github.com/ixmatus/inflector@ef5c19dc2aa8df5e6b4c452ff2d9b54ec41a04a8#egg=Inflector
```

### From source

Within the source directory:

```bash
python setup.py install
```


## Demo application

You can see a demo application running at
[https://djembersample.pythonanywhere.com/](https://djembersample.pythonanywhere.com/).

## Basic usage

First of all you'll need to import the default EndpointRouter in your urls.py file.

```python
from drf_auto_endpoint.router import router
```

As well as add its urls to your `urlpatterns` in `urls.py`, the same way you would with DRF's
`DefaultRouter`.

```python
urlpatterns = [
    ...
    path("api/", include(router.urls)),
    ...
]
```

### Prototyping

The quickest way to get a working endpoint is to register a model with the router. Register accepts
an optional keyword argument for the `url` associated to that endpoint. By default the url for an
endpoint willbe `app_label/verbose_name_plural`

```python
from django.urls import include, path
from drf_auto_endpoint.router import router
from my_app.models import MyModel, OtherModel

router.register(MyModel)
router.register(OtherModel, url='my_custom_url')

urlpatterns = [
    path("api/", include(router.urls)),
]
```

### Adding schema information to your `OPTIONS` calls

Django REST framework provides the ability to customize those calls thanks to
[metadata classes](http://www.django-rest-framework.org/api-guide/metadata/).

Setup DRF to use one of **DRF-schema-adapter**'s metadata classes to get schema information:

```python
## settings.py

...
REST_FRAMEWORK = {
    'DEFAULT_METADATA_CLASS': 'drf_auto_endpoint.metadata.AutoMetadata',
}
```


### Exporting to the frontend

First add `'export_app'` to your setting's `INSTALLED_APPS`, then run:

```bash
./manage.py export --adapter_name EmberAdapter samples/products
```

## Full documentation

For much more complete documentation, please see: http://drf-schema-adapter.readthedocs.io

## Related projects

- Django:
  - [Django Rest Framework](http://www.django-rest-framework.org/)
  - [DRF-Base64](https://bitbucket.org/levit_scs/drf_base64)
- Ember:
  - [ember-cli-dynamic-model](https://bitbucket.org/levit_scs/ember-cli-dynamic-model)
  - [ember-cli-crudities](https://bitbucket.org/levit_scs/ember-cli-crudities)
- Angular:
  - [angular-formly](http://angular-formly.com/)
- React:
  _nothing so far_
- Third-party adapters:
  _nothing so far_

## Contibuting guide-lines

If you'd like to contibute to *DRF-schema-adapter**, you are more than welcome to do so. In order to
make contributing to this project a rich experience for everyone, please follow these guide-lines:

- First, fork the project with your own GitHub account, build your code on your own repository and
submit a pull-request once your contribution is ready.
- Before contributing a bug-fix or new feature, create an issue explaining what the problem/need is
first. When submitting your pull-request, make sure to reference the original issue.
- For any code you contribute, make sure to follow PEP8 recommendation (soft line-limit 100, hard
limit 120).
- For bug-fixes, please first write a test that will fail with the current code and passes using your
patch. For easier evaluation, please do so in 2 separate commits
- For new features, if your feature can be implemented as a third-party app (like new adapters), please
don't contribute them to this repo, publish your own application and open an issue telling us about it.
We will make sure to add a link to your application in this README.
- Read and respect the [Code Of Conduct](./COC.md)

## ToDo

- [ ] Write better documentation
- [ ] Write more/better tests

---

License information available [here](LICENSE.md).

Contributors code of conduct is available [here](COC.md). Note that this COC **will** be enforced.
