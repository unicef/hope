import base64
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_date

from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient, APIRequestFactory
from unit.api.base import HOPEApiTestCase

from hope.apps.account.models import Role, RoleAssignment, User
from hope.apps.account.permissions import Permissions
from hope.apps.payment.models import PaymentPlan
from hope.apps.program.api.serializers import (
    ProgramCycleCreateSerializer,
    ProgramCycleUpdateSerializer,
)
from hope.apps.program.api.views import ProgramCycleViewSet
from hope.apps.program.models import Program, ProgramCycle


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
        unicef = PartnerFactory(name="UNICEF")
        partner = PartnerFactory(name="UNICEF HQ", parent=unicef)
        cls.user = UserFactory(username="Hope_Test_DRF", password="SpeedUp", partner=partner, is_superuser=True)
        cls.program = ProgramFactory(
            name="Test REST API Program",
            status=Program.ACTIVE,
            start_date="2023-01-01",
            end_date="2099-12-31",
            frequency_of_payments=Program.REGULAR,
            cycle__title="Default",
            cycle__status=ProgramCycle.ACTIVE,
            cycle__start_date="2023-01-02",
            cycle__end_date="2023-01-10",
            cycle__created_by=cls.user,
        )
        permission_list = [perm.value for perm in user_permissions]
        role, created = Role.objects.update_or_create(name="TestName", defaults={"permissions": permission_list})
        user_role, _ = RoleAssignment.objects.get_or_create(
            user=cls.user, role=role, business_area=cls.business_area, program=cls.program
        )
        cls.client = APIClient()

        cls.cycle1 = ProgramCycle.objects.create(
            program=cls.program,
            title="Cycle 1",
            status=ProgramCycle.ACTIVE,
            start_date="2023-02-01",
            end_date="2023-02-20",
            created_by=cls.user,
        )
        cls.cycle2 = ProgramCycle.objects.create(
            program=cls.program,
            title="RANDOM NAME",
            status=ProgramCycle.DRAFT,
            start_date="2023-05-01",
            end_date="2023-05-25",
            created_by=cls.user,
        )
        cls.list_url = reverse(
            "api:programs:cycles-list", kwargs={"business_area_slug": "afghanistan", "program_slug": cls.program.slug}
        )
        cls.cycle_1_detail_url = reverse(
            "api:programs:cycles-detail",
            kwargs={"business_area_slug": "afghanistan", "program_slug": cls.program.slug, "pk": str(cls.cycle1.id)},
        )

    def test_list_program_cycles_without_perms(self) -> None:
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_program_cycles(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        first_cycle = results[0]
        second_cycle = results[1]
        last_cycle = results[2]
        # check can_remove_cycle
        self.assertEqual(first_cycle["can_remove_cycle"], False)
        self.assertEqual(second_cycle["can_remove_cycle"], False)
        self.assertEqual(last_cycle["status"], "Draft")
        self.assertEqual(last_cycle["can_remove_cycle"], True)

    def test_retrieve_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.cycle_1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Created Cycle",
            "start_date": parse_date("2024-05-26"),
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProgramCycle.objects.count(), 4)
        self.assertEqual(ProgramCycle.objects.last().title, "New Created Cycle")
        self.assertEqual(ProgramCycle.objects.last().end_date, None)

    def test_full_update_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Updated Fully Title",
            "start_date": parse_date("2023-02-02"),
            "end_date": parse_date("2023-02-22"),
        }
        response = self.client.put(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.title, "Updated Fully Title")
        self.assertEqual(self.cycle1.start_date.strftime("%Y-%m-%d"), "2023-02-02")
        self.assertEqual(self.cycle1.end_date.strftime("%Y-%m-%d"), "2023-02-22")

    def test_partial_update_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        data = {"title": "Title Title New", "start_date": parse_date("2023-02-11")}
        response = self.client.patch(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.title, "Title Title New")
        self.assertEqual(self.cycle1.start_date.strftime("%Y-%m-%d"), "2023-02-11")

    def test_update_cycle_dates_and_payment_plan(self) -> None:
        payment_plan = PaymentPlanFactory(program_cycle=self.cycle1, start_date=None, end_date=None)
        self.assertIsNone(payment_plan.start_date)
        self.assertIsNone(payment_plan.end_date)
        self.client.force_authenticate(user=self.user)

        # update only end_date
        data = {"end_date": parse_date("2023-02-22")}
        response = self.client.patch(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.end_date.strftime("%Y-%m-%d"), "2023-02-22")
        self.assertIsNone(payment_plan.start_date)

        # update only start_date
        data = {"start_date": parse_date("2023-02-02")}
        response = self.client.patch(self.cycle_1_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment_plan.refresh_from_db()
        self.assertEqual(payment_plan.start_date.strftime("%Y-%m-%d"), "2023-02-02")

    def test_delete_program_cycle(self) -> None:
        cycle3 = ProgramCycleFactory(
            program=self.program,
            status=ProgramCycle.DRAFT,
        )
        # create PP
        pp = PaymentPlanFactory(program_cycle=cycle3)
        self.assertEqual(PaymentPlan.objects.count(), 1)
        self.assertEqual(ProgramCycle.objects.count(), 4)
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "api:programs:cycles-detail",
            kwargs={"business_area_slug": "afghanistan", "program_slug": self.program.slug, "pk": str(cycle3.id)},
        )

        bad_response = self.client.delete(url)
        self.assertEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Don’t allow to delete Cycle with assigned Target Population", bad_response.data)
        pp.delete()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProgramCycle.objects.count(), 3)
        self.assertEqual(PaymentPlan.objects.count(), 0)

    def test_filter_by_status(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"status": "DRAFT"})
        self.assertEqual(ProgramCycle.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "Draft")

    def test_filter_by_title_startswith(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"title": "Cycle"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Cycle 1")

    def test_filter_by_start_date_gte(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"start_date": "2023-03-01"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["start_date"], "2023-05-01")

    def test_filter_by_end_date_lte(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"end_date": "2023-01-15"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["end_date"], "2023-01-10")

    def test_filter_by_program(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"program": str(self.program.pk)})
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
        response = self.client.get(
            self.list_url, {"total_delivered_quantity_usd_from": "1000", "total_delivered_quantity_usd_to": "1900"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(str(response.data["results"][0]["total_delivered_quantity_usd"]), "1500.00")

    def test_reactivate_program_cycle(self) -> None:
        self.client.force_authenticate(user=self.user)
        self.cycle1.status = ProgramCycle.FINISHED
        self.cycle1.save()

        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.status, ProgramCycle.FINISHED)
        response = self.client.post(self.cycle_1_detail_url + "reactivate/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.status, ProgramCycle.ACTIVE)

    def test_finish_program_cycle(self) -> None:
        PaymentPlanFactory(program_cycle=self.cycle1, status=PaymentPlan.Status.TP_OPEN)
        payment_plan = PaymentPlanFactory(program_cycle=self.cycle1, status=PaymentPlan.Status.IN_REVIEW)
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.cycle1.status, ProgramCycle.ACTIVE)
        self.assertEqual(payment_plan.status, PaymentPlan.Status.IN_REVIEW)
        resp_error = self.client.post(self.cycle_1_detail_url + "finish/", {}, format="json")
        self.assertEqual(resp_error.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.", resp_error.data)

        payment_plan.status = PaymentPlan.Status.ACCEPTED
        payment_plan.save()
        response = self.client.post(self.cycle_1_detail_url + "finish/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cycle1.refresh_from_db()
        self.assertEqual(self.cycle1.status, ProgramCycle.FINISHED)


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
        user, _ = User.objects.get_or_create(
            username="MyUser", first_name="FirstName", last_name="LastName", password="PassworD"
        )
        request.user = user
        request.parser_context = {
            "kwargs": {"program_slug": str(self.program.slug), "business_area_slug": "afghanistan"}
        }
        return {"request": request}

    def test_validate_title_unique(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1")
        data = {"title": "Cycle 1", "start_date": parse_date("2033-01-02"), "end_date": parse_date("2033-01-12")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle title should be unique.", str(error.exception))

    def test_validate_if_no_end_date(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1", end_date=None)
        data = {"title": "Cycle 123123", "start_date": parse_date("2025-01-02"), "end_date": parse_date("2025-01-12")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("All Programme Cycles must have an end date before creating a new one.", str(error.exception))

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {"title": "Cycle new", "start_date": self.program.start_date, "end_date": self.program.end_date}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle can only be created for an Active Programme.", str(error.exception))

    def test_validate_start_date(self) -> None:
        # before program start date
        data = {"title": "Cycle 3", "start_date": parse_date("2022-01-01"), "end_date": parse_date("2023-01-01")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle start date must be between programme start and end dates.", str(error.exception))
        # after program end date
        data = {"title": "Cycle 3", "start_date": parse_date("2100-01-01"), "end_date": parse_date("2100-01-11")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle start date must be between programme start and end dates.", str(error.exception))
        # before latest cycle
        data = {"title": "Cycle 34567", "start_date": parse_date("2023-01-09"), "end_date": parse_date("2023-01-30")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Start date must be after the latest cycle end date.", str(error.exception))
        # before program start date
        self.program.end_date = None
        self.program.save()
        data = {"title": "Cycle 3", "start_date": parse_date("2022-01-01"), "end_date": parse_date("2023-01-01")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle start date cannot be before programme start date.", str(error.exception))
        # no error
        data = {"title": "Cycle new", "start_date": parse_date("2055-01-01"), "end_date": parse_date("2055-11-11")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_validate_end_date(self) -> None:
        # after program end date
        data = {"title": "Cycle", "start_date": parse_date("2098-01-01"), "end_date": parse_date("2111-01-01")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle end date must be between programme start and end dates", str(error.exception))
        # before program start date
        data = {"title": "Cycle", "start_date": parse_date("2023-01-01"), "end_date": parse_date("2022-01-01")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("End date cannot be before start date.", str(error.exception))
        # end before start date
        data = {"title": "Cycle", "start_date": parse_date("2023-02-22"), "end_date": parse_date("2023-02-11")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("End date cannot be before start date", str(error.exception))
        # no program end date and end date before program end date
        self.program.end_date = None
        self.program.save()
        data = {"title": "Cycle", "start_date": parse_date("2055-01-01"), "end_date": parse_date("2000-01-02")}
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle end date cannot be before programme start date.", str(error.exception))


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
        data = {"title": "Cycle 1 "}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle with this title already exists.", str(error.exception))

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {"title": "Cycle 2"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Updating Programme Cycle is only possible for Active Programme.", str(error.exception))

    def test_validate_start_date(self) -> None:
        cycle_2 = ProgramCycleFactory(
            program=self.program, title="Cycle 2222", start_date="2023-12-20", end_date="2023-12-25"
        )
        cycle_2.save()
        cycle_2.refresh_from_db()
        data = {"start_date": parse_date("2023-12-20"), "end_date": parse_date("2023-12-19")}
        serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("End date cannot be earlier than the start date.", str(error.exception))

        data = {"start_date": parse_date("2023-12-10"), "end_date": parse_date("2023-12-26")}
        serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=self.get_serializer_context())
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycles' timeframes must not overlap with the provided start date.", str(error.exception)
        )
        # before program start date (program with end_date)
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2, data={"start_date": parse_date("1999-12-10")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle start date must be within the programme's start and end dates", str(error.exception)
        )
        # after program end date
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2, data={"start_date": parse_date("2100-01-01")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle start date must be within the programme's start and end dates.", str(error.exception)
        )
        # before program start date
        self.program.end_date = None
        self.program.save()
        cycle_2.refresh_from_db()
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2, data={"start_date": parse_date("2022-01-01")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Programme Cycle start date must be after the programme start date.", str(error.exception))
        # start date after existing end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"start_date": parse_date("2023-12-26")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle start date must be before the end date.",
            str(error.exception),
        )
        # no error
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2, data={"start_date": parse_date("2023-12-24")}, context=self.get_serializer_context()
        )
        self.assertTrue(serializer.is_valid())

    def test_validate_end_date(self) -> None:
        self.cycle.end_date = datetime.strptime("2023-02-03", "%Y-%m-%d").date()
        self.cycle.save()
        # end date before program start date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"end_date": parse_date("1999-10-10")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle end date must be within the programme's start and end dates.",
            str(error.exception),
        )
        # end date after program end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"end_date": parse_date("2100-10-10")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle end date must be within the programme's start and end dates.",
            str(error.exception),
        )
        # clearing end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"end_date": None}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Cannot clear the Programme Cycle end date if it was previously set.",
            str(error.exception),
        )
        # end date before existing start date
        self.program.end_date = None
        self.program.save()
        self.cycle.start_date = datetime.strptime("2023-02-02", "%Y-%m-%d").date()
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"end_date": parse_date("2023-02-01")}, context=self.get_serializer_context()
        )
        with self.assertRaises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            "Programme Cycle end date must be after the start date.",
            str(error.exception),
        )
        # no errors
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle, data={"end_date": parse_date("2023-12-24")}, context=self.get_serializer_context()
        )
        self.assertTrue(serializer.is_valid())


class ProgramCycleViewSetTestCase(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")
        self.viewset = ProgramCycleViewSet()

    def test_delete_non_active_program(self) -> None:
        program = ProgramFactory(
            status=Program.DRAFT,
            cycle__status=ProgramCycle.DRAFT,
        )
        cycle = program.cycles.first()
        with self.assertRaises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        self.assertEqual(context.exception.detail[0], "Only Programme Cycle for Active Programme can be deleted.")  # type: ignore

    def test_delete_non_draft_cycle(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            cycle__status=ProgramCycle.ACTIVE,
        )
        cycle = program.cycles.first()
        with self.assertRaises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        self.assertEqual(context.exception.detail[0], "Only Draft Programme Cycle can be deleted.")  # type: ignore

    def test_delete_last_cycle(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            cycle__status=ProgramCycle.DRAFT,
        )
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
