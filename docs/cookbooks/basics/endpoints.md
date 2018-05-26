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

```bash
sudo pip install cookiecutter
```

Once cookiecutter is installed you can go forward and bootstrap your new project:

```bash
$ cookiecutter https://bitbucket.org/levit_scs/cc_project_app_drf.git 
project_name [Project name]: Simple test
repo_name [simple_test]: 
author [Your Name]: Emma
username [emma]: 
email [you@domain.com]: emma@example.com
python [/usr/bin/python3.6]: 
create_superuser [no]: yes
```

you can now go to the newly created folder (`simple_test` in my case), activate
your virtualenv and launch Django dev server:

```bash
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

```bash
source venv/bin/activate
pip install drf-schema-adapter
```

And add `drf_auto_endpoint` to your `INSTALLED_APPS`. 

```pyton
## settings.py

...
INSTALLED_APPS = (
    ...
    'drf_auto_endpoint',
)
```

`drf_auto_endpoint` is one of the 2 modules provided by DRF-schema-adapter and
is responsible for generating endpoints.

Now that DRF-schema-adapter is installed, we can replace DRF's `DefaultRouter`
with `drf_auto_endpoint`'s router in the urls file.
With this cookiecutter, urls that are linked to the API are located in your
project's forlder in a file called `api_urls.py`. In my case that would be
`simple_test/api_urls.py`.

After the substitution, the file should look like this:

```python
## simple_test/api_urls.py

from django.conf.urls import include, path
# from rest_framework import routers
from drf_auto_endpoint.router import router

from .views import UserViewSet

# router = routers.DefaultRouter()

#router.register(r'users', UserViewSet)
router.registerViewSet(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## Creating endpoints from models

After doing this, you shouldn't notice any change in the output of DRF. The
only difference is that we are now using `drf_auto_endpoint`'s router which is
a subclass of DRF's `DefaultRouter`.

It is now time to get started. In a virtualenv-activated shell, start a new
application (let's call it catalog).

```bash
$ ./manage.py startapp catalog
```

```python
## settings.py

INSTALLED_APPS = (
  ...
  'catalog',
)
```

In this application, we will created two models: `Category` and `Product`.

```python
## catalog/models.py

from django.db import models


class Category(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=3)
```

Don't forget to create and run migrations for our new models.

```bash
$ ./manage.py makemigrations
$ ./manage.py migrate
```

Now that we have two new models, we are going to create endpoints for them.
Simple model endpoints are straight-forward to create. Models can be directly
registered on the router which will generate a `ModelSerializer` and a
`ModelViewSet` for you. Create new file`catalog/endpoints.py` with the following
content:

```python
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

At this point, you should probably create a couple categories and products
from the DRF browable interface in order to be able to play with the interface
later on. 

This is great for prototyping but in real life our endpoints are rarely that
simple.
In the case of our application, let's say we want to use this application for an
e-commerce. The frontend application that will connect to our api should not be
allowed to write anything, it should also be able to perform search queries on
products by name, filter queries by category_id and order results by name or
price.

In order to achieve this we will have to create an `Endpoint` class. As with
Django admin, instead of registering models directly on the router, you can use
the `@register` decorator to register any Endpoint class on the router like this:

```python
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

## Customizing Endpoints

Let's implement the changes we mentioned above. As you'll notice, most
attributes are similar to attributes you would declare on a DRF `ViewSet`.

```python
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

## Custom viewset

A common usecase when building an API is to have to slightly customize
`ViewSet`'s. An example of this is when you want the details view to perform a
slightly different operation than the list view like adding `1` to a counter.

Let's do that with our example app.

First we'll add a view counter to our Product model.

```python
## catalog/models.py

...
class Product(models.Model):
    ...
    views = models.PositiveIntegerField(default=0)
```

Then create and run the migrations.

```bash
./manage.py makemigrations
./manage.py migrate
```

You can notice that our new field is already available on the products endpoint
without us having to do anything (after refreshing
[http://localhost:8000/api/v1/catalog/products/](http://localhost:8000/api/v1/catalog/products/)
).

Now let's create a custom ViewSet.

```python
## catalog/endpoints.py

from rest_framework import viewsets

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register

from .models import Category, Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super(ProductViewSet, self).retrieve(request, *args, **kwargs)

@register
class ProductEndpoint(Endpoint):

    model = Product
    read_only = True
    search_fields = ('name', )
    filter_fields = ('category_id', )
    ordering_fields = ('price', 'name', )

    base_viewset = ProductViewSet

...
```

As you might have noticed, we still don't have to specify any `serializer_class`
or `queryset` parameter when creating the ViewSet, those will be added for us
by drf-schema-adapter.

If you have already created some products, go to
[http://localhost:8000/api/v1/catalog/products/1/](http://localhost:8000/api/v1/catalog/products/1/)
and refresh it a few times to see the counter go up. Of course, this is a naive
implementation and a real-world scenario would be slightly more complex.

## Customizing serializers

Now, intead of referencing a product's category by id like it is right now,
let's say we want to embed the category information in the product records.
For this we will need a custom serializer.
Let's build one by only specifying the fields that should be different from the
default serialiazer.

```python
## catalog/endpoints.py

from rest_framework import viewsets, serializers

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import register

from .models import Category, Product


@register
class CategoryEndpoint(Endpoint):

    model = Category
    read_only = True


class ProductViewSet(viewsets.ReadOnlyModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        return super(ProductViewSet, self).retrieve(request, *args, **kwargs)


class SimpleCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
        )


class ProductSerializer(serializers.ModelSerializer):

    category = SimpleCategorySerializer()


@register
class ProductEndpoint(Endpoint):

    model = Product
    read_only = True
    search_fields = ('name', )
    filter_fields = ('category_id', )
    ordering_fields = ('price', 'name', )

    base_viewset = ProductViewSet
    base_serializer = ProductSerializer
```

As you can see, again here, we only had to define whatever was not standard in
our serializer, we didn't have to declare a `Meta` class as drf-schema-adapter
does this for us.

But wait... since we don't have to manually create a full seriliazer for
the `Product` or `Category` endpoints, it is a bit sad to have to create one
(very similar to the one used on the endpoint) for the nested `Category` inside
the `Product` endpoint!

Indeed and we don't *have* to create it manually we can use the same factory
function invoke by `Endpooint` classes in order to create one for us.

```python
## catalog/endpoints.py

from rest_framework import viewsets, serializers

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.factories import serializer_factory
from drf_auto_endpoint.router import register

from .models import Category, Product

...

# class SimpleCategorySerializer(serializers.ModelSerializer):
# 
#     class Meta:
#         model = Category
#         fields = (
#             'id',
#             'name',
#         )


class ProductSerializer(serializers.ModelSerializer):

    category = serializer_factory(model=Category, fields=('id', 'name'))()
```

The call `serializer_factory` function returns a serializer class for the
`Category` model. It is therefore important to remember to instanciate the
value returned from that call (notice the `()` at the end of the call)
