from six import iteritems

from django.core.urlresolvers import reverse

from rest_framework import status

from .factories import get_admin


class BaseAPITestCase(object):
    model_factory_class = None
    model = None
    factory_default_kwargs = {}
    factory_delete_kwargs = {}
    api_base_name = None
    api_base_url = ''

    list_requires_login = False
    detail_requires_login = False
    create_requires_login = True
    update_requires_login = True
    delete_requires_login = True

    to_update_fieds = {}
    extra_update_fields = {}
    create_kwargs = {}
    extra_create_fields = {}
    create_strip_data_fields = ['id', ]
    create_strip_response_fields = ['id', ]

    serializer_class = None
    create_serializer_class = None
    update_serializer_class = None

    api_is_read_only = False

    @classmethod
    def setUpTestData(cls):
        cls.test_model = cls.model_factory_class(
            **cls.factory_default_kwargs
        )
        cls.test_model.save()
        cls.admin = get_admin()

    def tearDown(self):
        self.client.logout()

    def login(self, user=None):
        if user is None:
            user = self.admin

        self.client.force_authenticate(user)

    def get_list_url(self):
        if self.api_base_name is None:
            return self.api_base_url

        return reverse('{}-list'.format(self.api_base_name))

    def get_detail_url(self, record=None):
        if record is None:
            record = self.test_model

        if self.api_base_name is None:
            return '{}{}/'.format(
                 self.api_base_url,
                 self.test_model.pk
            )

        return reverse(
            '{}-detail'.format(self.api_base_name),
            kwargs={'pk': record.pk, }
        )

    def test_list_view(self):
        url = self.get_list_url()
        response = self.client.get(url, format='json')

        if self.list_requires_login:
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
            self.login()
            response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_view(self):
        url = self.get_detail_url()
        response = self.client.get(url, format='json')

        if self.detail_requires_login:
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
            self.login()
            response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_view(self):
        if self.api_is_read_only:
            self.assertTrue(True)
        else:
            url = self.get_detail_url()

            record = self.model.objects.get(
                pk=self.test_model.pk
            )

            for field, value in iteritems(self.to_update_fieds):
                setattr(record, field, value)
            if self.update_serializer_class is not None:
                serializer = self.update_serializer_class(record)
            else:
                serializer = self.serializer_class(record)

            data = serializer.data

            for field, value in iteritems(self.extra_update_fields):
                data[field] = value

            response = self.client.put(url, data, format='json')

            if self.update_requires_login:
                self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
                self.login()
                response = self.client.put(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_view(self):
        if self.api_is_read_only:
            self.assertTrue(True)
        else:
            to_delete = self.model_factory_class(**self.factory_delete_kwargs)
            to_delete.save()

            url = self.get_detail_url(to_delete)
            response = self.client.delete(url, format='json')

            if self.delete_requires_login:
                self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
                self.login()
                response = self.client.delete(url, format='json')

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_view(self):
        if self.api_is_read_only:
            self.assertTrue(True)
        else:
            url = self.get_list_url()

            dummy = self.model_factory_class.simple_generate(
                create=False,
                **self.create_kwargs
            )

            foreign_keys = [field.name for field in self.serializer_class.Meta.model._meta.get_fields()
                                         if field.one_to_one or (field.many_to_one and field.related_model)]

            if self.create_serializer_class is not None:
                serializer = self.create_serializer_class(dummy)
            else:
                serializer = self.serializer_class(dummy)

            data = serializer.data

            for field in foreign_keys:
                related = getattr(dummy, field, None)
                if related is not None:
                        related.save()
                        data[field] = related.id

            for field, value in iteritems(self.extra_create_fields):
                data[field] = value

            response = self.client.post(url, data, format='json')

            if self.create_requires_login:
                self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
                self.login()
                response = self.client.post(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

            response_data = response.data
            for field in self.create_strip_response_fields:
                response_data.pop(field, None)
            for field in self.create_strip_data_fields:
                data.pop(field, None)

            self.assertEqual(response_data, data)


class EndpointAPITestCase(BaseAPITestCase):

    api_url_prefix = '/api/'

    def __init__(self, *args, **kwargs):
        from urls import router
        self.api_base_url =  '{}{}/'.format(self.api_url_prefix, self.endpoint_url)
        self.endpoint = router.get_endpoint(self.endpoint_url)
        self.model = self.endpoint.model
        self.serializer_class = self.endpoint.get_serializer()
        self.api_is_read_only = self.endpoint.read_only

        super(EndpointAPITestCase, self).__init__(*args, **kwargs)
