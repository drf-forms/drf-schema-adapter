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
