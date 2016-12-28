from django.test import TestCase

from rest_framework.permissions import AllowAny
from rest_framework import filters, pagination

from ..models import Product, Category, PRODUCT_TYPES

from .data import DummyProductSerializer, DummyProductViewSet

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router


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

        self.assertEqual(viewset.pagination_class, pagination.PageNumberPagination)

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
