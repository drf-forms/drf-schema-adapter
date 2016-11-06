from django.test import TestCase

from drf_auto_endpoint.adapters import (
    AngularFormlyAdapter,
    BaseAdapter,
    EmberAdapter,
)


class AdapterTestCase(TestCase):

    def setUp(self):
        self._input = {
            "key": "age",
            "type": "number",
            "default": 20,
            "read_only": False,
            "ui": {
                "label": "Age",
            },
            "validation": {
                "required": False,
                "min": 10,
                "max": 100,
            },
            "extra": {}
        }

    def test_base_adapter(self):
        adapter = BaseAdapter()
        config = {"hello": "world"}
        json_config = adapter(config)
        assert json_config == config

    def test_angular_formly_adapter(self):
        adapter = AngularFormlyAdapter()
        output = adapter(self._input)

        expected = {
            "key": "age",
            "type": "input",
            "read_only": False,
            "templateOptions": {
                "label": "Age",
                "type": "number",
                "required": False,
                "min": 10,
                "max": 100
            },
            "defaultValue": 20
        }

        self.assertEqual(output, expected)

    def test_ember_adapter(self):
        adapter = EmberAdapter()
        ember_input = dict(**self._input)
        ember_input["extra"]["related_endpoint"] = "test"
        output = adapter(self._input)

        expected = {
            "read_only": False,
            "extra": {
                "related_model": "test",
            },
            "name": "age",
            "label": "Age",
            "widget": "number"
        }

        self.assertEqual(output, expected)
