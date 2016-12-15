# Exporter-app

**DRF-schema-adapters** also allows you to export your endpoint ('s serialier definition) to frontend
frameworks model (Ember.data models, Angular modules, angular-formly json files, Mobx definitions, ...).
This can be done in 2 different ways:

- on-the-fly generation
- on-disk files generation

Before you are able to use any of these features, you'll have to enable `exporter-app` in your `setting.py`

```
## settings.py

...
INSTALLED_APPS = (
    ...
    'exporter_app',
)
```

## Configuration

The default adapter is `export_app.adapters.EmberAdapter`, if you wish to use another adapter, you'll
have to configure it in your `settings.py` as well:

```
## settings.py

EXPORTER_ADAPTER = 'export_app.adapters.MobXAdapter'
```

or specify it on the command-line with `--adapter &lt;adapter_name&gt;`.

If you are using one of the provided adapter, you can simply specify them using their classname eg:

`./manage.py export --adapter AngularAdapter sample/categories`

If you are using a third-party adapter, you'll have to specify the full dotted path to the adapapter eg:

`./manage.py export --adapter third_party.very_cool.Adapter sample/categories`

## Usage

### On-the-fly generation *(currently only available with `EmberAdapter`)*

In order to generate js files on the fly, you'll have import the urls from the project and add them
to your urlpatterns.

```
# urls.py

from exporter_app import urls as exporter_urls, settings as exporter_settings
...

urlpatterns = [
    ...
    url(r'^models/', include(exporter_urls, namespace=exporter_settings.URL_NAMESPACE)),
]
```

For each `ViewSet` (Ember expects the same endpoint for CRUD operations, so it's better to use
`ViewSet`'s) or `Endpoint` registered on your router, this url setting will provide a corresponding
ember js model.

If you have registered the following Viewset:
```router.register('categories', CategoryViewSet)```

The corresponding (ES5) Ember model definition will now be available at
http://localhost:8000/models/categories.js

This functionality is meant to be used with
[ember-cli-dynamic-model](https://bitbucket.org/levit_scs/ember-cli-dynamic-model) and
the recommended usage is to register all your `ViewSet`'s or `Endpoint`'s using the
 &lt;app_name&gt;/&lt;model_name_correct_english_plural&gt; as in `my_app/categories`.
(This is automatically done for you if you are using `drf_auto_endpoint`'s router registration
capabilities with `Model`'s or `Endpoint`'s)

### On-disk files generation

`exporter_app` also provides a management command to generate (ES5 or ES6 depending on the adapter)
models on disk:

```./manage.py export route_registered_with_the_router```

So assuming you have registered the following ViewSet:

```router.register('sample/categories', CategoryViewSet)```

you can run:

```./manage.py export sample/categories```

in order to generate the corresponding model.
This command will generate on or more files (once again depending on the chosen adapter)
in you frontend application.

## Adapters

### `EmberAdapter`

### `AngularAdapter`

*coming soon*

### `FormlyAdapter`

*coming soon*

### `MobXAdapter`

*coming soon*
