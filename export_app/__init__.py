from collections import defaultdict

from django.conf import settings as django_settings


DEFAULT_SETTINGS = {
    'ROUTER_PATH': 'urls.router',
    'URL_NAMESPACE': None,
    'URL_NAME': 'djember_model',
    'EMBER_APPLICATION_NAME': 'djember',
    'EMBER_APPLICATION_PATH': '../front',
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
    }
}


class Settings:

    def __init__(self):
        mapping = getattr(django_settings, 'DJEMBER_FIELD_TYPE_MAPPING', {})
        mapping.update(DEFAULT_SETTINGS['FIELD_TYPE_MAPPING'])
        self.FIELD_TYPE_MAPPING = defaultdict(lambda: 'string')
        for k, v in mapping.items():
            self.FIELD_TYPE_MAPPING[k] = v

    def __getattr__(self, name):
        if name not in DEFAULT_SETTINGS:
            raise AttributeError(name)
        return getattr(django_settings, 'DJEMBER_{}'.format(name), DEFAULT_SETTINGS[name])


settings = Settings()
