from django.conf import settings as django_settings
from django.core.exceptions import FieldDoesNotExist
from django.utils.text import capfirst
from django.db.models.fields import NOT_PROVIDED

from rest_framework import serializers, relations
from rest_framework.fields import empty

from .app_settings import settings


def reverse(*args, **kwargs):
    try:
        exception = ModuleNotFoundError
    except:
        ## py 3.6+
        exception = ImportError

    try:
        from django.core.urlresolvers import reverse
        return reverse(*args, **kwargs)
    except exception:
        # Django 1.11+
        from django.urls.resolvers import get_resolver
        resolver = get_resolver()
        return resolver.reverse(*args, **kwargs)


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


def get_field_dict(field, serializer, translated_fields=None, fields_annotation=False, model=None):
    if translated_fields is None:
        translated_fields = []

    serializer_instance = serializer()
    name = field['name'] if isinstance(field, dict) else field
    field_instance = serializer_instance.fields[name]
    read_only = name == '__str__'
    if not read_only and field_instance.read_only:
        if not isinstance(field_instance, serializers.ManyRelatedField):
            read_only = True

    rv = {
        'key': name,
        'type': settings.WIDGET_MAPPING[field_instance.__class__.__name__],
        'read_only': read_only,
        'ui': {
            'label': name.title().replace('_', ' ')
            if name != '__str__'
            else serializer_instance.Meta.model.__name__,
        },
        'validation': {
            'required': field_instance.required,
        },
        'extra': {},
        'translated': name in translated_fields
    }

    if fields_annotation and name in fields_annotation:
        if 'placeholder' in fields_annotation[name]:
            rv['ui']['placeholder'] = fields_annotation[name]['placeholder']
        if 'help' in fields_annotation[name]:
            rv['ui']['help'] = fields_annotation[name]['help']
    if field_instance.help_text is not None and 'help' not in rv['ui']:
        rv['ui']['help'] = field_instance.help_text

    default = field_instance.default
    model_field = None
    if model:
        try:
            model_field = model._meta.get_field(field_instance.source)
        except FieldDoesNotExist:
            pass

    if default and default != empty:
        rv['default'] = default
    elif default == empty and hasattr(model_field, 'default'):
        default = model_field.default
        if default != NOT_PROVIDED:
            if callable(default):
                default = default()
            rv['default'] = default

    if isinstance(field_instance, (relations.PrimaryKeyRelatedField, relations.ManyRelatedField)):
        if model_field:
            related_model = model_field.related_model
            rv['type'] = settings.WIDGET_MAPPING[model_field.__class__.__name__]
        else:
            related_model = field_instance.queryset.model
        if model_field and model_field.__class__.__name__ == 'ManyToManyRel':
            rv['validation']['required'] = False
        rv['related_endpoint'] = '{}/{}'.format(
            related_model._meta.app_label,
            related_model._meta.model_name.lower()
        )
    elif hasattr(field_instance, 'choices'):
        rv['type'] = settings.WIDGET_MAPPING['choice']
        rv['choices'] = [
            {
                'label': v,
                'value': k,
            } for k, v in field_instance.choices.items()
        ]

    rv['validation'].update(get_validation_attrs(field_instance))

    if isinstance(field, dict):
        extra = rv['extra']
        extra.update(field.get('extra', {}))
        rv.update(field)
        rv['extra'] = extra

    return rv


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
