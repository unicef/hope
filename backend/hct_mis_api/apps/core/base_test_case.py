import base64

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from django_countries.data import COUNTRIES
from elasticsearch_dsl import connections
from graphene.test import Client
from snapshottest.django import TestCase as SnapshotTestTestCase

from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.household.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_CHOICE, DocumentType


class APITestCase(SnapshotTestTestCase):
    def setUp(self):
        from hct_mis_api.schema import schema

        super().setUp()
        self.client = Client(schema)

    def snapshot_graphql_request(self, request_string, context=None, variables=None):
        if context is None:
            context = {}

        graphql_request = self.client.execute(
            request_string,
            variables=variables,
            context=self.generate_context(**context),
        )

        self.assertMatchSnapshot(graphql_request)

    def graphql_request(self, request_string, context=None, variables=None):
        if context is None:
            context = {}

        return self.client.execute(
            request_string,
            variables=variables,
            context=self.generate_context(**context),
        )

    def generate_context(self, user=None, files=None):
        request = RequestFactory()
        context_value = request.get("/api/graphql/")
        context_value.user = user or AnonymousUser()
        self.__set_context_files(context_value, files)
        return context_value

    @classmethod
    def generate_document_types_for_all_countries(cls):
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for alpha2 in COUNTRIES:
            for doc_type, label in identification_type_choice:
                document_types.append(DocumentType(country=alpha2, label=label, type=doc_type))

        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

    @staticmethod
    def id_to_base64(object_id, name):
        return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()

    @staticmethod
    def __set_context_files(context, files):
        if isinstance(files, dict):
            for name, file in files.items():
                context.FILES[name] = file

    @staticmethod
    def create_user_role_with_permissions(user, permissions, business_area):
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(
            name="Role with Permissions", defaults={"permissions": permission_list}
        )
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)
        return user_role


class BaseElasticSearchTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        connections.create_connection(hosts=["elasticsearch:9200"], timeout=20)
        cls.rebuild_search_index()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    @classmethod
    def rebuild_search_index(cls):
        rebuild_search_index()
