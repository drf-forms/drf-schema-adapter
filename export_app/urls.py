from django.conf.urls import url

from export_app import settings
from export_app.views import EmberModelView


urlpatterns = [
    url(r'^(?P<model>[\w\/]+)\.js', EmberModelView.as_view(), name=settings.URL_NAME),
]
