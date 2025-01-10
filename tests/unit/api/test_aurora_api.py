from django.urls import reverse

from rest_framework import status

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.contrib.aurora.fixtures import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
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
        self.organization = OrganizationFactory(name="Test Organization", slug="test_organization")
        self.prj_1 = ProjectFactory.create(
            name="Test Project 1",
            source_id="123",
            organization=self.organization,
            programme=self.program,
        )
        self.prj_2 = ProjectFactory.create(
            name="Test Project 2",
            source_id="456",
            organization=self.organization,
            programme=self.program,
        )
        self.registration = RegistrationFactory(project=self.prj_1)

        self.url_organization = reverse("api:organization-list")
        self.url_project = reverse("api:project-list")
        self.url_registration = reverse("api:registration-list")

    # Organization
    def test_organization_list_no_permission(self) -> None:
        response = self.client.get(self.url_organization)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organization_list_all(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_organization)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    # Project
    def test_project_list_no_permission(self) -> None:
        response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_list_all(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_project)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    # Registration
    def test_registration_list_no_permission(self) -> None:
        response = self.client.get(self.url_registration)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_list_all(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_registration)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
