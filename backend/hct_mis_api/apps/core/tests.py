import base64

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from graphene.test import Client
from snapshottest.django import TestCase

from hct_mis_api.schema import schema


class APITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client(schema)

    def snapshot_graphql_request(
            self,
            request_string,
            context=None,
            variables=None
    ):
        if context is None:
            context = {}

        graphql_request = self.client.execute(
            request_string,
            variables=variables,
            context=self.generate_context(**context)
        )

        self.assertMatchSnapshot(graphql_request)

    def generate_context(self, user=None, files=None):
        request = RequestFactory()
        context_value = request.get('/api/graphql/')
        context_value.user = user or AnonymousUser()
        self.__set_context_files(context_value, files)
        return context_value

    @staticmethod
    def id_to_base64(node_id, node_name):
        return base64.b64encode(
            f'{node_name.capitalize()}Node:{str(node_id)}'.encode('utf-8')
        ).decode()

    @staticmethod
    def __set_context_files(context, files):
        if isinstance(files, dict):
            for name, file in files.items():
                context.FILES[name] = file
