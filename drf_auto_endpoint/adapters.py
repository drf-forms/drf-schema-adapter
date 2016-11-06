class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    def render(self, config):
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
        {
            "read_only": False,
            "extra": {
                "related_model": "emberadmin/category",
                "choices": [{"foo": "bar"}]
            },
            "name": "category",
            "label": "Category",
            "widget": "foreignkey"
        }
    """

    def render(self, config):
        adapted = {
            "label": config["ui"]["label"],
            "read_only": config["read_only"],
            "extra": {},
            "name": config["key"],
            "widget": config["type"],
        }

        if "choices" in config["extra"]:
            adapted["extra"]["choices"] = config["extra"]["choices"]
        if "related_endpoint" in config["extra"]:
            adapted["extra"]["related_model"] = config["extra"]["related_endpoint"]

        return adapted
