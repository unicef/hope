import base64
import os
import random
import shutil
import time
from functools import reduce
from io import BytesIO
from typing import TYPE_CHECKING, Any, Iterable, Optional

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory

import factory
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.program import ProgramFactory
from graphene.test import Client
from snapshottest.django import TestCase as SnapshotTestTestCase

from hct_mis_api.apps.account.models import AdminAreaLimitedTo, Role, RoleAssignment
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_CHOICE, DocumentType

if TYPE_CHECKING:  # pragma: no_cover
    from hct_mis_api.apps.account.models import Partner, User
    from hct_mis_api.apps.core.models import BusinessArea
    from hct_mis_api.apps.geo.models import Area
    from hct_mis_api.apps.program.models import Program


class APITestCase(SnapshotTestTestCase):
    def setUp(self) -> None:
        from hct_mis_api.schema import schema

        ContentType.objects.clear_cache()
        super().setUp()
        self.client: Client = Client(schema)

        seed_in_env = os.getenv("RANDOM_SEED")
        self.seed = seed_in_env if seed_in_env not in [None, ""] else random.randint(0, 100000)
        faker = factory.faker.Faker._get_faker()
        faker.random.seed(seed_in_env)
        random.seed(self.seed)
        self.maxDiff = None

        self.start_time = time.time()

        PartnerFactory(name="UNICEF")

    def tearDown(self) -> None:
        with open(f"{settings.PROJECT_ROOT}/../test_times.txt", "a") as f:
            f.write(f"{time.time() - self.start_time:.3f} {self.id()}" + os.linesep)
        super().tearDown()

    def snapshot_graphql_request(
        self, request_string: str, context: dict | None = None, variables: dict | None = None
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

    def graphql_request(self, request_string: str, context: dict | None = None, variables: dict | None = None) -> dict:
        if context is None:
            context = {}

        return self.client.execute(
            request_string,
            variables=variables,
            context=self.generate_context(**context),
        )

    def generate_context(
        self, user: Optional["User"] = None, files: dict | None = None, headers: dict[str, str] | None = None
    ) -> WSGIRequest:
        request = RequestFactory()
        prepared_headers: dict = reduce(
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
    def __set_context_files(context: Any, files: dict) -> None:
        if isinstance(files, dict):
            for name, file in files.items():
                context.FILES[name] = file

    @staticmethod
    def set_admin_area_limits_in_program(
        partner: "Partner",
        program: "Program",
        areas: list["Area"],
    ) -> None:
        admin_area_limits, _ = AdminAreaLimitedTo.objects.get_or_create(
            program=program,
            partner=partner,
        )
        admin_area_limits.areas.set(areas)

    @classmethod
    def create_partner_role_with_permissions(
        cls,
        partner: "Partner",
        permissions: Iterable,
        business_area: "BusinessArea",
        program: Optional["Program"] = None,
        areas: list["Area"] | None = None,
        name: str | None = None,
        whole_business_area_access: bool | None = False,
    ) -> RoleAssignment:
        """
        whole_business_area_access: If True, the role is created for all programs in a business area (program=None).
        """
        permission_list = [perm.value for perm in permissions]
        name = name or f"Partner Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for Partner Role")
        partner.allowed_business_areas.add(business_area)
        role_assignment, _ = RoleAssignment.objects.get_or_create(
            partner=partner, role=role, business_area=business_area, program=program
        )
        # set admin area limits in program
        if program and areas:
            cls.set_admin_area_limits_in_program(partner, program, areas)
        return role_assignment

    @classmethod
    def create_user_role_with_permissions(
        cls,
        user: "User",
        permissions: Iterable,
        business_area: "BusinessArea",
        program: Optional["Program"] = None,
        areas: list["Area"] | None = None,
        name: str | None = None,
        whole_business_area_access: bool | None = False,
    ) -> RoleAssignment:
        """
        whole_business_area_access: If True, the role is created for all programs in a business area (program=None).
        """
        permission_list = [perm.value for perm in permissions]
        name = name or f"User Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for User Role")
        role_assignment, _ = RoleAssignment.objects.get_or_create(
            user=user, role=role, business_area=business_area, program=program
        )

        # set admin area limits in program
        if program and areas:
            cls.set_admin_area_limits_in_program(user.partner, program, areas)
        return role_assignment


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
