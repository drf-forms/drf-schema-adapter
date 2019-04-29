from django.db.models.fields import NOT_PROVIDED

from rest_framework import serializers

from sample.models import Product, Category


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


class RequestAwareCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        field_names = super().get_field_names(*args, **kwargs)

        # Joe is banned from seeing category names. Poor Joe.
        if self.context['request'].META.get('USERNAME') == 'Joe':
            field_names.remove('name')

        return field_names
