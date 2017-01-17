from collections import defaultdict

from django.conf import settings as django_settings


DEFAULT_SETTINGS = {
    'WIDGET_MAPPING': {
        'BooleanField': 'checkbox',
        'NullBooleanField': 'checkbox',
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'ForeignKey': 'foreignkey',
        'ManyToOneRel': 'tomany-table',
        'text': 'textarea',
        'choice': 'select',
        'DateField': 'date',
        'TimeField': 'time',
        'DateTimeField': 'datetime',
        'CharField': 'text',
        'ChoiceField': 'select',
        'EmailField': 'email',
        'URLField': 'url',
        'ManyToManyField': 'manytomany',
        'ManyToManyRel': 'manytomany',
    },
    'METADATA_ADAPTER': 'drf_auto_endpoint.adapters.BaseAdapter',
}


class Settings(object):

    def __init__(self):
        mapping = getattr(django_settings, 'DRF_AUTO_WIDGET_MAPPING', {})
        mapping.update(DEFAULT_SETTINGS['WIDGET_MAPPING'])
        self.WIDGET_MAPPING = defaultdict(lambda: 'text')
        for k, v in mapping.items():
            self.WIDGET_MAPPING[k] = v

    def __getattr__(self, name):
        if name not in DEFAULT_SETTINGS:
            raise AttributeError(name)
        return getattr(django_settings, 'DRF_AUTO_{}'.format(name), DEFAULT_SETTINGS[name])


settings = Settings()
