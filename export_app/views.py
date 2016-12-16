from django.http import Http404
from django.views.generic import TemplateView
from django.utils.module_loading import import_string

from export_app import settings
from export_app.base import SerializerExporterWithFields, ModelNotFoundException


class BaseModelView(SerializerExporterWithFields, TemplateView):
    adapter_class = import_string(settings.ADAPTER)

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
        except ModelNotFoundException as e:
            raise Http404('No viewset found for {}'.format(e.model))

        fields, rels = self.get_fields_for_model(model, serializer_instance, self.adapter_class)

        # WIP: for models on the fly, we may need to add url name
        # url_name = settings.URL_NAME
        # if settings.URL_NAMESPACE is not None:
        #     url_name = '{}:{}'.format(settings.URL_NAMESPACE, settings.URL_NAME)

        context['fields'] = fields
        context['rels'] = rels
        context['ember_app'] = settings.FRONT_APPLICATION_NAME
        return context
