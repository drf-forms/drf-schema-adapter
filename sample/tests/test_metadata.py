from django.test import TestCase

from drf_auto_endpoint.metadata import AutoMetadataMixin

from sample.endpoints import ProductEndpoint

from .data import DummyProductSerializer


class TestMetadata(TestCase):

    def test_placeholder(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer
            endpoint = ProductEndpoint(fields=['name'])

        view = MockView()
        metadata = metadata_mixin.determine_metadata(request, view)
        self.assertIn('placeholder', metadata[0]['ui'])

    def test_produce_metadata_with_serializer(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer
            endpoint = ProductEndpoint(serializer=DummyProductSerializer)

        view = MockView()
        try:
            metadata_mixin.determine_metadata(request, view)
        except:
            self.fail('Unable to produce metatdata')

    def test_produce_metadata_withoutendpoint(self):
        metadata_mixin = AutoMetadataMixin()
        request = None

        class MockView(object):
            serializer_class = DummyProductSerializer

        view = MockView()
        try:
            metadata_mixin.determine_metadata(request, view)
        except:
            self.fail('Unable to produce metatdata')
