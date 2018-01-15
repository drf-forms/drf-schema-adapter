from django.utils.module_loading import import_string

from inflector import Inflector

from rest_framework.response import Response
from rest_framework.serializers import PrimaryKeyRelatedField

from .app_settings import settings
from .utils import action_kwargs, get_field_dict, get_languages


def custom_action(method='GET', type='request', icon_class=None, btn_class=None, text=None, **kwargs):

    kwargs.update({
        'type': type,
    })

    def decorator(func):
        func.bind_to_methods = [method, ]
        func.detail = True
        func.action_type = 'custom'
        func.action_kwargs = action_kwargs(icon_class, btn_class, text, func, kwargs)
        func.kwargs = {}

        return func

    return decorator


def bulk_action(method='GET', type='request', icon_class=None, btn_class=None, text=None, **kwargs):

    kwargs.update({
        'type': type,
    })

    def decorator(func):
        func.bind_to_methods = [method, ]
        func.detail = False
        func.action_type = 'bulk'
        func.action_kwargs = action_kwargs(icon_class, btn_class, text, func, kwargs)
        func.action_kwargs['atOnce'] = func.action_kwargs.get('atOnce', True)
        func.kwargs = {}

        return func

    return decorator


def wizard(target_model, serializer=None, icon_class=None, btn_class=None, text=None, meta_type='custom', **kwargs):

    if serializer is None and target_model is not None:
        serializer = target_model
        target_model = None

    assert serializer is not None, "You need to pass a serializer to the wizard decorator"
    assert meta_type in ['custom', 'list']

    inflector_language = import_string(settings.INFLECTOR_LANGUAGE)
    inflector = Inflector(inflector_language)

    _kwargs = {
        'type': 'wizard',
        'params': {},
    }
    _kwargs.update(kwargs)
    kwargs = _kwargs

    kwargs['params']['fieldsets'] = kwargs.pop('fieldsets', None)

    serializer_instance = serializer()
    needs = []
    fields = []
    Adapter = import_string(settings.METADATA_ADAPTER)
    for field in serializer.Meta.fields:
        field_instance = serializer_instance.fields[field]
        if isinstance(field_instance, PrimaryKeyRelatedField):
            model = field_instance.queryset.model
            needs.append({
                'app': model._meta.app_label,
                'singular': model._meta.model_name.lower(),
                'plural': inflector.pluralize(model._meta.model_name.lower()),
            })
        fields.append(Adapter.adapt_field(get_field_dict(field, serializer)))
    kwargs['params']['needs'] = needs
    kwargs['params']['fields'] = fields
    kwargs['languages'] = get_languages()

    def decorator(func):

        def wizard_func(self, request, *args, **kwargs):
            Serializer = serializer
            serializer_instance = Serializer(data=request.data)

            if not serializer_instance.is_valid():
                return Response(serializer_instance.errors, status=400)

            request.validated_data = serializer_instance.validated_data

            return func(self, request, *args, **kwargs)

        wizard_func.bind_to_methods = [kwargs.pop('method', 'POST'), ]
        wizard_func.action_type = meta_type
        if meta_type == 'custom':
            wizard_func.detail = True
        else:
            wizard_func.detail = False
        wizard_func.wizard = True
        wizard_func.__name__ = func.__name__
        wizard_func.action_kwargs = action_kwargs(icon_class, btn_class, text, wizard_func, kwargs)
        wizard_func.kwargs = {}
        if target_model is not None:
            wizard_func.action_kwargs['params']['model'] = '{}/{}/{}'.format(
                target_model._meta.app_label.lower().replace('_', '-'),
                inflector.pluralize(target_model._meta.model_name.lower()),
                wizard_func.__name__
            )
            print(wizard_func.action_kwargs['params']['model'])
        wizard_func.serializer = serializer

        return Adapter.adapt_wizard(wizard_func)

    return decorator
