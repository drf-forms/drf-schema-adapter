from django.conf.urls import include, url
from django.contrib import admin

from drf_auto_endpoint.router import router
from sample.views import HomepageView, ProductViewSet

from sample.models import Product

router.register(Product, viewset=ProductViewSet)

urlpatterns = [
    # Examples:
    # url(r'^$', 'drf_auto_endpoint.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomepageView.as_view()),
    url(r'^api/', include(router.urls)),
]
