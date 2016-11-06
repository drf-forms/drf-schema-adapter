from collections import defaultdict

from django.conf import settings as django_settings


DEFAULT_SETTINGS = {
    'ROUTER_PATH': 'urls.router',
    'URL_NAMESPACE': None,
    'URL_NAME': 'djember_model',
    'FRONT_APPLICATION_NAME': 'appName',
    'FRONT_APPLICATION_PATH': '../front',
    'URL_FORMAT': '{app}/{model}',
    'FIELD_TYPE_MAPPING': {
        'BooleanField': 'boolean',
        'NullBooleanField': 'boolean',
        'IntegerField': 'number',
        'FloatField': 'number',
        'DecimalField': 'number',
        'ListField': None,
        'DictField': None,
        'JSONField': None,
        'PrimaryKeyRelatedField': 'belongsTo',
        'ManyRelatedField': 'hasMany',
    },
    'ADAPTER': 'export_app.adapters.EmberAdapter'
}


class Settings(object):

    def __init__(self):
        mapping = getattr(django_settings, 'EXPORTER_FIELD_TYPE_MAPPING', {})
        mapping.update(DEFAULT_SETTINGS['FIELD_TYPE_MAPPING'])
        self.FIELD_TYPE_MAPPING = defaultdict(lambda: 'string')
        for k, v in mapping.items():
            self.FIELD_TYPE_MAPPING[k] = v

    def __getattr__(self, name):
        if name not in DEFAULT_SETTINGS:
            raise AttributeError(name)
        return getattr(django_settings, 'EXPORTER_{}'.format(name), DEFAULT_SETTINGS[name])


settings = Settings()
