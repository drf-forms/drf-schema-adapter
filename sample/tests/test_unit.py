from django.test import TestCase, override_settings

from rest_framework.permissions import AllowAny
from rest_framework import filters, pagination
from rest_framework.serializers import CharField, IntegerField
from rest_framework.viewsets import ModelViewSet

from ..models import Product, Category, PRODUCT_TYPES

from .data import DummyProductSerializer, DummyProductViewSet, DummyProductSerializerWithField

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router
from drf_auto_endpoint import utils
from drf_auto_endpoint.app_settings import settings


class EndpointTestCase(TestCase):

    def setUp(self):
        self.endpoint = Endpoint(model=Product)
        self.fields = tuple([field.name for field in Product._meta.get_fields()])

        self.permission_classes = (AllowAny, )
        self.filter_fields = ('name', 'category_id')
        self.search_fields = ('id', 'name')
        self.ordering_fields = ('name', )
        self.page_size = 2

        self.alternate_endpoint = Endpoint(model=Product, permission_classes=self.permission_classes,
                                           filter_fields=self.filter_fields,
                                           search_fields=self.search_fields,
                                           ordering_fields=self.ordering_fields,
                                           page_size=self.page_size)

    def test_fields(self):
        self.assertEqual(len(self.endpoint.get_fields_for_serializer()), len(self.fields) + 1)
        fields_for_serializer = self.endpoint.get_fields_for_serializer()
        for field in self.fields:
            self.assertIn(field, fields_for_serializer)
        self.assertIn('__str__', fields_for_serializer)

        endpoint = Endpoint(model=Product, include_str=False)
        self.assertEqual(len(endpoint.get_fields_for_serializer()), len(self.fields))
        for field in self.fields:
            self.assertIn(field, endpoint.get_fields_for_serializer())
        self.assertNotIn('__str__', endpoint.get_fields_for_serializer())

        endpoint = Endpoint(model=Product, fields=('id', 'name'))
        self.assertEqual(len(endpoint.get_fields_for_serializer()), 2)
        for field in ('id', 'name'):
            self.assertIn(field, endpoint.get_fields_for_serializer())

    def test_widgets(self):

        data = {
            'name': 'text',
            'category': 'foreignkey',
            'product_type': 'select',
        }

        for field, expected_widget in data.items():
            field_dict = self.endpoint._get_field_dict(field)
            self.assertIn('type', field_dict)
            self.assertEqual(field_dict['type'], expected_widget)
            self.assertIn('extra', field_dict)
            if field == 'category':
                self.assertIn('related_endpoint', field_dict)
                self.assertEqual(field_dict['related_endpoint'], 'sample/category')
                self.assertNotIn('choices', field_dict)
            elif field == 'product_type':
                self.assertIn('choices', field_dict)
                self.assertEqual(len(field_dict['choices']), len(PRODUCT_TYPES))

    def test_model(self):
        self.assertEqual(self.endpoint.model, Product)

    def test_dynamic_params(self):
        endpoint = self.alternate_endpoint

        for attr in ('permission_classes', 'filter_fields', 'search_fields', 'ordering_fields',
                     'page_size'):
            self.assertEqual(getattr(endpoint, attr), getattr(self, attr))

    def test_serializer_factory(self):
        serializer = self.endpoint.get_serializer()
        self.assertEqual(serializer.Meta.model, Product)
        self.assertEqual(len(serializer.Meta.fields), len(self.endpoint.get_fields_for_serializer()))
        for field in self.fields:
            self.assertIn(field, serializer.Meta.fields)

        self.assertEqual(serializer.__name__, 'ProductSerializer')

    def test_factory_serializer_dont_override_fields(self):
        endpoint = Endpoint(model=Product, base_serializer=DummyProductSerializerWithField, fields=('id', 'name'))
        serializer = endpoint.get_serializer()
        self.assertTrue(serializer._declared_fields['name'].read_only)

    def test_non_factory_serializer(self):
        endpoint = Endpoint(model=Product, serializer=DummyProductSerializer)

        self.assertEqual(endpoint.get_serializer(), DummyProductSerializer)

    def test_viewset_factory(self):
        viewset = self.endpoint.get_viewset()
        self.assertEqual(viewset.serializer_class, self.endpoint.get_serializer())

        for backend in (filters.DjangoFilterBackend, filters.SearchFilter):
            self.assertNotIn(backend, viewset.filter_backends)

        self.assertEqual(viewset.__name__, 'ProductViewSet')

        viewset = self.alternate_endpoint.get_viewset()

        for attr in ('permission_classes', 'filter_fields', 'search_fields', 'ordering_fields'):
            self.assertEqual(getattr(viewset, attr), getattr(self, attr))

        for backend in ('DjangoFilterBackend', 'SearchFilter', 'OrderingFilter'):
            self.assertIn(backend, [be.__name__ for be in viewset.filter_backends])

        self.assertEqual(viewset.pagination_class.__name__, 'ProductPagination')
        self.assertTrue(issubclass(
            viewset.pagination_class,
            pagination.PageNumberPagination
        ))

    def test_non_factory_viewset(self):
        endpoint = Endpoint(viewset=DummyProductViewSet)

        self.assertEqual(endpoint.get_viewset(), DummyProductViewSet)
        self.assertEqual(endpoint.get_serializer(), DummyProductSerializer)
        self.assertEqual(endpoint.model, Product)

    def test_inheritance(self):

        class DummyEndpoint(Endpoint):
            model = Product
            permission_classes = self.permission_classes
            filter_fields = self.filter_fields
            search_fields = self.search_fields
            ordering_fields = self.ordering_fields

        endpoint = DummyEndpoint()

        self.assertEqual(endpoint.model, Product)
        self.assertEqual(len(endpoint.get_fields_for_serializer()), len(self.fields) + 1)
        for field in self.fields:
            self.assertIn(field, endpoint.get_fields_for_serializer())
        self.assertIn('__str__', endpoint.get_fields_for_serializer())

        serializer = endpoint.get_serializer()
        self.assertEqual(serializer.Meta.model, Product)
        self.assertEqual(len(serializer.Meta.fields), len(self.endpoint.get_fields_for_serializer()))

        viewset = endpoint.get_viewset()

        for attr in ('permission_classes', 'filter_fields', 'search_fields', 'ordering_fields'):
            self.assertEqual(getattr(viewset, attr), getattr(self, attr))

        for backend in ('DjangoFilterBackend', 'SearchFilter', 'OrderingFilter'):
            self.assertIn(backend, [be.__name__ for be in viewset.filter_backends])

    def test_plurals(self):
        endpoint = Endpoint(model=Category)
        self.assertEqual(endpoint.get_url(), 'sample/categories')

        needs = self.endpoint.get_needs()
        self.assertEqual(len(needs), 1)
        self.assertEqual(needs[0]['plural'], 'categories')

    def test_get_base_viewset(self):

        class DummyViewSet(ModelViewSet):
            pass

        class OtherDummyViewSet(ModelViewSet):
            pass

        class DummyEndpoint(Endpoint):
            model = Product
            base_viewset = DummyViewSet

        class DummyReadOnlyEndpoint(DummyEndpoint):
            read_only = True

        class OtherDummyReadOnlyEndpoint(Endpoint):
            model = Product
            read_only = True
            base_viewset = OtherDummyViewSet
            base_readonly_viewset = DummyViewSet

        dummy = DummyEndpoint()
        self.assertTrue(issubclass(dummy.get_base_viewset(), DummyViewSet))

        dummy = DummyReadOnlyEndpoint()
        self.assertTrue(issubclass(dummy.get_base_viewset(), DummyViewSet))

        dummy = OtherDummyReadOnlyEndpoint()
        self.assertTrue(issubclass(dummy.get_base_viewset(), DummyViewSet))


