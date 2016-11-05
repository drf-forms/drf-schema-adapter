from rest_framework import serializers

from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'category',
            'price',
            'is_available',
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'products',
        )
