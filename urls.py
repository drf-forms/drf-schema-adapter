from django.urls import include, path

from drf_auto_endpoint.router import router

from sample.views import HomepageView
from export_app import settings as export_settings


urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    path('api/', include(router.urls)),
    path('models/', include('export_app.urls', namespace=export_settings.URL_NAMESPACE)),
    path('', HomepageView.as_view()),
]
