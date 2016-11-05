from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers

from djember_model import urls as djember_urls, settings as djember_settings

from sample.views import ProductViewSet, CategoryViewSet


router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('sample/categories', CategoryViewSet)

urlpatterns = [
    # Examples:
    # url(r'^$', 'djember_model.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^models/', include(djember_urls, namespace=djember_settings.URL_NAMESPACE)),
    url(r'^api/', include(router.urls)),
]