class RouterTestCase(TestCase):

    def test_register_model(self):
        router.register(Product)
        endpoint = router.get_endpoint('sample/products')
        self.assertTrue(isinstance(endpoint, Endpoint))

    def test_register_endpoint(self):
        router.register(endpoint=Endpoint(Product))
        endpoint = router.get_endpoint('sample/products')
        self.assertTrue(isinstance(endpoint, Endpoint))

    def test_alternate_url(self):
        router.register(Product, url='bogus')
        endpoint = router.get_endpoint('bogus')
        self.assertTrue(isinstance(endpoint, Endpoint))


class ViewSetFactoryTestCase(TestCase):

    def test_pagination(self):
        endpoint = Endpoint(model=Product)
        self.assertEqual(endpoint.viewset.pagination_class.__name__, 'ProductPagination')
        self.assertEqual(endpoint.viewset.pagination_class.page_size, 50)


class UtilsTestCase(TestCase):

    def test_reverse(self):
        utils.reverse('sample/products-list')
        self.assertTrue(True)

    def test_validation_attrs(self):
        data = (
            (CharField(), {}),
            (IntegerField, {}),
            (CharField(min_length=3), {'min': 3}),
            (CharField(max_length=10), {'max': 10}),
            (CharField(min_length=3, max_length=10), {'min': 3, 'max': 10}),
            (IntegerField(min_value=0), {'min': 0}),
            (IntegerField(max_value=100), {'max': 100}),
            (IntegerField(min_value=0, max_value=100), {'min': 0, 'max': 100}),
        )

        for input_field, expected in data:
            result = utils.get_validation_attrs(input_field)
            self.assertEqual(result, expected,
                             'got {} while expecting {} when comparing validation attrs for {}'.format(
                                 result,
                                 expected,
                                 input_field
                             ))

    def test_action_kwargs(self):
        def test_func():
            pass

        custom_btn = 'custom_btn'
        custom_icon = 'custom_icon'
        custom_text = 'custom'

        data = (
            ((None, None, None, test_func, {}), {
                'icon_class': settings.ACTION_ICON_CLASS,
                'btn_class': settings.ACTION_BTN_CLASS,
                'text': 'Test_func',
            }),
            ((custom_icon, None, None, test_func, {}), {
                'icon_class': custom_icon,
                'btn_class': settings.ACTION_BTN_CLASS,
                'text': 'Test_func',
            }),
            ((None, custom_btn, None, test_func, {}), {
                'icon_class': settings.ACTION_ICON_CLASS,
                'btn_class': custom_btn,
                'text': 'Test_func',
            }),
            ((None, None, custom_text, test_func, {}), {
                'icon_class': settings.ACTION_ICON_CLASS,
                'btn_class': settings.ACTION_BTN_CLASS,
                'text': custom_text,
            }),
            ((custom_icon, custom_btn, custom_text, test_func, {}), {
                'icon_class': custom_icon,
                'btn_class': custom_btn,
                'text': custom_text,
            }),
        )

        for input_args, expected_kwargs in data:
            result = utils.action_kwargs(*input_args)
            self.assertEqual(result, expected_kwargs,
                             'got {} while expecting {} when getting action_kwargs for {}'.format(
                                 result,
                                 expected_kwargs,
                                 input_args
                             ))

    @override_settings(USE_I18N=False)
    def test_get_languages_no_i18n(self):
        languages = utils.get_languages()
        self.assertEqual(languages, None)

    @override_settings(USE_I18N=True, LANGUAGES=(('fr', 'french'), ('en', 'english')))
    def test_get_languages_i18n(self):
        languages = utils.get_languages()
        self.assertEqual(len(languages), 2)
        self.assertEqual(languages, ['fr', 'en'])
