from django.views.generic import TemplateView
from django.http import Http404

from djember_model import settings
from djember_model.base import SerializerExporter, ModelNotFoundException


class EmberModelView(SerializerExporter, TemplateView):

    template_name = 'djember_model/dynamic_model.js'

    def get_context_data(self, **kwargs):
        context = super(EmberModelView, self).get_context_data(**kwargs)
        try:
            model, serializer_instance, context['model_name'], context['application_name'] = \
                self.get_serializer_for_model(self.kwargs['model'])
        except ModelNotFoundException as e:
            raise Http404('No viewset found for {}'.format(e.model))


        fields, rels = self.get_fields_for_model(model, serializer_instance)

        url_name = settings.URL_NAME
        if settings.URL_NAMESPACE is not None:
            url_name = '{}:{}'.format(settings.URL_NAMESPACE, settings.URL_NAME)

        context['fields'] = fields
        context['rels'] = rels
        context['ember_app'] = settings.EMBER_APPLICATION_NAME
        return context
