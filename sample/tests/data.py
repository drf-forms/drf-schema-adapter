from rest_framework import viewsets, serializers

from ..models import Product


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
