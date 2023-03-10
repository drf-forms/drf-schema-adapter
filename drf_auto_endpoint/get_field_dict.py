from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import NOT_PROVIDED
from django.utils.module_loading import import_string

from rest_framework import serializers, relations
from rest_framework.fields import empty, ChoiceField

from inflector import Inflector

from .app_settings import settings


inflector_language = import_string(settings.INFLECTOR_LANGUAGE)
inflector = Inflector(inflector_language)


class GetFieldDict():

    def __call__(self, *args, **kwargs):
        return self.dict_for_field(*args, **kwargs)

    def get_validation_attrs(self, instance_field):
        rv = {}

        attrs_to_validation = {
            'min_length': 'min',
            'max_length': 'max',
            'min_value': 'min',
            'max_value': 'max'
        }
        for attr_name, validation_name in attrs_to_validation.items():
            if getattr(instance_field, attr_name, None) is not None:
                rv[validation_name] = getattr(instance_field, attr_name)

        return rv

    def get_read_only(self, name, field_instance):
        if name == '__str__':
            return True

        if field_instance.read_only and not isinstance(field_instance, serializers.ManyRelatedField):
            return True

        return False

    def get_write_only(self, name, field_instance):
        if field_instance.write_only and not isinstance(field_instance, serializers.ManyRelatedField):
            return True

        return False

    def get_base_dict_for_field(self, name, field_instance, translated_fields, serializer_instance):

        read_only = self.get_read_only(name, field_instance)
        write_only = self.get_write_only(name, field_instance)

        return {
            'key': name,
            'type': settings.WIDGET_MAPPING[field_instance.__class__.__name__],
            'read_only': read_only,
            'write_only': write_only,
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

    def update_annotations(self, rv, name, field_instance, fields_annotation):

        if fields_annotation and name in fields_annotation:
            if 'placeholder' in fields_annotation[name]:
                rv['ui']['placeholder'] = fields_annotation[name]['placeholder']
            if 'help' in fields_annotation[name]:
                rv['ui']['help'] = fields_annotation[name]['help']
        if field_instance.help_text is not None and 'help' not in rv['ui']:
            rv['ui']['help'] = field_instance.help_text

    def get_model_field(self, field_instance, model):
        if model is None:
            return None
        try:
            return model._meta.get_field(field_instance.source)
        except FieldDoesNotExist:
            return None

    def update_default_from_model(self, rv, model_field):
        if model_field is None:
            return
        if hasattr(model_field, 'default') and model_field.default != NOT_PROVIDED:
            rv['default'] = model_field.default

    def update_default_from_serializer(self, rv, field_instance):
        if field_instance.default == empty:
            return
        rv['default'] = field_instance.default

    def normalize_default(self, rv, field_instance):
        if 'default' in rv:
            if callable(rv['default']):
                rv['default'] = rv['default']()

        # TODO: handle relationships

    def update_label(self, rv, model_field):
        if model_field is None:
            return

        try:
            rv['ui']['label'] = model_field.verbose_name
        except AttributeError:
            rv['ui']['label'] = model_field.name

    def update_extra(self, rv, field):
        if not isinstance(field, dict):
            return

        extra = rv['extra']
        extra.update(field.get('extra', {}))
        rv.update(field)
        rv['extra'] = extra

    def update_related_endpoint(self, rv, related_model):
        rv['related_endpoint'] = {
            'app': related_model._meta.app_label,
            'singular': related_model._meta.model_name.lower(),
            'plural': inflector.pluralize(related_model._meta.model_name.lower())
        }

    def set_choices_from_qs(self, rv, qs, key_attr='id'):
        rv['type'] = settings.WIDGET_MAPPING['choice']

        rv['choices'] = [
            {
                'label': record.__str__(),
                'value': getattr(record, key_attr)
            } for record in qs.all()
        ]

    def update_realtionship_from_model(self, rv, model_field, foreign_key_as_list):
        if model_field is None:
            return

        related_model = getattr(model_field, 'related_model', None)
        if related_model is None:
            return

        if model_field.__class__.__name__ == 'ManyToManyRel':
            rv['validation']['required'] = False

        if not foreign_key_as_list:
            rv['type'] = settings.WIDGET_MAPPING[model_field.__class__.__name__]
            self.update_related_endpoint(rv, related_model)
        else:
            # FIXME: we may not need this code as the serializer field has a 'choices' attribute
            qs = related_model.objects

            key_attr = 'pk'
            if hasattr(model_field, 'to_fields') and model_field.to_fields is not None \
                    and len(model_field.to_fields) > 0:
                key_attr = model_field.to_fields[0]

            self.set_choices_from_qs(rv, qs, key_attr)

    def update_relationship_from_serializer(self, rv, field_instance, foreign_key_as_list):
        if not isinstance(field_instance, (relations.PrimaryKeyRelatedField, relations.ManyRelatedField,
                                           relations.SlugRelatedField)):
            return

        if not hasattr(field_instance, 'queryset') or field_instance.queryset is None:
            return

        related_model = field_instance.queryset.model

        if not foreign_key_as_list:
            self.update_related_endpoint(rv, related_model)
        else:
            if not hasattr(field_instance, 'queryset') or field_instance.queryset is None:
                return
            # FIXME: we may not need this code as the serializer field has a 'choices' attribute
            self.set_choices_from_qs(rv, field_instance.queryset)

    def update_choices_from_serializer(self, rv, field_instance, force=False):
        if not isinstance(field_instance, ChoiceField) and force is False:
            return

        if not hasattr(field_instance, 'choices'):
            return

        if rv.get('related_endpoint', None) is not None and force is False:
            return

        rv['type'] = settings.WIDGET_MAPPING['choice']
        rv['choices'] = [
            {
                'label': v,
                'value': k,
            } for k, v in field_instance.choices.items()
        ]

    def dict_for_field(self, field, serializer_instance, translated_fields=None, fields_annotation=False,
                       model=None, foreign_key_as_list=False):
        if translated_fields is None:
            translated_fields = []

        name = field['name'] if isinstance(field, dict) else field
        try:
            field_instance = serializer_instance.fields[name]
        except KeyError:
            return {'key': name}

        model_field = self.get_model_field(field_instance, model)

        rv = self.get_base_dict_for_field(name, field_instance, translated_fields, serializer_instance)
        self.update_annotations(rv, name, field_instance, fields_annotation)

        self.update_default_from_model(rv, model_field)
        self.update_default_from_serializer(rv, field_instance)
        self.normalize_default(rv, field_instance)

        self.update_label(rv, model_field)

        self.update_realtionship_from_model(rv, model_field, foreign_key_as_list)
        self.update_relationship_from_serializer(rv, field_instance, foreign_key_as_list)

        self.update_choices_from_serializer(rv, field_instance)

        rv['validation'].update(self.get_validation_attrs(field_instance))

        self.update_extra(rv, field)
        return rv


get_field_dict = GetFieldDict()
