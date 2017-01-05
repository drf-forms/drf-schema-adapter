from django.test import TestCase

from drf_auto_endpoint.adapters import (
    AngularFormlyAdapter,
    BaseAdapter,
    EmberAdapter,
)


class AdapterTestCase(TestCase):

    def setUp(self):
        self._input = {
            'fields': [{
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
            }],
            'fieldsets': [{
                'title': None,
                'fields': [{
                    'key': '__str__'
                }]
            }]
        }

    def test_base_adapter(self):
        adapter = BaseAdapter()
        json_config = adapter(self._input)
        assert json_config == self._input['fields']

    def test_angular_formly_adapter(self):
        adapter = AngularFormlyAdapter()
        output = adapter(self._input)

        expected = [{
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
        }]

        self.assertEqual(output, expected)

    def test_ember_adapter(self):
        adapter = EmberAdapter()
        ember_input = dict(**self._input)
        ember_input['fields'][0]["related_endpoint"] = "test"
        output = adapter(ember_input)

        expected = {
            "fields": [{
                "readonly": False,
                "extra": {
                    "related_model": "test",
                    "default": 20,
                },
                "name": "age",
                "label": "Age",
                "widget": "number"
                "required": False
            }],
            "fieldsets": [{
                "title": None,
                "fields": [{
                    "name": "__str__"
                }]
            }]
        }

        self.assertEqual(output, expected)
