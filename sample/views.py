from django.views.generic import RedirectView

from rest_framework import viewsets

from sample.models import Product
from sample.serializers import ProductSerializer


class HomepageView(RedirectView):

    url = '/api/'


class AbstractHowItWorksViewSet(viewsets.ModelViewSet):

    called_counter = 0

    def get_queryset(self):
        self.__class__.called_counter += 1
        return super(AbstractHowItWorksViewSet, self).get_queryset()


class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
