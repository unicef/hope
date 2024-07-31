import base64
from decimal import Decimal
from typing import Any, Dict

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient, APIRequestFactory

from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.program.api.serializers import (
    ProgramCycleCreateSerializer,
    ProgramCycleListSerializer,
    ProgramCycleUpdateSerializer,
)
from hct_mis_api.apps.program.api.views import ProgramCycleViewSet
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle


class ProgramCycleAPITestCase(HOPEApiTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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
        response = self.client.post(self.list_url, data, format="json")
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
        response = self.client.get(self.list_url, {"end_date__lte": "2023-01-15"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["end_date"], "2023-01-10")

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
        self.cycle2.refresh_from_db()
        self.assertEqual(self.cycle2.total_delivered_quantity_usd, 1500)
        # TODO: have to fix this one
        # response = self.client.get(self.list_url, {"total_delivered_quantity_usd": "{\"min\": \"1000\", \"max\": \"2000\"}"})
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data["results"]), 1)
        # self.assertEqual(response.data["results"][0]["total_delivered_quantity_usd"], "1500.00")


class ProgramCycleCreateSerializerTest(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")
        self.factory = APIRequestFactory()
        self.program = ProgramFactory(
            status=Program.ACTIVE,
            start_date="2023-01-01",
            end_date="2099-12-31",
            cycle__status=ProgramCycle.ACTIVE,
            cycle__start_date="2023-01-02",
            cycle__end_date="2023-01-10",
        )
        self.program_id = base64.b64encode(f"ProgramNode:{str(self.program.pk)}".encode()).decode()

    def get_serializer_context(self) -> Dict[str, Any]:
        request = self.factory.get("/")
        request.parser_context = {"kwargs": {"program_id": str(self.program_id)}}
        return {"request": request}

    def test_validate_title_unique(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1")
        data = {"title": "Cycle 1", "start_date": "2033-01-02", "end_date": "2033-01-12"}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycles' title should be unique.", str(error.exception))

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {"title": "Cycle new", "start_date": self.program.start_date, "end_date": self.program.end_date}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Create Programme Cycle is possible only for Active Programme.", str(error.exception))

    def test_validate_start_date(self) -> None:
        data = {"title": "Cycle 3", "start_date": "2022-01-01", "end_date": "2023-01-01"}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle start date cannot be earlier than programme start date", str(error.exception))

    def test_validate_end_date(self) -> None:
        data = {"title": "Cycle new", "start_date": "2098-01-01", "end_date": "2111-01-01"}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle end date cannot be later than programme end date", str(error.exception))

    def test_validate_overlapping_cycles(self) -> None:
        ProgramCycleFactory(program=self.program, start_date="2023-02-01", end_date="2023-02-20")
        data = {"title": "Cycle new", "start_date": "2023-02-15", "end_date": "2023-03-01"}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Program Cycles' timeframes must not overlap.", str(error.exception))


class ProgramCycleUpdateSerializerTest(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")
        self.factory = APIRequestFactory()
        self.program = ProgramFactory(
            status=Program.ACTIVE,
            start_date="2023-01-01",
            end_date="2099-12-31",
            cycle__status=ProgramCycle.ACTIVE,
            cycle__start_date="2023-01-02",
            cycle__end_date="2023-12-10",
        )
        self.program_id = base64.b64encode(f"ProgramNode:{str(self.program.pk)}".encode()).decode()
        self.cycle = self.program.cycles.first()

    def get_serializer_context(self) -> Dict[str, Any]:
        request = self.factory.get("/")
        request.parser_context = {"kwargs": {"program_id": self.program_id, "pk": str(self.cycle.id)}}
        return {"request": request}

    def test_validate_title_unique(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1")
        data = {"title": "Cycle 1"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("A ProgramCycle with this title already exists.", str(error.exception))

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {"title": "Cycle 2"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Update Programme Cycle is possible only for Active Programme.", str(error.exception))

    def test_validate_start_date(self) -> None:
        data = {"end_date": "2023-11-11"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Not possible leave the Programme Cycle start date empty.", str(error.exception))

    def test_validate_end_date(self) -> None:
        self.cycle.end_date = None
        self.cycle.save()
        data = {"start_date": "2023-02-02"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Not possible leave the Programme Cycle end date empty if it was empty upon starting the edit.",
            str(error.exception),
        )


class ProgramCycleViewSetTestCase(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")
        self.viewset = ProgramCycleViewSet()

    def test_delete_non_active_program(self) -> None:
        program = ProgramFactory(status=Program.DRAFT, cycle__status=ProgramCycle.DRAFT)
        cycle = program.cycles.first()
        with self.assertRaises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        self.assertEqual(context.exception.detail[0], "Only Programme Cycle for Active Programme can be deleted.")  # type: ignore

    def test_delete_non_draft_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE, cycle__status=ProgramCycle.ACTIVE)
        cycle = program.cycles.first()
        with self.assertRaises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        self.assertEqual(context.exception.detail[0], "Only Draft Programme Cycle can be deleted.")  # type: ignore

    def test_delete_last_cycle(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE, cycle__status=ProgramCycle.DRAFT)
        cycle = program.cycles.first()
        with self.assertRaises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        self.assertEqual(context.exception.detail[0], "Don’t allow to delete last Cycle.")  # type: ignore

    def test_successful_delete(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        cycle1 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
        cycle2 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
        self.viewset.perform_destroy(cycle1)
        self.assertFalse(ProgramCycle.objects.filter(id=cycle1.id).exists())
        self.assertTrue(ProgramCycle.objects.filter(id=cycle2.id).exists())
