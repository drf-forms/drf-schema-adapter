class BaseAdapter(object):
    """
    Basic adapter that renders a dict to json with no modifications.
    """

    def render(self, config):
        return config

    def __call__(self, config):
        return self.render(config)


def to_html_tag(widget_type):
    if widget_type == 'checkbox':
        return 'checkbox'
    if widget_type == 'select':
        return 'select'
    return 'input'


class AngularFormlyAdapter(BaseAdapter):

    def render(self, config):
        config["validation"].update({
            "label": config['ui']['label'],
            "type": config['type'],
        })

        adapted = {
            'key': config['key'],
            "type": to_html_tag(config['type']),
            "templateOptions": config['validation']
        }

        if 'default' in config:
            adapted['defaultValue'] = config['default']

        return adapted
