from django.conf.urls import include, url
from django.contrib import admin

from drf_auto_endpoint.router import router

from sample.views import HomepageView
from export_app import urls as export_urls, settings as export_settings


urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomepageView.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^models/', include(export_urls, namespace=export_settings.URL_NAMESPACE)),
]
