import base64
import os
import random
import shutil
import sys
import time
from functools import reduce
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory, TestCase

import factory
from elasticsearch_dsl import connections
from graphene.test import Client
from snapshottest.django import TestCase as SnapshotTestTestCase

from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_CHOICE, DocumentType
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.core.models import BusinessArea


class APITestCase(SnapshotTestTestCase):
    def setUp(self) -> None:
        from hct_mis_api.schema import schema

        super().setUp()
        self.client: Client = Client(schema)

        seed_in_env = os.getenv("RANDOM_SEED")
        self.seed = seed_in_env if seed_in_env not in [None, ""] else random.randint(0, 100000)
        faker = factory.faker.Faker._get_faker()
        faker.random.seed(seed_in_env)
        random.seed(self.seed)
        self.maxDiff = None

        self.start_time = time.time()

    def tearDown(self) -> None:
        with open(f"{settings.PROJECT_ROOT}/../test_times.txt", "a") as f:
            f.write(f"{time.time() - self.start_time:.3f} {self.id()}" + os.linesep)

        # https://stackoverflow.com/a/39606065
        if hasattr(self._outcome, "errors"):
            # Python 3.4 - 3.10  (These two methods have no side effects)
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
        else:
            # Python 3.11+
            result = self._outcome.result

        for typ, errors in (("ERROR", result.errors), ("FAIL", result.failures)):
            for test, text in errors:
                if test is self:
                    msg = [x for x in text.split("\n")[1:] if not x.startswith(" ")][0]
                    print(f"Seed: {self.seed}", file=sys.stderr)
                    print("%s: %s\n%s" % (typ, self.id(), msg), file=sys.stderr)

    def snapshot_graphql_request(
        self, request_string: str, context: Optional[Dict] = None, variables: Optional[Dict] = None
    ) -> None:
        if context is None:
            context = {}

        self.assertMatchSnapshot(
            self.client.execute(
                request_string,
                variables=variables,
                context=self.generate_context(**context),
            )
        )

    def graphql_request(
        self, request_string: str, context: Optional[Dict] = None, variables: Optional[Dict] = None
    ) -> Dict:
        if context is None:
            context = {}

        return self.client.execute(
            request_string,
            variables=variables,
            context=self.generate_context(**context),
        )

    def generate_context(
        self, user: Optional["User"] = None, files: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None
    ) -> WSGIRequest:
        request = RequestFactory()
        prepared_headers: Dict = reduce(
            lambda prev_headers, curr_header: {**prev_headers, f"HTTP_{curr_header[0]}": curr_header[1]},
            (headers or {}).items(),
            {},
        )
        context_value = request.get("/api/graphql/", **prepared_headers)
        context_value.user = user or AnonymousUser()
        self.__set_context_files(context_value, files or {})
        return context_value

    @classmethod
    def generate_document_types_for_all_countries(cls) -> None:
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))

        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

    @staticmethod
    def id_to_base64(object_id: str, name: str) -> str:
        return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()

    @staticmethod
    def __set_context_files(context: Any, files: Dict) -> None:
        if isinstance(files, dict):
            for name, file in files.items():
                context.FILES[name] = file

    @staticmethod
    def create_user_role_with_permissions(
        user: "User", permissions: Iterable, business_area: "BusinessArea"
    ) -> UserRole:
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(
            name="Role with Permissions", defaults={"permissions": permission_list}
        )
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)
        return user_role


class BaseElasticSearchTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        connections.create_connection(hosts=["elasticsearch:9200"], timeout=20)
        cls.rebuild_search_index()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    @classmethod
    def rebuild_search_index(cls) -> None:
        rebuild_search_index()


class UploadDocumentsBase(APITestCase):
    TEST_DIR = "test_data"

    @staticmethod
    def create_fixture_file(name: str, size: int, content_type: str) -> InMemoryUploadedFile:
        return InMemoryUploadedFile(
            name=name, file=BytesIO(b"xxxxxxxxxxx"), charset=None, field_name="0", size=size, content_type=content_type
        )

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(cls.TEST_DIR)
        except OSError:
            pass
        super().tearDownClass()
