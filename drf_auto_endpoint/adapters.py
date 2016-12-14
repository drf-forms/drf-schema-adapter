class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    def render(self, config):
        return config['fields']

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
        config["validation"].update({
            "label": config["ui"]["label"],
            "type": config["type"],
        })

        adapted = {
            "key": config["key"],
            "read_only": config["read_only"],
            "type": to_html_tag(config["type"]),
            "templateOptions": config["validation"]
        }

        if "placeholder" in config["ui"]:
            adapted["templateOptions"]["placeholder"] = config["ui"]["placeholder"]

        if "default" in config:
            adapted["defaultValue"] = config["default"]

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
                "label": field["ui"]["label"],
                "read_only": field["read_only"],
                "extra": {},
                "name": field["key"],
                "widget": field["type"],
            }

            if "choices" in field:
                new_field["extra"]["choices"] = field["choices"]

            if "related_endpoint" in field:
                new_field["extra"]["related_model"] = field["related_endpoint"]

            if "placeholder" in field["ui"]:
                new_field["extra"]["placeholder"] = field["ui"]["placeholder"]

            if "default" in field:
                new_field["extra"]["default"] = field["default"]

            adapted.append(new_field)

        config['fields'] =  adapted

        return config
