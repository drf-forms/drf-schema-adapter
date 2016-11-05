from django.conf import settings

from factory import fuzzy, SubFactory, Faker, PostGenerationMethodCall, lazy_attribute
from factory.django import DjangoModelFactory

from ..models import Category, Product, HowItWorks


class UserFactory(DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = fuzzy.FuzzyText()
    first_name = fuzzy.FuzzyText()
    last_name = fuzzy.FuzzyText()
    password = PostGenerationMethodCall('set_password', 'changeM3')
    is_active = True
    is_staff = False
    is_superuser = False

    @lazy_attribute
    def email(self):
        return '{}@example.com'.format(self.username)


def get_admin(username=None):
    from django.contrib.auth import get_user_model

    kwargs = {
        'is_superuser': True,
        'is_staff': True
    }

    if username is not None:
        kwargs['username'] = username

    users = get_user_model().objects.filter(**kwargs)
    if users.count() > 0:
        return users[0]

    rv = UserFactory(**kwargs)
    rv.save()

    return rv


class CategoryFactory(DjangoModelFactory):

    class Meta:
        model = Category

    name = fuzzy.FuzzyText(prefix='Category ', length=3)


class ProductFactory(DjangoModelFactory):

    class Meta:
        model = Product

    name = Faker('word')
    category = SubFactory(CategoryFactory)


class HowItWorksFactory(DjangoModelFactory):

    class Meta:
        model = HowItWorks

    name = Faker('word')
