from django.test import override_settings, TestCase, RequestFactory
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import CategoryFactory, ProductFactory, HowItWorksFactory
from .base import EndpointAPITestCase
from .data import ProductFilterSet

from ..models import HowItWorks, Product

from urls import router


class ItRendersAPITest(APITestCase):

    def _do_test(self):

        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.options('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/sample/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.options('/api/sample/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(DRF_AUTO_METADATA_ADAPTER='drf_auto_endpoint.adapters.EmberAdapter')
    def test_ember_adapter(self):
        self._do_test()

    @override_settings(DRF_AUTO_METADATA_ADAPTER='drf_auto_endpoint.adapters.AngularFormlyAdapter')
    def test_formly_adapter(self):
        self._do_test()

    @override_settings(DRF_AUTO_METADATA_ADAPTER='drf_auto_endpoint.adapters.ReactJsonSchemaAdapter')
    def test_jsonschema_adapter(self):
        self._do_test()

    @override_settings(DRF_AUTO_METADATA_ADAPTER='drf_auto_endpoint.adapters.BaseAdapter')
    def test_base_adapter(self):
        self._do_test()


# We exclude request_aware_endpoint because it requires request to operate, and during export there is no such thing.
@override_settings(EXPORTER_EXCLUDE=('sample/request_aware_categories',))
class ItExportsTest(TestCase):

    def _do_test(self):
        call_command('export', all=True, noinput=True)

    @override_settings(EXPORTER_ADAPTER='export_app.adapters.EmberAdapter')
    def test_ember_export(self):
        self._do_test()

    @override_settings(EXPORTER_ADAPTER='export_app.adapters.Angular2Adapter')
    def test_angular2_export(self):
        self._do_test()

    @override_settings(EXPORTER_ADAPTER='export_app.adapters.MetadataAdapter')
    def test_metadata_export(self):
        self._do_test()

    @override_settings(EXPORTER_ADAPTER='export_app.adapters.MetadataES6Adapter')
    def test_metadata_es6_export(self):
        self._do_test()

    @override_settings(EXPORTER_ADAPTER='export_app.adapters.MobxAxiosAdapter')
    def test_mobx_axios_export(self):
        self._do_test()


class CategoryAPITest(EndpointAPITestCase, APITestCase):

    endpoint_url = 'sample/categories'
    model_factory_class = CategoryFactory

    create_requires_login = False
    update_requires_login = False
    delete_requires_login = False


class ProductAPITest(EndpointAPITestCase, APITestCase):

    endpoint_url = 'sample/products'
    model_factory_class = ProductFactory

    create_requires_login = False
    update_requires_login = False
    delete_requires_login = False


class HowItWorksAPITest(EndpointAPITestCase, APITestCase):

    endpoint_url = 'sample/howitworks'
    model_factory_class = HowItWorksFactory

    create_requires_login = False
    update_requires_login = False
    delete_requires_login = False

    def setUp(self):
        super(HowItWorksAPITest, self).setUp()
        self.called = router._endpoints[self.endpoint_url].viewset.called_counter

    def test_list_view(self):
        super(HowItWorksAPITest, self).test_list_view()
        self.assertTrue(self.called < router._endpoints[self.endpoint_url].viewset.called_counter,
                        router._endpoints[self.endpoint_url].viewset.called_counter)

    def test_custom_action(self):
        self.test_model.count = 0
        self.test_model.save()
        response = self.client.post(
            '/api/sample/howitworks/{}/increment/'.format(self.test_model.id),
            {}
        )
        self.assertEqual(response.status_code, 200)

        self.test_model.refresh_from_db()
        self.assertEqual(self.test_model.count, 1)

    def test_bulk_action(self):
        self.test_model.count = 10
        self.test_model.save()

        other_record = HowItWorksFactory(count=23)
        other_record.save()

        record_with_zero = HowItWorks(count=0)
        record_with_zero.save()

        response = self.client.post('/api/sample/howitworks/decrement/', {})
        self.assertEqual(response.status_code, 204)

        for record, expected in ((self.test_model, 9), (other_record, 22), (record_with_zero, 0)):
            record.refresh_from_db()
            self.assertEqual(record.count, expected)

    def test_wizard(self):
        self.test_model.count = 40
        self.test_model.save()

        response = self.client.post(
            '/api/sample/howitworks/{}/add/'.format(self.test_model.id),
            {'amount': 2}
        )
        self.assertEqual(response.status_code, 200)

        self.test_model.refresh_from_db()
        self.assertEqual(self.test_model.count, 42)


class ResponseDataMixin:

    def get_response_data(self, response):
        import django
        from distutils.version import LooseVersion

        self.assertEqual(200, response.status_code)

        if LooseVersion(django.get_version()) >= LooseVersion('1.9'):
            return response.json()
        return response.data


class PaginationTestCase(ResponseDataMixin, APITestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(251):
            CategoryFactory().save()
        cls.url = '/api/sample/categories/'

    def test_default_page_size(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(len(self.get_response_data(response)['results']), 50)

    def test_custom_page_size(self):
        page_size = 250
        response = self.client.get('{}?page_size={}'.format(self.url, page_size), format='json')
        self.assertEqual(len(self.get_response_data(response)['results']), page_size)


class FilterTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.count = 2
        for i in range(cls.count):
            cat = CategoryFactory()
            cat.save()
            setattr(cls, f'cat{i}', cat)
            product = ProductFactory(category=cat)
            product.save()
            setattr(cls, f'product{i}', product)
        cls.url = '/api/sample/products/'

    def setUp(self):
        from drf_auto_endpoint.endpoints import Endpoint

        self.endpoint = Endpoint(model=Product, filter_fields=('category_id', ))
        self.factory = RequestFactory()

    def test_unfiltered_count(self):
        request = self.factory.get(f'{self.url}?format=json')
        response = self.endpoint.viewset.as_view({'get': 'list'})(request)
        self.assertEqual(len(response.data['results']), self.count)

    def test_filtered_count(self):
        request = self.factory.get(f'{self.url}?format=json&category_id={self.cat1.id}')
        response = self.endpoint.viewset.as_view({'get': 'list'})(request)
        self.assertEqual(len(response.data['results']), 1)

class FilterClassTestCase(FilterTestCase):

    def setUp(self):
        from drf_auto_endpoint.endpoints import Endpoint

        class ProductEndpoint(Endpoint):
            model = Product
            filter_class = ProductFilterSet

        self.endpoint = ProductEndpoint()
        self.factory = RequestFactory()

class BaseFilterClassTestCase(FilterTestCase):

    def setUp(self):
        from drf_auto_endpoint.endpoints import Endpoint

        class ProductEndpoint(Endpoint):
            model = Product
            base_filter_class = ProductFilterSet
            filter_fields = ['category_id']

        self.endpoint = ProductEndpoint()
        self.factory = RequestFactory()


class RequestAwareEndpointTestCase(ResponseDataMixin, APITestCase):
    url = '/api/sample/request_aware_categories/'

    def test_options_depend_on_request(self):
        """Serializer fields (reported in OPTIONS) is based on incoming request"""
        response = self.client.options(self.url, USERNAME='Joe')
        self.assertNotIn('name', (field['key'] for field in self.get_response_data(response)))

        response = self.client.options(self.url, USERNAME='Pirx')
        self.assertIn('name', (field['key'] for field in self.get_response_data(response)))
