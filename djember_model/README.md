# Djember Model

This project is aimed at automatically generating EmberJS models from Django REST Framework serializer definitions.
This can be done in 2 different ways:

- on-the-fly generation
- on-disk files generation

## installation

Install using pip:

```
pip install djember_model
```

Add djember_model to your `INSTALLED_APPS`:

```
# settings.py

INSTALLED_APPS = (
    ...
    djember_model,
)
```

## Usage

### On-the-fly generation

In order to generate js files on the fly, you'll have import the urls from the project add add them to your urlpatterns.

```
# urls.py

from djember_model import urls as djember_urls, settings as djember_settings
...

urlpatterns = [
    ...
    url(r'^models/', include(djember_urls, namespace=djember_settings.URL_NAMESPACE)),
]
```

For each `ViewSet` (Ember expects the same endpoint for CRUD operations, so it's better to use `ViewSet`'s) registered on your router, this will provide a corresponding ember js model.

If you have registered the following Viewset:
```router.register('categories', CategoryViewSet)```

The corresponding (ES5) Ember model definition will now be available at http://localhost:8000/models/categories.js

This functionality is meant to be used with [ember-cli-dynamic-model](https://bitbucket.org/levit_scs/ember-cli-dynamic-model) and the recommended usage is to register all your `ViewSet`'s using the &lt;app_name&gt;&lt;model_name_correct_english_plural&gt; as in `my_app/categories`.

### On-disk files generation

`djember_model` also provides a management command to generate (ES6) Ember models on disk:

```./manage.py export_to_ember route_registered_with_the_router```

So assuming you have registered the following ViewSet:

```router.register('sample/categories', CategoryViewSet)```

you can run:

```./manage.py export_to_ember sample/categories```

in order to generate the corresponding model.
This command will generate 3 files in you ember app:

- `app/models/sample/base/category.py` <- always generated
- `app/models/sample/category.py` <- only generate the file if it doen't exist yet
- `tests/unit/models/sample/category-test.py` <- always generated

The fields or attributes definition will be generated in `app/models/sample/base/category.py`; `app/models/sample/category.py` inherits from the first file and is the place where you should add any customization to your Ember model.

## Configuration

`djember_model` comes with a series of settings that can (should) be customized:

### `DJEMBER_ROUTER_PATH`

*Default value*: ``'urls.router'`

*Used by*: Dynamic & on-disk generation


The python path to the router on which you registered your `ViewSet`'s

### `DJEMBER_EMBER_APPLICATION_NAME`

*Default value*: `'djember'`

*Used by*: Dynamic generation only


The name of your ember application or `modulePrefix` (found in `config/environment.js` in your ember app folder)

### `DJEMBER_EMBER_APPLICATION_PATH`

*Default value*: `'../front'`

*Used by*: On-disk generation only


Relative path from your Django project base to your Ember application base

### `DJEMBER_FIELD_TYPE_MAPPING`

*Default value*: 
```
{
    'BooleanField': 'boolean',
    'NullBooleanField': 'boolean',
    'IntegerField': 'number',
    'FloatField': 'number',
    'DecimalField': 'number',
    'ListField': None,
    'DictField': None,
    'JSONField': None,
}
```

*Used by*: Dynamy & on-disk generation


Mapping from Django Model fields to ember-data attr types. Any missing mapping will be mapped as `string`. If you are using custom transforms in Ember, you probably want to update these mappings.


---

License information available [here](LICENSE.md).

Contributors code of conduct is available [here](COC.md). Note that this COC **will** be enforced.
