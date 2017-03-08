from django.conf import settings as django_settings


DEFAULT_SETTINGS = {
    'ROUTER_PATH': 'urls.router',
    'URL_NAMESPACE': None,
    'URL_NAME': 'djember_model',
    'FRONT_APPLICATION_NAME': 'appName',
    'FRONT_APPLICATION_PATH': '../front',
    'BACK_API_BASE': '/api/v1',
    'URL_FORMAT': '{app}/{model}',
    'FIELD_TYPE_MAPPING': {},
    'DEFAULT_MAPPING': None,
    'ADAPTER': 'export_app.adapters.EmberAdapter'
}


class Settings(object):

    def __getattr__(self, name):
        if name not in DEFAULT_SETTINGS:
            raise AttributeError(name)
        return getattr(django_settings, 'EXPORTER_{}'.format(name), DEFAULT_SETTINGS[name])


settings = Settings()
