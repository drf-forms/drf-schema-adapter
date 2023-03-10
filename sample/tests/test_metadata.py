from django.test import TestCase

from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.metadata import AutoMetadataMixin

from sample.endpoints import ProductEndpoint, HowItWorksEndpoint, FirstFieldEndpoint, SecondFieldEndpoint

from ..models import ProductChoice
from .data import (DummyProductSerializer, DummyProductViewSet, DummyProductSerializerWithAllFields,
                   DummyChoicesSerializer, ProductChoiceSerializer)


class TestMetadata(TestCase):

    def test_placeholder(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer
            endpoint = ProductEndpoint(fields=['name'])

            def get_serializer_class(self):
                return self.serializer_class

        view = MockView()
        metadata = metadata_mixin.determine_metadata(request, view)
        self.assertIn('placeholder', metadata[0]['ui'])

    def test_produce_metadata_with_serializer(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer
            endpoint = ProductEndpoint(serializer=DummyProductSerializer)

            def get_serializer_class(self):
                return self.serializer_class

        view = MockView()
        try:
            metadata_mixin.determine_metadata(request, view)
        except Exception:
            self.fail('Unable to produce metatdata')

    def test_produce_metadata_withoutendpoint(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer

            def get_serializer_class(self):
                return self.serializer_class

        view = MockView()
        try:
            metadata_mixin.determine_metadata(request, view)
        except Exception:
            self.fail('Unable to produce metatdata')

    def test_filter_and_search_fields_defined_on_viewset(self):
        endpoint = ProductEndpoint(viewset=DummyProductViewSet)
        self.assertTrue(endpoint.search_enabled)
        self.assertIn('name', endpoint.get_filter_fields())

    def test__all__fields_in_serializer(self):
        metadata_mixin = AutoMetadataMixin()

        class MockView(object):
            serializer_class = DummyProductSerializerWithAllFields
            endpoint = ProductEndpoint(serializer=DummyProductSerializerWithAllFields)

            def get_serializer_class(self):
                return self.serializer_class

        request = None
        view = MockView()
        metadata = metadata_mixin.determine_metadata(request, view)
        self.assertEqual(['id', 'name', 'product_type', 'category'], [item['key'] for item in metadata])

    def test_custom_actions_are_present(self):
        endpoint = HowItWorksEndpoint()
        custom_actions = endpoint.get_custom_actions()
        self.assertGreater(len(custom_actions), 0)

    def test_named_fieldsets(self):
        endpoint = FirstFieldEndpoint()
        fieldsets = endpoint.get_fieldsets()

        self.assertEqual(len(fieldsets), 1)
        self.assertIn('first_field', [fs.get('key', None) for fs in fieldsets])

        endpoint = SecondFieldEndpoint()
        fieldsets = endpoint.get_fieldsets()

        self.assertEqual(len(fieldsets), 2)
        self.assertIn('third_field', [fs.get('key', None) for fs in fieldsets])

    def test_choices_in_metadata_from_serializer_only(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyChoicesSerializer

            def get_serializer_class(self):
                return self.serializer_class

        view = MockView()
        metadata = metadata_mixin.determine_metadata(request, view)

        for i in range(2):
            # There are 2 fields in DummyChoiesSerializer and both should have choices
            self.assertIn('choices', metadata[i])
