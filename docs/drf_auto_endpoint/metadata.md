# The metadata classes and mixin

When building a frontend-framework-based or mobile application,
usually the models you define on the frontend or the data you receive
from your DRF backend isn't enough to be able to create forms or lists.
This is where the metadata classes and mixin proided by **DRF-schema-adapters**
comes to the rescue by providing extra information when calling the `OPTIONS`
method on an endpoint's root.

**DRF-schema-adapters** provides 2 metadata classes `AutoMetadata` (which inherits
from [DRF's `SimpleMetadata` class](http://www.django-rest-framework.org/api-guide/metadata/))
and `MinimalAutoMetadata` (which inherits from DRF's BaseMetadata class).
Both of those classes use the `AutoMetadataMixin` class that you can also apply to your own metadata
classes.

To use the metadata feature of **DRF-schema-adapters**, you'll first have to change DRF's default
settings:

```
## settings.py

...
REST_FRAMEWORK = {
    'DEFAULT_METADATA_CLASS': 'drf_auto_endpoint.metadata.AutoMetadata',
}
```

Any of the two provided metadata classes (or your own metadata class using `AutoMetadataMixin`)
will provide an output similar to this when calling `OPTIONS` on an endpoint:

```
[
    {
        "validation": {
            "required": false
        },
        "read_only": true,
        "type": "number",
        "extra": {},
        "key": "id",
        "ui": {
            "label": "Id"
        }
    },
    {
        "validation": {
            "required": true,
            "max": 255
        },
        "read_only": false,
        "type": "text",
        "extra": {},
        "key": "name",
        "ui": {
            "label": "Name",
            "placeholder": "Enter your name here"
        }
    },
    {
        "validation": {
            "required": true
        },
        "related_endpoint": "sample/category",
        "read_only": false,
        "type": "foreignkey",
        "extra": {},
        "key": "category",
        "ui": {
            "label": "Category"
        }
    },
    {
        "validation": {
            "required": false
        },
        "read_only": false,
        "type": "select",
        "extra": {},
        "choices": [
            {
                "label": "Sellable",
                "value": "s"
            },
            {
                "label": "Rentable",
                "value": "r"
            }
        ],
        "key": "product_type",
        "ui": {
            "label": "Product Type"
        }
    },
    {
        "validation": {
            "required": false
        },
        "read_only": true,
        "type": "text",
        "extra": {},
        "key": "__str__",
        "ui": {
            "label": "Product"
        }
    }
]
```

Any of the two provided metadata classes will provide an output similar this when calling `OPTIONS` on the root of the api.

```
{
    "endpoints": [
        "crm/companies",
        "crm/contacts",
        "crm/contactmechanisms",
        "products/categories",
        "products/products",
        "accounting/invoices",
        "accounting/invoicelines"
    ],
    "applications": [
        {
            "models": [
                {
                    "singular": "invoice",
                    "endpoint": "accounting/invoices",
                    "name": "invoices"
                }
            ],
            "name": "accounting"
        },
        {
            "models": [
                {
                    "singular": "category",
                    "endpoint": "products/categories",
                    "name": "categories"
                },
                {
                    "singular": "product",
                    "endpoint": "products/products",
                    "name": "products"
                }
            ],
            "name": "products"
        },
        {
            "models": [
                {
                    "singular": "company",
                    "endpoint": "crm/companies",
                    "name": "companies"
                },
                {
                    "singular": "contact",
                    "endpoint": "crm/contacts",
                    "name": "contacts"
                }
            ],
            "name": "crm"
        }
    ]
}
```

The exact output depends on the `Adapter` you choose to use. Currently **DRF-schama-adapters** supports
3 different adapters.

## Adapters

### `BaseAdapter`

The `BaseAdapter` produces an output usuable with [JSON Schema](http://json-schema.org/).
This is the default adapter.

`BaseAdapter` will produce an output similar to the one above.

### `AngularFormlyAdapter`

The `AngularFormlyAdapter` is destined to be used with [angular-formly](http://angular-formly.com/).
To use this adapter, you'll have to enable it in your settings first.

```
## settings.py

...
DRF_AUTO_METADATA_ADAPTER = 'drf_auto_endpoint.adapters.AngularFormlyAdapter'
```

This adapter will have a slightly different output:

```
[
    {
        "key": "id",
        "type": "input",
        "templateOptions": {
            "type": "number",
            "required": false,
            "label": "Id"
        },
        "read_only": true
    },
    {
        "key": "name",
        "type": "input",
        "templateOptions": {
            "label": "Name",
            "type": "text",
            "placeholder": "Enter your name here",
            "required": true,
            "max": 255
        },
        "read_only": false
    },
    {
        "key": "category",
        "type": "input",
        "templateOptions": {
            "type": "foreignkey",
            "required": true,
            "label": "Category"
        },
        "read_only": false
    },
    {
        "key": "product_type",
        "type": "select",
        "templateOptions": {
            "type": "select",
            "required": false,
            "label": "Product Type"
        },
        "read_only": false
    },
    {
        "key": "__str__",
        "type": "input",
        "templateOptions": {
            "type": "text",
            "required": false,
            "label": "Product"
        },
        "read_only": true
    }
]
```

### EmberAdapter

The `EmberAdapter` was built to use with
[ember-cli-crudities](https://bitbucket.org/levit_scs/ember-cli-dynamic-model)
and
[ember-cli-dynamic-model](https://bitbucket.org/levit_scs/ember-cli-dynamic-model).

To use the `EmberAdapter` you'll also have to enable it in your settings.

```
## settings.py

...
DRF_AUTO_METADATA_ADAPTER = 'drf_auto_endpoint.adapters.EmberAdapter'
```


It's output is somewhat fuller as it is intended to render a full "admin-like" application and
not just single forms; it looks like this.

```
{
  "fields": [
  {
            "extra": {},
            "readonly": true,
            "required": false,
            "name": "id",
            "widget": "number",
            "translated": false,
            "label": "Id"
        
  },
  {
    "extra": {
                "placeholder": "Enter your name here"
            
    },
            "readonly": false,
            "required": true,
            "name": "name",
            "widget": "text",
            "translated": false,
            "label": "Name"
        
  },
  {
    "extra": {
                "related_model": "sample/category"
            
    },
            "readonly": false,
            "required": true,
            "name": "category",
            "widget": "foreignkey",
            "translated": false,
            "label": "Category"
        
  },
  {
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
            
    },
            "readonly": false,
            "required": false,
            "name": "product_type",
            "widget": "select",
            "translated": false,
            "label": "Product Type"
        
  },
  {
            "extra": {},
            "readonly": true,
            "required": false,
            "name": "__str__",
            "widget": "text",
            "translated": false,
            "label": "Product"
        
  }
    
  ],
  "list_display": [
        "__str__"
    
  ],
    "filter_fields": [],
    "search_enabled": false,
    "languages": [],
    "ordering_fields": [],
    "needs": [
    {
            "app": "sample",
            "singular": "category",
            "plural": "categories"
        
    }
    
    ],
    "fieldsets": [
    {
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
            
      ],
            "title": null
        
    }
    
    ],
    "list_editable": [],
    "sortable_by": null,
    "translated_fields": []
}
```
