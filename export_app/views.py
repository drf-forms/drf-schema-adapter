from django.http import Http404
from django.views.generic import TemplateView
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class BaseModelView(SerializerExporterWithFields, TemplateView):
    adapter_class = import_string(settings.ADAPTER)
    content_type = 'text/javascript'

    def get_template_names(self):
        return [self.adapter_class.dynamic_template_name]


class EmberModelView(BaseModelView):
    """
    Generate resource on the fly for Ember
    """

    def get_context_data(self, **kwargs):
        context = super(EmberModelView, self).get_context_data(**kwargs)
        try:
            model, serializer_instance, context['model_name'], context['application_name'] = \
                self.get_serializer_for_basename(self.kwargs['model'])
            endpoint = self.get_endpoint_for_basename(self.kwargs['model'])
        except ModelNotFoundException as e:
            raise Http404('No viewset found for {}'.format(e.model))

        for item in ['model_name', 'application_name']:
            context[item] = context[item].replace('_', '-')

        fields, rels = self.get_fields_for_model(model, serializer_instance, self.adapter_class,
                                                 endpoint=endpoint)

        # WIP: for models on the fly, we may need to add url name
        # url_name = settings.URL_NAME
        # if settings.URL_NAMESPACE is not None:
        #     url_name = '{}:{}'.format(settings.URL_NAMESPACE, settings.URL_NAME)

        context['fields'] = fields
        context['rels'] = []
        for rel in rels:
            for item in ['app', 'related_model']:
                rel[item] = rel[item].replace('_', '-')
            context['rels'].append(rel)

        context['ember_app'] = settings.FRONT_APPLICATION_NAME
        return context


class WizardModelView(BaseModelView):

    def get_context_data(self, **kwargs):
        context = super(WizardModelView, self).get_context_data(**kwargs)
        base_name, method_name = self.kwargs['model'].rsplit('/', 1)
        context['application_name'] = 'wizard/{}'.format(base_name.replace('_', '-'))
        context['model_name'] = method_name.replace('_', '-')

        viewset, model_name, application_name = \
            self.get_viewset_for_basename(base_name, dasherize=self.adapter_class.dasherize)
        serializer = getattr(viewset, method_name).serializer
        serializer_instance = serializer()

        fields, rels = self.get_fields_for_model(None, serializer_instance, self.adapter_class)

        context['fields'] = fields
        context['rels'] = []
        for rel in rels:
            for item in ['app', 'related_model']:
                rel[item] = rel[item].replace('_', '-')
            context['rels'].append(rel)

        context['ember_app'] = settings.FRONT_APPLICATION_NAME
        return context
