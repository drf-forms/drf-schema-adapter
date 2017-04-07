from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import CategoryFactory, ProductFactory, HowItWorksFactory
from .base import EndpointAPITestCase

from ..views import AbstractHowItWorksViewSet
from urls import router


class ItRendersAPITest(APITestCase):

    def _do_test(self):

        response = self.client.get('/api/');
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.options('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/sample/categories/');
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
