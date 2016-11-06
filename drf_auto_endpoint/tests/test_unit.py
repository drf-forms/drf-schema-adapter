from django.test import TestCase

from drf_auto_endpoint.adapters import (
    AngularFormlyAdapter,
    BaseAdapter,
)


class AdapterTestCase(TestCase):

    def setUp(self):
        pass

    def test_base_adapter(self):
        adapter = BaseAdapter()
        config = {"hello": "world"}
        json_config = adapter(config)
        assert json_config == config

    def test_angular_formly_adapter(self):
        adapter = AngularFormlyAdapter()
        _input = {
            "key": "favorite_int",
            "type": "number",
            "default": 20,
            "ui": {
                "label": "Favorite integer between 10 and 100",
            },
            "validation": {
                "required": False,
                "min": 10,
                "max": 100,
            }
        }

        output = adapter(_input)

        expected = {
            "key": "favorite_int",
            "type": "input",
            "templateOptions": {
                "label": "Favorite integer between 10 and 100",
                "type": "number",
                "required": False,
                "min": 10,
                "max": 100
            },
            "defaultValue": 20
        }

        self.assertEqual(output, expected)
