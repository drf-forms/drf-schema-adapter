from django.utils.module_loading import import_string
from rest_framework.serializers import PrimaryKeyRelatedField, ManyRelatedField

from djember_model import settings


class ModelNotFoundException(Exception):

    def __init__(self, model, *args, **kwargs):
        self.model = model


class SerializerExporter:

    def __init__(self, *args, **kwargs):
        self.router = import_string(settings.ROUTER_PATH)
        super(SerializerExporter, self).__init__(*args, **kwargs)

    def get_serializer_for_model(self, model_arg):

        viewset = None
        if hasattr(self.router, '_endpoints') and model_arg in self.router._endpoints:
            endpoint = self.router._endpoints[model_arg]
            model = endpoint.model
            serializer_instance = endpoint.serializer()
            model_name = endpoint.singular_model_name
            application_name = endpoint.application_name
        else:
            for item in self.router.registry:
                if item[0] == model_arg:
                    viewset = item[1]
                    break
            if viewset is None:
                raise ModelNotFoundException(model_arg)
            model = viewset.serializer_class.Meta.model
            serializer_instance = viewset.serializer_class()
            model_name = model._meta.model_name.lower()
            application_name = model._meta.app_label.lower()

        return model, serializer_instance, model_name, application_name

    def get_fields_for_model(self, model, serializer_instance, target_app=None):

        fields = []
        rels = []

        for field_name, field in serializer_instance.get_fields().items():

            if field_name == 'id':
                continue
            field_item = {
                'name': field_name
            }
            if isinstance(field, PrimaryKeyRelatedField) or isinstance(field, ManyRelatedField):
                if isinstance(field, PrimaryKeyRelatedField):
                    field_item['type'] = 'belongsTo'
                else:
                    field_item['type'] = 'hasMany'
                model_field = model._meta.get_field_by_name(field_name)[0]
                field_item['related_model'] = model_field.related_model._meta.model_name.lower()
                field_item['app'] = target_app if target_app is not None else \
                    model_field.related_model._meta.app_label.lower()
                rels.append(field_item)
            else:
                field_item['type'] = settings.FIELD_TYPE_MAPPING[field.__class__.__name__]
                fields.append(field_item)

        return fields, rels
