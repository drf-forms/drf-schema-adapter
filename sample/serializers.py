from django.db.models.fields import NOT_PROVIDED

from rest_framework import serializers

from sample.models import Product


class SampleSerializer(serializers.ModelSerializer):
    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super(SampleSerializer, self).build_standard_field(field_name, model_field)
        if model_field.default is not NOT_PROVIDED:
            field_kwargs['default'] = model_field.default
        return field_class, field_kwargs


class ProductSerializer(SampleSerializer):
    class Meta:
        model = Product
        fields = ('name', 'category', 'product_type', )


class AddSerializer(serializers.Serializer):

    amount = serializers.IntegerField()

    class Meta:
        fields = ('amount', )
