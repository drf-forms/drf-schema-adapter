from collections import namedtuple


PROPERTY = 1
GETTER = 0
MetaDataInfo = namedtuple('MetaDataInfo', ['attr', 'attr_type', 'default'])


class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
    ]

    def render(self, config):
        return config['fields']

    def render_root(self, config):
        return config

    def __call__(self, config):
        return self.render(config)


def to_html_tag(widget_type):
    if widget_type in ["checkbox", "select"]:
        return widget_type
    return "input"


class AngularFormlyAdapter(BaseAdapter):

    def render(self, config):
        fields = config['fields'];
        adapted = []
        for field in fields:
            field["validation"].update({
                "label": field["ui"]["label"],
                "type": field["type"],
            })

            new_field = {
                "key": field["key"],
                "read_only": field["read_only"],
                "type": to_html_tag(field["type"]),
                "templateOptions": field["validation"]
            }

            if "placeholder" in field["ui"]:
                new_field["templateOptions"]["placeholder"] = field["ui"]["placeholder"]

            if "default" in field:
                new_field["defaultValue"] = field["default"]

            adapted.append(new_field)

        return adapted


class EmberAdapter(BaseAdapter):
    """
    Here is an example of the expected output
        [{
            "read_only": False,
            "extra": {
                "related_model": "emberadmin/category",
                "choices": [{"foo": "bar"}]
            },
            "name": "category",
            "label": "Category",
            "widget": "foreignkey"
        }, ...]
    """

    metadata_info = [
        MetaDataInfo('fields', GETTER, []),
        MetaDataInfo('fieldsets', GETTER, []),
        MetaDataInfo('list_display', GETTER, []),
        MetaDataInfo('filter_fields', GETTER, []),
        MetaDataInfo('languages', GETTER, []),
        MetaDataInfo('ordering_fields', GETTER, []),
        MetaDataInfo('needs', GETTER, []),
        MetaDataInfo('list_editable', GETTER, []),
        MetaDataInfo('sortable_by', GETTER, []),
        MetaDataInfo('translated_fields', GETTER, []),
        MetaDataInfo('custom_actions', GETTER, []),
        MetaDataInfo('bulk_actions', GETTER, []),
        MetaDataInfo('save_twice', PROPERTY, False),
        MetaDataInfo('search_enabled', PROPERTY, False),
    ]

    @classmethod
    def adapt_field(cls, field):
        new_field = {
            'label': field['ui']['label'],
            'readonly': field['read_only'],
            'extra': {},
            'name': field['key'],
            'widget': field['type'],
            'required': field['validation']['required'],
            'translated': field['translated'],
        }

        if 'choices' in field:
            new_field['extra']['choices'] = field['choices']

        if 'related_endpoint' in field:
            new_field['extra']['related_model'] = field['related_endpoint'].replace('_', '-')

        if 'placeholder' in field['ui']:
            new_field['extra']['placeholder'] = field['ui']['placeholder']

        if 'default' in field:
            new_field['extra']['default'] = field['default']

        return new_field

    def render(self, config):
        fields = config['fields']
        adapted = []
        for field in fields:
            adapted.append(self.adapt_field(field))

        config['fields'] =  adapted
        for i, fs in enumerate(config['fieldsets']):
            for j, f in enumerate(fs['fields']):
                new_field = f
                if 'key' in f:
                    new_field['name'] = new_field.pop('key')
                fs['fields'][j] = new_field
            config['fieldsets'][i] = fs

        for i, need in enumerate(config.get('needs', [])):
            config['needs'][i] = {
                key: value.replace('_', '-')
                for key, value in need.items()
            }

        return config
