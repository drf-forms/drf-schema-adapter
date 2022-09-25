from django.urls import re_path
from export_app import settings
from export_app.views import EmberModelView, WizardModelView


urlpatterns = [
    re_path(r'^wizard/(?P<model>[\w\/_-]+)\.js', WizardModelView.as_view(), name='{}-wizard'.format(
        settings.URL_NAME
    )),
    re_path(r'^(?P<model>[\w\/_-]+)\.js', EmberModelView.as_view(), name=settings.URL_NAME),
]
