from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from drf_auto_endpoint.decorators import bulk_action, custom_action, wizard
from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router, register

from .models import Product, Category, HowItWorks
from .serializers import AddSerializer, RequestAwareCategorySerializer
from .views import AbstractHowItWorksViewSet, ProductViewSet


@register
class ProductEndpoint(Endpoint):
    model = Product
    fields_annotation = {
        'name': {'placeholder': 'Enter your name here'}
    }
    viewset = ProductViewSet


@register
class HowItWorksEndpoint(Endpoint):
    model = HowItWorks
    base_viewset = AbstractHowItWorksViewSet

    @custom_action(method='POST')
    def increment(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.count += 1
        obj.save()
        return Response(self.get_serializer(obj).data)

    @bulk_action(method='POST')
    def decrement(self, request):
        for obj in self.model.objects.all():
            obj.count = max(0, obj.count - 1)
            obj.save()
        return Response(status=204)

    @wizard(AddSerializer, method='POST')
    def add(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        obj.count += request.validated_data['amount']
        obj.save()
        return Response(self.get_serializer(obj).data)


router.register(Category)


@register
class RequestAwareCategoryEndpoint(Endpoint):
    model = Category
    serializer = RequestAwareCategorySerializer

    def get_url(self):
        return 'sample/request_aware_categories'

    def get_serializer_instance(self, request):
        return self.get_serializer()(context={'request': request})
