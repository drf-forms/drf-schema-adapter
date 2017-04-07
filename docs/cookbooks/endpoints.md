# Cookbook: creating endpoints from models

## Setup

In this cookbook, we will see how to create enpoints from models without
building any frontend yet.

First let's kickstart our project by installing
[cc_project_app_drf](https://bitbucket.org/levit_scs/cc_project_app_drf)
which will setup a Django project with a virtualenv and Django REST Framework
pre-installed.

To start with this cookiecutter, you will first need to install
[cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) globally on
your computer if you haven't already done so.

`$ sudo pip install cookiecutter`

Once cookiecutter is install you can go forward and bootstrap your new project:

```
$ cookiecutter cc_project_app_drf 
project_name [Project name]: Simple test
repo_name [simple_test]: 
author [Your Name]: Emma
username [emma]: 
email [you@domain.com]: emma@levit.be
python [/usr/bin/python3.5]: 
create_superuser [no]: yes
```

you can now go to the newly created folder (`simple_test` in my case), activate
your virtualenv and launch Django dev server:

```
$ cd simple_test
$ source venv/bin/activate
$ ./manage.py runserver
```

After doing so, if you head to
[http://localhost:8000/api/v1/](http://localhost:8000/api/v1/) you'll see that
we have a running application with basic DRF setup and even already have an
endpoint for users.

Before being able to use DRF-schema-adapter we'll now have to install it. In a
new terminal window, activate your virtualenv and install drf-schema-adpater.

```
source venv/bin/activate
pip install drf-schema-adapter
```

And add `drf_auto_endpoint` to your `INSTALLED_APPS`. 

```
## settings.py

...
INSTALLED_APPS = (
    ...
    'drf_auto_endpoint',
)
```

`drf_auto_endpoint` is one of the 2 packages provided by DRF-schema-adapter and
is responsible for everything that happens on the Django side of things.

Now that DRF-schema-adapter is installed, we can replace DRF's `DefaultRouter`
with `drf_auto_endpoint`'s router in the urls file.
With this cookiecutter, urls that are linked to the API are located in your
project's forlder in a file called `api_urls.py`. In my case that would be
`simple_test/api_urls.py`.

After the substitution, the file should look like this:

```
## simple_test/api_urls.py

from django.conf.urls import include, url
from drf_auto_endpoint.router import router

from .views import UserViewSet

router.registerViewSet(r'users', UserViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
```

## Creating endpoints from models

After doing this, you shouldn't notice any change in the output of DRF. The
only difference is that we are now using `drf_auto_endpoint`'s router which is
a subclass of DRF's `DefaultRouter`.

It is now time to get started. In a virtualenv-activated shell, start a new
application (let's call it catalog).

`$ ./manage.py startapp catalog`

```
## settings.py

INSTALLED_APPS = (
  ...
  'catalog',
)
```

In this application, we will created two models: `Category` and `Product`.

```
## catalog/models.py

from django.db import models


class Category(models.Model):

    name = models.CharField(max_length=100)


class Product(models.Model):

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='products')
    price = models.DecimalField(max_digits=9, decimal_places=3)
```

Don't forget to create and run migrations for our new models.

```
$ ./manage.py makemigrations
$ ./manage.py migrate
```

Now that we have two new models, we are going to create endpoints for them.
Simple model endpoints are straight-forward to create. Models can be directly
registered on the router which will generate a `ModelSerializer` and a
`ModelViewSet` for you. Create new file`catalog/endpoints.py` with the following
content:

```
## catalog/endpoints.py

from drf_auto_endpoint.router import router

from .models import Category, Product


router.register(Category)
router.register(Product)
```

As `endpoints.py` is a new file, you will have to restart your Django dev
server in order to see the changes.
Once this is done and you have reloaded
[http://localhost:8000/api/v1/](http://localhost:8000/api/v1/), you'll notice
that we now have two new endpoints available, one for each of our models.

## Customizing Endpoints

This is great for prototyping but in real life our endpoints are rarely that
simple.
In the case of our application, let's say we want to use this application for an
e-commerce. The frontend application that will connect to our api should not be
allowed to write anything, it should also be able to perform search queries on
products by name, filter queries by category_id and ordering results by name or
price.

In order to achieve this we will have to create an `Endpoint` class. As with
Django admin, instead of registering models directly on the router, you can use
the `@register` decorator to register an (almost) empty Endpoint class on the
router like this:

```
## catalog/endpoints.py

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router, register

from .models import Category, Product


@register
class ProductEndpoint(Endpoint):

    model = Product


router.register(Category)
```

This is the same Endpoint class to which we can pass different parameters in
order to customize it.
For a full list of available parameters/attributes, please see
[the endpoint attributes section](../drf_auto_endpoint/endpoint.md#atrributes).

Let's implement the changes we mentioned above. As you'll notice, most
attributes are similar to attributes you would declare on a DRF `ViewSet`.

```
## catalog/endpoints.py

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register

from .models import Category, Product


@register
class ProductEndpoint(Endpoint):

    model = Product
    read_only = True
    search_fields = ('name', )
    filter_fields = ('category_id', )
    ordering_fields = ('price', 'name', )


@register
class CategoryEndpoint(Endpoint):

    model = Category
    read_only = True
```
