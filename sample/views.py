from django.views.generic import RedirectView

from rest_framework import viewsets


class HomepageView(RedirectView):

    url = '/api/'


class AbstractHowItWorksViewSet(viewsets.ModelViewSet):

    called_counter = 0

    def get_queryset(self):
        self.__class__.called_counter += 1
        return super(AbstractHowItWorksViewSet, self).get_queryset()
