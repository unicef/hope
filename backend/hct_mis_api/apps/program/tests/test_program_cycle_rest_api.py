import base64
from decimal import Decimal

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.program.api.serializers import ProgramCycleListSerializer
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle


class ProgramCycleAPITestCase(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_permissions = [
            Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
            Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
            Permissions.PM_PROGRAMME_CYCLE_CREATE,
            Permissions.PM_PROGRAMME_CYCLE_UPDATE,
            Permissions.PM_PROGRAMME_CYCLE_DELETE,
        ]
        partner = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(username="Hope_Test_DRF", password="SpeedUp", partner=partner)
        permission_list = [perm.value for perm in user_permissions]
        role, created = Role.objects.update_or_create(name="TestName", defaults={"permissions": permission_list})
        user_role, _ = UserRole.objects.get_or_create(user=cls.user, role=role, business_area=cls.business_area)
        cls.client = APIClient()

        cls.program = ProgramFactory(
            name="Test REST API Program",
            status=Program.ACTIVE,
            start_date="2023-01-01",
            end_date="2099-12-31",
            cycle__title="Default",
            cycle__status=ProgramCycle.ACTIVE,
            cycle__start_date="2023-01-02",
            cycle__end_date="2023-01-10",
        )
        cls.cycle1 = ProgramCycle.objects.create(
            program=cls.program,
            title="Cycle 1",
            status=ProgramCycle.ACTIVE,
            start_date="2023-02-01",
            end_date="2023-02-20",
        )
        cls.cycle2 = ProgramCycle.objects.create(
            program=cls.program,
            title="RANDOM NAME",
            status=ProgramCycle.DRAFT,
            start_date="2023-05-01",
            end_date="2023-05-25",
        )
        cls.program_id_base64 = base64.b64encode(f"ProgramNode:{str(cls.program.pk)}".encode()).decode()
        cls.list_url = reverse(
            "api:programs:cycles-list", kwargs={"business_area": "afghanistan", "program_id": cls.program_id_base64}
        )
        cls.cycle_1_detail_url = reverse(
            "api:programs:cycles-detail",
            kwargs={"business_area": "afghanistan", "program_id": cls.program_id_base64, "pk": str(cls.cycle1.id)},
        )

    def test_list_program_cycles_without_perms(self) -> None:
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_program_cycles(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cycles = ProgramCycle.objects.filter(program=self.program)
        self.assertEqual(int(response.data["count"]), cycles.count())

    def test_retrieve_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cycle_1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProgramCycleListSerializer(self.cycle1)
        self.assertEqual(response.data, serializer.data)

    def test_create_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Created Cycle",
            "start_date": "2024-01-10",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProgramCycle.objects.count(), 4)
        self.assertEqual(ProgramCycle.objects.last().title, "New Created Cycle")
        self.assertEqual(ProgramCycle.objects.last().end_date, None)

    def test_full_update_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {"title": "Updated Fully Title", "start_date": "2023-02-02", "end_date": "2023-02-22"}
        response = self.client.put(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.title, "Updated Fully Title")
        self.assertEqual(self.cycle1.start_date.strftime("%Y-%m-%d"), "2023-02-02")
        self.assertEqual(self.cycle1.end_date.strftime("%Y-%m-%d"), "2023-02-22")

    def test_partial_update_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {"title": "Title Title New", "start_date": "2023-02-11"}
        response = self.client.patch(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.title, "Title Title New")
        self.assertEqual(self.cycle1.start_date.strftime("%Y-%m-%d"), "2023-02-11")

    def test_delete_program_cycle(self) -> None:
        cycle3 = ProgramCycleFactory(
            program=self.program,
            status=ProgramCycle.DRAFT,
        )
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:programs:cycles-detail",
            kwargs={"business_area": "afghanistan", "program_id": self.program_id_base64, "pk": str(cycle3.id)},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProgramCycle.objects.count(), 3)
        self.assertEqual(ProgramCycle.all_objects.count(), 4)

    def test_filter_by_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"status": "DRAFT"})
        self.assertEqual(ProgramCycle.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "Draft")

    def test_filter_by_title_startswith(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"title__startswith": "Cycle"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Cycle 1")

    def test_filter_by_start_date_gte(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"start_date__gte": "2023-03-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["start_date"], "2023-05-01")

    def test_filter_by_end_date_lte(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"end_date__lte": "2023-06-30"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        # self.assertEqual(response.data["results"][0]["end_date"], "2023-06-30")

    def test_filter_by_program(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"program": self.program_id_base64})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_search_filter(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"search": "Cycle 1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Cycle 1")

    def test_filter_total_delivered_quantity_usd(self) -> None:
        self.client.force_authenticate(user=self.user)
        PaymentPlanFactory(program_cycle=self.cycle1, total_delivered_quantity_usd=Decimal("500.00"))
        PaymentPlanFactory(program_cycle=self.cycle2, total_delivered_quantity_usd=Decimal("1500.00"))
        # response = self.client.get(self.list_url, {'total_delivered_quantity_usd': '1000,2000'})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["results"]), 1)
        # self.assertEqual(response.data["results"][0]['total_delivered_quantity_usd'], '1500.00')
