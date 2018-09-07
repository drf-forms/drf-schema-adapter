from django.core.exceptions import FieldDoesNotExist
from django.utils.module_loading import import_string

from rest_framework.serializers import (PrimaryKeyRelatedField, ManyRelatedField, ModelSerializer,
                                        ListSerializer, SlugRelatedField)

from export_app import settings


class ModelNotFoundException(Exception):

    def __init__(self, model, *args, **kwargs):
        self.model = model


class BaseSerializerExporter(object):
    """
    Returns the minimum info we need about a model
    """

    def __init__(self, *args, **kwargs):
        self.router = import_string(settings.ROUTER_PATH)
        super(BaseSerializerExporter, self).__init__(*args, **kwargs)

    def get_endpoint_for_basename(self, basename):
        if hasattr(self.router, '_endpoints') and basename in self.router._endpoints:
            return self.router._endpoints[basename]
        return None

    def get_viewset_for_basename(self, basename, with_endpoint=False, dasherize=True):
        if dasherize:
            basename = basename.replace('_', '-')
        viewset = None
        endpoint = self.get_endpoint_for_basename(basename)
        if endpoint is not None:
            model_name = endpoint.singular_model_name
            application_name = endpoint.application_name
            viewset = endpoint.viewset
        else:
            for item in self.router.registry:
                if item[0] == basename:
                    viewset = item[1]
                    break
            if viewset is None:
                raise ModelNotFoundException(basename)

            model = viewset.serializer_class.Meta.model
            model_name = model._meta.model_name.lower()
            application_name = model._meta.app_label.lower()

        if with_endpoint:
            return viewset, model_name, application_name, endpoint
        return viewset, model_name, application_name

    def get_serializer_for_basename(self, basename):
        viewset, model_name, application_name, endpoint = \
            self.get_viewset_for_basename(basename, True)

        if endpoint is not None:
            model = endpoint.model
            serializer_instance = endpoint.serializer()
        else:
            model = viewset.serializer_class.Meta.model
            serializer_instance = viewset.serializer_class()

        return model, serializer_instance, model_name, application_name

    def get_fields_for_model(self, model, serializer_instance, adapter, target_app=None, endpoint=None):
        return [], []


class SerializerExporterWithFields(BaseSerializerExporter):

    def _extract_field_info(self, model, field_name, field, fields, relationships, adapter, target_app,
                            allow_recursion=False, relationship_as_attribute=False):
        if field_name == 'id':
            return None
        field_item = {
            'name': field_name,
            'type': adapter.field_type_mapping[field.__class__.__name__]
        }
        if not relationship_as_attribute and (isinstance(field, PrimaryKeyRelatedField) or
                                              isinstance(field, SlugRelatedField) or
                                              isinstance(field, ManyRelatedField) or
                                              isinstance(field, ModelSerializer)):

            model_field = None
            if model is not None:
                try:
                    model_field = model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    pass

            if model_field is None:
                if isinstance(field, PrimaryKeyRelatedField) or isinstance(field, SlugRelatedField):
                    queryset = field.queryset
                else:
                    queryset = field._kwargs['child_relation'].queryset

                if queryset is not None:
                    field_item['related_model'] = queryset.model._meta.model_name.lower()
                    field_item['app'] = target_app if target_app is not None else \
                        queryset.model._meta.app_label.lower()
                    relationships.append(field_item)
                else:
                    field_item['type'] = 'CharField'
            else:
                field_item['related_model'] = model_field.related_model._meta.model_name.lower()
                field_item['app'] = target_app if target_app is not None else \
                    model_field.related_model._meta.app_label.lower()
                relationships.append(field_item)
                if hasattr(model_field, 'field'):
                    field_item['inverse'] = model_field.field.name
                elif hasattr(model_field, 'remote_field') and \
                        getattr(model_field.remote_field, 'related_name', None) is not None:
                    field_item['inverse'] = model_field.remote_field.related_name
                if field_item.get('inverse', '-')[-1] == '+':
                    field_item.pop('inverse')
            if isinstance(field, ModelSerializer):
                if hasattr(field, 'many') and field.many:
                    field_item['type'] = adapter.field_type_mapping['ManyRelatedField']
                else:
                    field_item['type'] = adapter.field_type_mapping['PrimaryKeyRelatedField']
        elif isinstance(field, ModelSerializer):
            field_item['related_model'] = field.queryset.model._meta.model_name.lower()
            field_item['app'] = target_app if target_app is not None else \
                field.queryset.model._meta.app_label.lower()
            relationships.append(field_item)
            if field.many:
                field_item['type'] = adapter.field_type_mapping['ManyRelatedField']
            else:
                field_item['type'] = adapter.field_type_mapping['PrimaryKeyRelatedField']
        elif isinstance(field, ListSerializer):
            child_rels = []
            child_fields = []
            self._extract_field_info(model, field_name, field.child, child_fields, child_rels, adapter, target_app)
            if len(child_rels) > 0:
                for item in child_rels:
                    item['type'] = adapter.field_type_mapping['ManyRelatedField']
                    item.pop('inverse', None)
                    relationships.append(item)
            else:
                field_item['type'] = adapter.field_type_mapping['ListField']
                fields.append(field_item)

        else:
            if relationship_as_attribute:
                field_item['type'] = adapter.field_type_mapping[None]
            fields.append(field_item)

        return field_item

    def get_fields_for_model(self, model, serializer_instance, adapter, target_app=None, endpoint=None):

        fields = []
        relationships = []

        for field_name, field in serializer_instance.get_fields().items():
            relationship_as_attribute = False
            if endpoint is not None:
                if getattr(endpoint, 'foreign_key_as_list', False):
                    if endpoint.foreign_key_as_list is True:
                        relationship_as_attribute = True
                    else:
                        relationship_as_attribute = field_name in endpoint.foreign_key_as_list
            self._extract_field_info(model, field_name, field, fields, relationships, adapter, target_app, True,
                                     relationship_as_attribute=relationship_as_attribute)

        return adapter.adapt_fields_for_model(fields, relationships)
