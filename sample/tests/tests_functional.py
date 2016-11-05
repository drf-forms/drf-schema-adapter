from rest_framework.test import APITestCase

from .factories import CategoryFactory, ProductFactory, HowItWorksFactory
from .base import EndpointAPITestCase

from ..views import AbstractHowItWorksViewSet
from urls import router


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
