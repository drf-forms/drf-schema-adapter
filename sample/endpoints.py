from drf_auto_endpoint.endpoints import Endpoint
from .models import Product


class ProductEndpoint(Endpoint):
    model = Product
    field_annotation = {}
