import base64
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_date
import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.models import User
from hope.apps.account.permissions import Permissions
from hope.apps.payment.models import PaymentPlan
from hope.apps.program.api.serializers import (
    ProgramCycleCreateSerializer,
    ProgramCycleUpdateSerializer,
)
from hope.apps.program.api.views import ProgramCycleViewSet
from hope.apps.program.models import Program, ProgramCycle

pytestmark = pytest.mark.django_db(transaction=True)


class TestProgramCycleAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            start_date="2023-01-01",
            end_date="2099-12-31",
            frequency_of_payments=Program.REGULAR,
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.default_cycle = self.program.cycles.first()
        self.default_cycle.title = "Default"
        self.default_cycle.status = ProgramCycle.ACTIVE
        self.default_cycle.start_date = "2023-01-02"
        self.default_cycle.end_date = "2023-01-10"
        self.default_cycle.save()

        self.cycle1 = ProgramCycleFactory(
            program=self.program,
            title="Cycle 1",
            status=ProgramCycle.ACTIVE,
            start_date="2023-02-01",
            end_date="2023-02-20",
        )
        self.cycle2 = ProgramCycleFactory(
            program=self.program,
            title="RANDOM NAME",
            status=ProgramCycle.DRAFT,
            start_date="2023-05-01",
            end_date="2023-05-25",
        )

        self.list_url = reverse(
            "api:programs:cycles-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
            },
        )
        self.cycle_1_detail_url = reverse(
            "api:programs:cycles-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": str(self.cycle1.id),
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_200_OK),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_list_program_cycles(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            results = response.data["results"]
            assert len(results) == 3  # default_cycle, cycle1, cycle2
            first_cycle = results[0]
            second_cycle = results[1]
            last_cycle = results[2]
            # check can_remove_cycle
            assert first_cycle["can_remove_cycle"] is False
            assert second_cycle["can_remove_cycle"] is False
            assert last_cycle["status"] == "Draft"
            assert last_cycle["can_remove_cycle"] is True

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS], status.HTTP_200_OK),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_retrieve_program_cycle(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.cycle_1_detail_url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_CREATE], status.HTTP_201_CREATED),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_program_cycle(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {
            "title": "New Created Cycle",
            "start_date": parse_date("2024-05-26"),
        }
        response = self.api_client.post(self.list_url, data, format="json")
        assert response.status_code == expected_status

        if expected_status == status.HTTP_201_CREATED:
            assert ProgramCycle.objects.count() == 4
            assert ProgramCycle.objects.last().title == "New Created Cycle"
            assert ProgramCycle.objects.last().end_date is None

    @pytest.mark.parametrize(
        ("permissions", "expected_status", "method"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_UPDATE], status.HTTP_200_OK, "put"),
            ([Permissions.PM_PROGRAMME_CYCLE_UPDATE], status.HTTP_200_OK, "patch"),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN, "put"),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN, "patch"),
            ([], status.HTTP_403_FORBIDDEN, "put"),
            ([], status.HTTP_403_FORBIDDEN, "patch"),
        ],
    )
    def test_update_program_cycle(
        self, permissions: List, expected_status: int, method: str, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        if method == "put":
            data = {
                "title": "Updated Fully Title",
                "start_date": parse_date("2023-02-02"),
                "end_date": parse_date("2023-02-22"),
            }
            response = self.api_client.put(self.cycle_1_detail_url, data, format="json")
        else:  # patch
            data = {"title": "Title Title New", "start_date": parse_date("2023-02-11")}
            response = self.api_client.patch(self.cycle_1_detail_url, data, format="json")

        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            self.cycle1.refresh_from_db()
            if method == "put":
                assert self.cycle1.title == "Updated Fully Title"
                assert self.cycle1.start_date.strftime("%Y-%m-%d") == "2023-02-02"
                assert self.cycle1.end_date.strftime("%Y-%m-%d") == "2023-02-22"
            else:  # patch
                assert self.cycle1.title == "Title Title New"
                assert self.cycle1.start_date.strftime("%Y-%m-%d") == "2023-02-11"

    def test_update_cycle_dates_and_payment_plan(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        payment_plan = PaymentPlanFactory(program_cycle=self.cycle1, start_date=None, end_date=None)
        assert payment_plan.start_date is None
        assert payment_plan.end_date is None

        # update only end_date
        data = {"end_date": parse_date("2023-02-22")}
        response = self.api_client.patch(self.cycle_1_detail_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        payment_plan.refresh_from_db()
        assert payment_plan.end_date.strftime("%Y-%m-%d") == "2023-02-22"
        assert payment_plan.start_date is None

        # update only start_date
        data = {"start_date": parse_date("2023-02-02")}
        response = self.api_client.patch(self.cycle_1_detail_url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        payment_plan.refresh_from_db()
        assert payment_plan.start_date.strftime("%Y-%m-%d") == "2023-02-02"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_DELETE], status.HTTP_204_NO_CONTENT),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_delete_program_cycle(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        cycle3 = ProgramCycleFactory(
            program=self.program,
            status=ProgramCycle.DRAFT,
        )
        # create PP
        pp = PaymentPlanFactory(program_cycle=cycle3)
        assert PaymentPlan.objects.count() == 1
        assert ProgramCycle.objects.count() == 4

        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        url = reverse(
            "api:programs:cycles-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": str(cycle3.id),
            },
        )

        bad_response = self.api_client.delete(url)
        if permissions and Permissions.PM_PROGRAMME_CYCLE_DELETE in permissions:
            assert bad_response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Don't allow to delete Cycle with assigned Target Population" in bad_response.data
            pp.delete()

            response = self.api_client.delete(url)
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert ProgramCycle.objects.count() == 3
            assert PaymentPlan.objects.count() == 0
        else:
            assert bad_response.status_code == expected_status

    def test_filter_by_status(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"status": "DRAFT"})
        assert ProgramCycle.objects.count() == 3
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["status"] == "Draft"

    def test_filter_by_title_startswith(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"title": "Cycle"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Cycle 1"

    def test_filter_by_start_date_gte(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"start_date": "2023-03-01"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["start_date"] == "2023-05-01"

    def test_filter_by_end_date_lte(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"end_date": "2023-01-15"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["end_date"] == "2023-01-10"

    def test_filter_by_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"program": str(self.program.pk)})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_search_filter(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url, {"search": "Cycle 1"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == "Cycle 1"

    def test_filter_total_delivered_quantity_usd(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        PaymentPlanFactory(program_cycle=self.cycle1, total_delivered_quantity_usd=Decimal("500.00"))
        PaymentPlanFactory(program_cycle=self.cycle2, total_delivered_quantity_usd=Decimal("1500.00"))
        self.cycle2.refresh_from_db()
        assert self.cycle2.total_delivered_quantity_usd == 1500
        response = self.api_client.get(
            self.list_url,
            {
                "total_delivered_quantity_usd_from": "1000",
                "total_delivered_quantity_usd_to": "1900",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert str(response.data["results"][0]["total_delivered_quantity_usd"]) == "1500.00"

    def test_filter_total_entitled_quantity_usd(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        PaymentPlanFactory(program_cycle=self.cycle1, total_entitled_quantity_usd=Decimal("750.00"))
        PaymentPlanFactory(program_cycle=self.cycle2, total_entitled_quantity_usd=Decimal("2000.00"))
        self.cycle2.refresh_from_db()
        assert self.cycle2.total_entitled_quantity_usd == 2000
        response = self.api_client.get(
            self.list_url,
            {
                "total_entitled_quantity_usd_from": "1000",
                "total_entitled_quantity_usd_to": "2500",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert str(response.data["results"][0]["total_entitled_quantity_usd"]) == "2000.00"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_UPDATE], status.HTTP_200_OK),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_reactivate_program_cycle(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        self.cycle1.status = ProgramCycle.FINISHED
        self.cycle1.save()

        self.cycle1.refresh_from_db()
        assert self.cycle1.status == ProgramCycle.FINISHED
        response = self.api_client.post(self.cycle_1_detail_url + "reactivate/", {}, format="json")
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            self.cycle1.refresh_from_db()
            assert self.cycle1.status == ProgramCycle.ACTIVE

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_PROGRAMME_CYCLE_UPDATE], status.HTTP_200_OK),
            ([Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_finish_program_cycle(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        PaymentPlanFactory(program_cycle=self.cycle1, status=PaymentPlan.Status.TP_OPEN)
        payment_plan = PaymentPlanFactory(program_cycle=self.cycle1, status=PaymentPlan.Status.IN_REVIEW)
        assert self.cycle1.status == ProgramCycle.ACTIVE
        assert payment_plan.status == PaymentPlan.Status.IN_REVIEW

        resp_error = self.api_client.post(self.cycle_1_detail_url + "finish/", {}, format="json")
        if permissions and Permissions.PM_PROGRAMME_CYCLE_UPDATE in permissions:
            assert resp_error.status_code == status.HTTP_400_BAD_REQUEST
            assert "All Payment Plans and Follow-Up Payment Plans have to be Reconciled." in resp_error.data

            payment_plan.status = PaymentPlan.Status.ACCEPTED
            payment_plan.save()
            response = self.api_client.post(self.cycle_1_detail_url + "finish/", {}, format="json")
            assert response.status_code == status.HTTP_200_OK
            self.cycle1.refresh_from_db()
            assert self.cycle1.status == ProgramCycle.FINISHED
        else:
            assert resp_error.status_code == expected_status


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
            username="MyUser",
            first_name="FirstName",
            last_name="LastName",
            password="PassworD",
        )
        request.user = user
        request.parser_context = {
            "kwargs": {
                "program_slug": str(self.program.slug),
                "business_area_slug": "afghanistan",
            }
        }
        return {"request": request}

    def test_validate_title_unique(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1")
        data = {
            "title": "Cycle 1",
            "start_date": parse_date("2033-01-02"),
            "end_date": parse_date("2033-01-12"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle title should be unique." in str(error.value)

    def test_validate_if_no_end_date(self) -> None:
        ProgramCycleFactory(program=self.program, title="Cycle 1", end_date=None)
        data = {
            "title": "Cycle 123123",
            "start_date": parse_date("2025-01-02"),
            "end_date": parse_date("2025-01-12"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "All Programme Cycles must have an end date before creating a new one." in str(error.value)

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {
            "title": "Cycle new",
            "start_date": self.program.start_date,
            "end_date": self.program.end_date,
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle can only be created for an Active Programme." in str(error.value)

    def test_validate_start_date(self) -> None:
        # before program start date
        data = {
            "title": "Cycle 3",
            "start_date": parse_date("2022-01-01"),
            "end_date": parse_date("2023-01-01"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be between programme start and end dates." in str(error.value)
        # after program end date
        data = {
            "title": "Cycle 3",
            "start_date": parse_date("2100-01-01"),
            "end_date": parse_date("2100-01-11"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be between programme start and end dates." in str(error.value)
        # before latest cycle
        data = {
            "title": "Cycle 34567",
            "start_date": parse_date("2023-01-09"),
            "end_date": parse_date("2023-01-30"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Start date must be after the latest cycle end date." in str(error.value)
        # before program start date
        self.program.end_date = None
        self.program.save()
        data = {
            "title": "Cycle 3",
            "start_date": parse_date("2022-01-01"),
            "end_date": parse_date("2023-01-01"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date cannot be before programme start date." in str(error.value)
        # no error
        data = {
            "title": "Cycle new",
            "start_date": parse_date("2055-01-01"),
            "end_date": parse_date("2055-11-11"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        assert serializer.is_valid(raise_exception=True)

    def test_validate_end_date(self) -> None:
        # after program end date
        data = {
            "title": "Cycle",
            "start_date": parse_date("2098-01-01"),
            "end_date": parse_date("2111-01-01"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle end date must be between programme start and end dates" in str(error.value)
        # before program start date
        data = {
            "title": "Cycle",
            "start_date": parse_date("2023-01-01"),
            "end_date": parse_date("2022-01-01"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "End date cannot be before start date." in str(error.value)
        # end before start date
        data = {
            "title": "Cycle",
            "start_date": parse_date("2023-02-22"),
            "end_date": parse_date("2023-02-11"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "End date cannot be before start date" in str(error.value)
        # no program end date and end date before program end date
        self.program.end_date = None
        self.program.save()
        data = {
            "title": "Cycle",
            "start_date": parse_date("2055-01-01"),
            "end_date": parse_date("2000-01-02"),
        }
        serializer = ProgramCycleCreateSerializer(data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle end date cannot be before programme start date." in str(error.value)


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
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle with this title already exists." in str(error.value)

    def test_validate_program_status(self) -> None:
        self.program.status = Program.DRAFT
        self.program.save()
        data = {"title": "Cycle 2"}
        serializer = ProgramCycleUpdateSerializer(instance=self.cycle, data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Updating Programme Cycle is only possible for Active Programme." in str(error.value)

    def test_validate_start_date(self) -> None:
        cycle_2 = ProgramCycleFactory(
            program=self.program,
            title="Cycle 2222",
            start_date="2023-12-20",
            end_date="2023-12-25",
        )
        cycle_2.save()
        cycle_2.refresh_from_db()
        data = {
            "start_date": parse_date("2023-12-20"),
            "end_date": parse_date("2023-12-19"),
        }
        serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "End date cannot be earlier than the start date." in str(error.value)

        data = {
            "start_date": parse_date("2023-12-10"),
            "end_date": parse_date("2023-12-26"),
        }
        serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=self.get_serializer_context())
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycles' timeframes must not overlap with the provided start date." in str(error.value)
        # before program start date (program with end_date)
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2,
            data={"start_date": parse_date("1999-12-10")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be within the programme's start and end dates" in str(error.value)
        # after program end date
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2,
            data={"start_date": parse_date("2100-01-01")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be within the programme's start and end dates." in str(error.value)
        # before program start date
        self.program.end_date = None
        self.program.save()
        cycle_2.refresh_from_db()
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2,
            data={"start_date": parse_date("2022-01-01")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be after the programme start date." in str(error.value)
        # start date after existing end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"start_date": parse_date("2023-12-26")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle start date must be before the end date." in str(error.value)
        # no error
        serializer = ProgramCycleUpdateSerializer(
            instance=cycle_2,
            data={"start_date": parse_date("2023-12-24")},
            context=self.get_serializer_context(),
        )
        assert serializer.is_valid()

    def test_validate_end_date(self) -> None:
        self.cycle.end_date = datetime.strptime("2023-02-03", "%Y-%m-%d").date()
        self.cycle.save()
        # end date before program start date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"end_date": parse_date("1999-10-10")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle end date must be within the programme's start and end dates." in str(error.value)
        # end date after program end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"end_date": parse_date("2100-10-10")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle end date must be within the programme's start and end dates." in str(error.value)
        # clearing end date
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"end_date": None},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Cannot clear the Programme Cycle end date if it was previously set." in str(error.value)
        # end date before existing start date
        self.program.end_date = None
        self.program.save()
        self.cycle.start_date = datetime.strptime("2023-02-02", "%Y-%m-%d").date()
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"end_date": parse_date("2023-02-01")},
            context=self.get_serializer_context(),
        )
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)
        assert "Programme Cycle end date must be after the start date." in str(error.value)
        # no errors
        serializer = ProgramCycleUpdateSerializer(
            instance=self.cycle,
            data={"end_date": parse_date("2023-12-24")},
            context=self.get_serializer_context(),
        )
        assert serializer.is_valid()


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
        with pytest.raises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        assert context.value.detail[0] == "Only Programme Cycle for Active Programme can be deleted."  # type: ignore

    def test_delete_non_draft_cycle(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            cycle__status=ProgramCycle.ACTIVE,
        )
        cycle = program.cycles.first()
        with pytest.raises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        assert context.value.detail[0] == "Only Draft Programme Cycle can be deleted."  # type: ignore

    def test_delete_last_cycle(self) -> None:
        program = ProgramFactory(
            status=Program.ACTIVE,
            cycle__status=ProgramCycle.DRAFT,
        )
        cycle = program.cycles.first()
        with pytest.raises(ValidationError) as context:
            self.viewset.perform_destroy(cycle)
        assert context.value.detail[0] == "Don't allow to delete last Cycle."  # type: ignore

    def test_successful_delete(self) -> None:
        program = ProgramFactory(status=Program.ACTIVE)
        cycle1 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
        cycle2 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
        self.viewset.perform_destroy(cycle1)
        assert not ProgramCycle.objects.filter(id=cycle1.id).exists()
        assert ProgramCycle.objects.filter(id=cycle2.id).exists()
