from django.conf.urls import url

from djember_model.views import EmberModelView
from djember_model import settings


urlpatterns = [
    url(r'^(?P<model>[\w\/]+)\.js', EmberModelView.as_view(), name=settings.URL_NAME),
]
