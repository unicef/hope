from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from rest_framework import status

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.contrib.aurora.caches import (
    OrganizationListVersionsKeyBit,
    ProjectListVersionsKeyBit,
    RegistrationListVersionsKeyBit,
)
from hct_mis_api.contrib.aurora.fixtures import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from hct_mis_api.contrib.aurora.models import Organization, Project, Registration
from tests.unit.api.base import HOPEApiTestCase, token_grant_permission


class ProjectListViewTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()
        self.program = ProgramFactory(
            name="Test Program 123",
        )
        self.other_program = ProgramFactory(
            name="Other program",
        )
        self.organization = OrganizationFactory(
            name="Test Organization", slug="test_organization", business_area=self.business_area, source_id=777
        )
        self.organization_2 = OrganizationFactory(
            name="Test Organization 2", slug="slug123", business_area=self.business_area, source_id=111
        )
        self.prj_1 = ProjectFactory.create(
            name="Test Project 1",
            source_id="111",
            organization=self.organization,
            programme=self.program,
        )
        self.prj_2 = ProjectFactory.create(
            name="Test Project 2",
            source_id="222",
            organization=self.organization_2,
            programme=self.other_program,
        )
        self.registration_1 = RegistrationFactory(project=self.prj_1, source_id=111, name="Reg 1")
        self.registration_2 = RegistrationFactory(project=self.prj_1, source_id=222, name="Reg 2")
        self.registration_3 = RegistrationFactory(project=self.prj_2, source_id=333, name="Reg 3")

        self.url_organization = reverse("api:organization-list")
        self.url_project = reverse("api:project-list")
        self.url_registration = reverse("api:registration-list")

    # Organization
    def test_organization_list_no_permission(self) -> None:
        response = self.client.get(self.url_organization)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_list_all(self) -> None:
        cache.clear()
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(self.url_organization)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        org = response.data["results"][0]
        self.assertEqual(org["name"], "Test Organization")
        self.assertEqual(org["hope_id"], str(self.business_area.pk))
        self.assertEqual(org["aurora_id"], 777)

        cache_key = f"{OrganizationListVersionsKeyBit.specific_view_cache_key}:{Organization.objects.latest('updated_at').updated_at}:{Organization.objects.all().count()}"
        self.assertIsNotNone(cache.get(cache_key))
        self.assertGreater(len(queries), 0)
        # second call
        with CaptureQueriesContext(connection) as queries2:
            resp_2 = self.client.get(self.url_organization)
        self.assertEqual(resp_2.status_code, 200)
        self.assertLess(len(queries2), len(queries))

    # Project
    def test_project_list_no_permission(self) -> None:
        response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_list_all(self) -> None:
        cache.clear()
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        # check first
        project = response.data["results"][0]
        self.assertEqual(project["name"], "Test Project 1")
        self.assertEqual(project["aurora_id"], 111)
        self.assertEqual(project["hope_id"], str(self.program.pk))
        self.assertEqual(project["organization"], "test_organization")

        cache_key = f"{ProjectListVersionsKeyBit.specific_view_cache_key}:{Project.objects.latest('updated_at').updated_at}:{Project.objects.all().count()}"
        self.assertIsNotNone(cache.get(cache_key))
        self.assertGreater(len(queries), 0)
        # second call
        with CaptureQueriesContext(connection) as queries2:
            resp_2 = self.client.get(self.url_project)
        self.assertEqual(resp_2.status_code, 200)
        self.assertLess(len(queries2), len(queries))

    def test_project_list_filter_by_org_slug(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_project, {"org_slug": "slug123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        project = response.data["results"][0]
        self.assertEqual(project["name"], self.prj_2.name)
        self.assertEqual(project["aurora_id"], 222)
        self.assertEqual(project["hope_id"], str(self.other_program.pk))
        self.assertEqual(project["organization"], self.organization_2.slug)

    def test_project_list_filter_by_org_pk(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_project, {"org_pk": str(self.organization_2.pk)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        project = response.data["results"][0]
        self.assertEqual(project["name"], self.prj_2.name)
        self.assertEqual(project["aurora_id"], 222)
        self.assertEqual(project["hope_id"], str(self.other_program.pk))
        self.assertEqual(project["organization"], self.organization_2.slug)

    # Registration
    def test_registration_list_no_permission(self) -> None:
        response = self.client.get(self.url_registration)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_list_all(self) -> None:
        cache.clear()
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            with CaptureQueriesContext(connection) as queries:
                response = self.client.get(self.url_registration)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

        cache_key = f"{RegistrationListVersionsKeyBit.specific_view_cache_key}:{Registration.objects.latest('updated_at').updated_at}:{Registration.objects.all().count()}"
        self.assertIsNotNone(cache.get(cache_key))
        self.assertGreater(len(queries), 0)
        # second call
        with CaptureQueriesContext(connection) as queries2:
            resp_2 = self.client.get(self.url_registration)
        self.assertEqual(resp_2.status_code, 200)
        self.assertLess(len(queries2), len(queries))

    def test_registration_list_filter_by_org_slug(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_registration, {"org_slug": "slug123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        reg = response.data["results"][0]
        self.assertEqual(reg["name"], self.registration_3.name)
        self.assertEqual(reg["aurora_id"], self.registration_3.source_id)
        self.assertEqual(reg["project"], str(self.prj_2.pk))
        self.assertEqual(reg["organization"], "slug123")

    def test_registration_list_filter_by_org_pk(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_registration, {"org_pk": str(self.organization_2.pk)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        reg = response.data["results"][0]
        self.assertEqual(reg["name"], self.registration_3.name)
        self.assertEqual(reg["aurora_id"], self.registration_3.source_id)
        self.assertEqual(reg["project"], str(self.prj_2.pk))
        self.assertEqual(reg["organization"], self.organization_2.slug)

    def test_registration_list_filter_by_programme_pk(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            resp = self.client.get(self.url_registration, {"programme_pk": str(self.other_program.pk)})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        reg = resp.data["results"][0]
        self.assertEqual(reg["name"], self.registration_3.name)
        self.assertEqual(reg["aurora_id"], self.registration_3.source_id)
        self.assertEqual(reg["project"], str(self.prj_2.pk))
        self.assertEqual(reg["organization"], self.organization_2.slug)
