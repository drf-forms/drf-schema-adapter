from .utils import action_kwargs


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
