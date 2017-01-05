class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    def render(self, config):
        return config['fields']

    def render_root(self, config):
        return config

    def __call__(self, config):
        return self.render(config)


def to_html_tag(widget_type):
    if widget_type == "checkbox":
        return "checkbox"
    if widget_type == "select":
        return "select"
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

    def render(self, config):
        fields = config['fields'];
        adapted = []
        for field in fields:
            new_field = {
                'label': field['ui']['label'],
                'readonly': field['read_only'],
                'extra': {},
                'name': field['key'],
                'widget': field['type'],
                'required': field['validation']['required'],
            }

            if 'choices' in field:
                new_field['extra']['choices'] = field['choices']

            if 'related_endpoint' in field:
                new_field['extra']['related_model'] = field['related_endpoint']

            if 'placeholder' in field['ui']:
                new_field['extra']['placeholder'] = field['ui']['placeholder']

            if 'default' in field:
                new_field['extra']['default'] = field['default']

            adapted.append(new_field)

        config['fields'] =  adapted
        for i, fs in enumerate(config['fieldsets']):
            for j, f in enumerate(fs['fields']):
                new_field = f
                if 'key' in f:
                    new_field['name'] = new_field.pop('key')
                fs['fields'][j] = new_field
            config['fieldsets'][i] = fs

        return config
