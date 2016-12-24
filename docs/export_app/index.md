# Exporter-app

**DRF-schema-adapters** also allows you to export your endpoint ('s serialier definition) to frontend
frameworks models (Ember.data models, Angular modules, angular-formly json files, Mobx+Axios models and
stores definitions, ...).
This can be done in 2 different ways:

- on-the-fly generation
- on-disk files generation

Before you are able to use any of these features, you'll have to enable `export-app` in your `setting.py`

```
## settings.py

...
INSTALLED_APPS = (
    ...
    'export_app',
)
```

## Configuration

### `EXPORTER_ADAPTER`

*Default:* `export_app.adapters.EmberAdapter``

*Used by*: Dynamic & on-disk generation

If you wish to use another adapter, you'll
have to configure it in your `settings.py` as well:

```
## settings.py

EXPORTER_ADAPTER = 'export_app.adapters.MobxAxiosAdapter'
```

or specify it on the command-line with `--adapter &lt;adapter_name&gt;`.

If you are using one of the provided adapter, you can simply specify them using their classname eg:

`./manage.py export --adapter AngularAdapter sample/categories`

If you are using a third-party adapter, you'll have to specify the full dotted path to the adapapter eg:

`./manage.py export --adapter third_party.very_cool.Adapter sample/categories`

### `EXPORTER_ROUTER_PATH`

*Default:* ``'urls.router'`

*Used by*: Dynamic & on-disk generation


The python path to the router on which you registered your `ViewSet`'s

### `EXPORTER_FRONT_APPLICATION_NAME`

*Default:* `'djember'`

*Used by*: Dynamic generation only


The name of your frontend application or `modulePrefix` (eg: found in `config/environment.js` of an ember app folder)

### `EXPORTER_FRONT_APPLICATION_PATH`

*Default:* `'../front'`

*Used by*: On-disk generation only

### `EXPORTER_APP_BACK_API_BASE`

*Default:* `'/api'`

*Used by* On-disk generation only (AngularAdapter and MobxAxiosAdapter)

Relative path from your Django project base to your frontend application base directory.

### `EXPORTER_FIELD_TYPE_MAPPING`

*Default:* determined by the adapter

*Used by*: Dynamic & on-disk generation

A dictionary mapping DRF field serializer class names to frontend property types. An mapping you declare in this dictionnary will either override the default one or be added to it.

### `EXPORTER_FIELD_DEFAULT_MAPPING`

*Default:* determined by the adapter

*Used by*: Dynamic & on-disk generation

 string repesenting the frontend property type the export should default to when the DRF field serializer in not found in `EXPORTER_FIELD_TYPE_MAPPING`

## Usage

### On-the-fly generation *(currently only available with `EmberAdapter`)*

In order to generate js files on the fly, you'll have import the urls from the project and add them
to your urlpatterns.

```
# urls.py

from export_app import urls as export_urls, settings as export_settings
...

urlpatterns = [
    ...
    url(r'^models/', include(export_urls, namespace=export_settings.URL_NAMESPACE)),
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

`export_app` also provides a management command to generate (ES5, ES6 or ES7 depending on the adapter)
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

Using the `EmberAdapter` will export the definition of the serializer linked to an endpoint to an
Ember.data model definition.

Since you might want to add computed properties or other features to an Ember model, this is done using
3 files:

- `models/base/&lt;app_name&gt;/&ltmodel_name&gt;.js` &lt;- always overwritten
- `models/&lt;app_name&gt;/&lt;model_name&gt;.js` &lt; inherits from the base model, never overwritten
- `tests/unit/models/&lt;app_name&gt;/&lt;model_name&gt;-test.js` &lt; overwritten on confirmation

### `AngularAdapter`

Using the `AngularAdapter` will export an Angular1 resource definition file into
`modules/resources/&lt;application_name&gt;-&lt;model_name&gt;.js`.

### `Angular2Adapter`

*coming soon*

### `MetadataAdapter`

Using this adapter you'll be able to dump the content of the Metadata (`OPTIONS` call) of an endpoint
into your frontend application in a file named `data/&lt;application_name&gt;-&lt;model_name&gt;.json`.

The created output will depend on the adapter you chose for `drf_auto_endpoint` using the
[`DRF_AUTO_METADATA_ADAPTER`](../drf_auto_endpoint/metadata.md#adapters)

### `MobxAxiosAdapter` (for use with React or standalone)

Using the `MobxAxiosAdapter` will export the definition of the serializer linked to an endpoint to a
set of mobx "model" and mobx+axios "store".

Since you might want to ass computed value or other features to a mobx model, this will yield up to 6
different files:

- `config/axios-config.js` &lt;- configuration of the endpoint base and CSRF settings: never overwritten
- `stores/_base.js` &lt;- a base definition of how stores work: never overwritten
- `stores/&lt;app_name&gt;&lt;model_name&gt;` &lt;- specific definition for this store: overwritten on
confirmation
- `models/base/_base.js` &lt;- a base definition of how models work: never overwritten
- `models/base/&lt;app_name&gt;&lt;model_name&gt;` &lt;- a model containing the same list of fields as
the serializer: always overwritten
- `models/&lt;app_name&gt;&lt;model_name&gt;` &lt; a enpty model that inherits from it base counterpart:
never overwritten
