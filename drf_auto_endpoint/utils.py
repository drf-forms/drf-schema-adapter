from django.conf import settings as django_settings


def get_validation_attrs(instance_field):
    rv = {}

    attrs_to_validation = {
        'min_length': 'min',
        'max_length': 'max',
        'min_value': 'min',
        'max_value': 'max'
    }
    for attr_name, validation_name in attrs_to_validation.items():
        if getattr(instance_field, attr_name, None):
            rv[validation_name] = getattr(instance_field, attr_name)

    return rv

def get_languages():
    if django_settings.USE_I18N:
        return [
            x[0] for x in getattr(django_settings, 'LANGUAGES', [[django_settings.LANGUAGE_CODE]])
        ]
    else:
        return None

