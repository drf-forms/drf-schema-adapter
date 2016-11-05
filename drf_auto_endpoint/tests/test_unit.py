from django.test import TestCase

from drf_auto_endpoint.adapters import BaseAdapter
import json


class AdapterTestCase(TestCase):

    def setUp(self):
        """
        """

    def test_base_adapter(self):
        adapter = BaseAdapter()
        config = { "hello" : "world" }
        json_config = adapter(config)
        self.assertEqual(json_config, json.dumps(config))
