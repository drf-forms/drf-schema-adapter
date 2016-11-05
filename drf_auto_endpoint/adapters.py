import json

class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    def render_json(self, config):
        return config


    def __call__(self, config):
        return self.render_json(config)
