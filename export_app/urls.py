from django.conf.urls import url

from export_app import settings
from export_app.views import EmberModelView, WizardModelView


urlpatterns = [
    url(r'^wizard/(?P<model>[\w\/_-]+)\.js', WizardModelView.as_view(), name='{}-wizard'.format(
        settings.URL_NAME
    )),
    url(r'^(?P<model>[\w\/_-]+)\.js', EmberModelView.as_view(), name=settings.URL_NAME),
]
