from django.utils.text import capfirst

from .app_settings import settings


def custom_action(method='GET', type='request', icon_class=None, btn_class=None, text=None, **kwargs):

    kwargs.update({
        'type': type,
        'icon_class': icon_class if icon_class is not None else settings.ACTION_ICON_CLASS,
        'btn_class': btn_class if btn_class is not None else settings.ACTION_BTN_CLASS,
    })

    def decorator(func):
        func.bind_to_methods = [method, ]
        func.detail = True
        func.action_type = 'custom'
        func.action_kwargs = kwargs
        func.kwargs = {}

        if text is None:
            func.action_kwargs['text'] = capfirst(func.__name__.lower())
        else:
            func.action_kwargs['text'] = text

        return func

    return decorator


def bulk_action(method='GET', type='request', icon_class=None, btn_class=None, text=None, **kwargs):

    kwargs.update({
        'type': type,
        'icon_class': icon_class if icon_class is not None else settings.ACTION_ICON_CLASS,
        'btn_class': btn_class if btn_class is not None else settings.ACTION_BTN_CLASS,
    })

    def decorator(func):
        func.bind_to_methods = [method, ]
        func.detail = False
        func.action_type = 'bulk'
        func.action_kwargs = kwargs
        func.kwargs = {}

        if text is None:
            func.action_kwargs['text'] = capfirst(func.__name__.lower())
        else:
            func.action_kwargs['text'] = text

        return func

    return decorator
