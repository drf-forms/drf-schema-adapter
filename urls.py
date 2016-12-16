from django.conf.urls import include, url
from django.contrib import admin

from drf_auto_endpoint.router import router

from sample.endpoints import ProductEndpoint
from sample.models import Category, HowItWorks
from sample.views import AbstractHowItWorksViewSet, HomepageView, ProductViewSet
from export_app import urls as export_urls, settings as export_settings


router.register(endpoint=ProductEndpoint(), viewset=ProductViewSet)
router.register(Category)
router.register(HowItWorks, base_viewset=AbstractHowItWorksViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomepageView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^models/', include(export_urls, namespace=export_settings.URL_NAMESPACE)),
]
