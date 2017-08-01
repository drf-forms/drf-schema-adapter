from rest_framework import viewsets, serializers

from ..models import Product


class DummyProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')


class DummyProductViewSet(viewsets.ModelViewSet):

    serializer_class = DummyProductSerializer
    queryset = Product.objects.all()
    filter_fields = ['name', ]
    search_fields = ['name', ]


class DummyProductSerializerWithField(serializers.ModelSerializer):

    name = serializers.CharField(read_only=True)
