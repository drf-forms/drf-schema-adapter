import logging
import os

from django.conf import settings as django_settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.module_loading import import_string

from export_app import settings


class Command(BaseCommand):

    help = '''
Re-export already exported ember models
    '''

    logger = logging.getLogger('intranet')

    def handle(self, *args, **options):
        router = import_string(settings.ROUTER_PATH)
        endpoints = getattr(router, '_endpoints', {}).items()

        for endpoint, endpoint_instance in endpoints:
            model_name = endpoint_instance.singular_model_name
            application_name = endpoint_instance.application_name

            target = os.path.join(
                django_settings.BASE_DIR,
                settings.FRONT_APPLICATION_PATH,
                'app',
                'models',
                application_name.replace('_', '-'),
                '{}.js'.format(model_name).replace('_', '-')
            )

            if os.path.exists(target):
                call_command('export', endpoint, noinput=True)
