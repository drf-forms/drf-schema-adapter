from drf_auto_endpoint.endpoints import Endpoint
from drf_auto_endpoint.router import router, register

from .models import Product, Category, HowItWorks
from .views import AbstractHowItWorksViewSet, ProductViewSet


@register
class ProductEndpoint(Endpoint):
    model = Product
    fields_annotation = {
        'name': {'placeholder': 'Enter your name here'}
    }
    viewset = ProductViewSet


router.register(Category)
router.register(HowItWorks, base_viewset=AbstractHowItWorksViewSet)
