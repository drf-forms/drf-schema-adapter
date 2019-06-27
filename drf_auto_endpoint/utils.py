from django.conf import settings as django_settings
from django.utils.module_loading import import_string
from django.utils.text import capfirst

from inflector import Inflector

from .app_settings import settings
from .get_field_dict import get_field_dict  # NoQA


inflector_language = import_string(settings.INFLECTOR_LANGUAGE)
inflector = Inflector(inflector_language)


def action_kwargs(icon_class, btn_class, text, func, kwargs):

    kwargs.update({
        'icon_class': icon_class if icon_class is not None else settings.ACTION_ICON_CLASS,
        'btn_class': btn_class if btn_class is not None else settings.ACTION_BTN_CLASS,
    })

    if text is None:
        kwargs['text'] = capfirst(func.__name__.lower())
    else:
        kwargs['text'] = text

    return kwargs


def get_languages():
    if django_settings.USE_I18N:
        return [
            x[0] for x in getattr(django_settings, 'LANGUAGES', [[django_settings.LANGUAGE_CODE]])
        ]
    else:
        return None
