from rest_framework import viewsets, serializers
from django_filters.rest_framework import FilterSet

from ..models import Product, ProductChoice


class DummyProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')


class AllFieldDummyProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class DummyProductViewSet(viewsets.ModelViewSet):

    serializer_class = DummyProductSerializer
    queryset = Product.objects.all()
    filter_fields = ['name', ]
    search_fields = ['name', ]


class DummyProductSerializerWithField(serializers.ModelSerializer):

    name = serializers.CharField(read_only=True)


class DummyProductSerializerWithAllFields(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class DummyChoicesSerializer(serializers.Serializer):

    simple = serializers.ChoiceField(choices=tuple((x, x) for x in 'abcdef'))
    multiple = serializers.MultipleChoiceField(choices=tuple((x, x) for x in 'abcdef'))


class ProductChoiceSerializer(serializers.ModelSerializer):

    products = serializers.MultipleChoiceField(choices=tuple(Product.objects.all().values_list('id', 'name')))

    class Meta:
        model = ProductChoice
        fields = '__all__'


class ProductFilterSet(FilterSet):

    class Meta:
        model = Product
        fields = ['category_id']
