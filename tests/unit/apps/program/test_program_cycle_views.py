"""Tests for program cycle REST API endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict

from django.urls import reverse
from django.utils.dateparse import parse_date
import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from extras.test_utils.old_factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.payment import PaymentPlanFactory
from extras.test_utils.old_factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.program.api.serializers import (
    ProgramCycleCreateSerializer,
    ProgramCycleUpdateSerializer,
)
from hope.apps.program.api.views import ProgramCycleViewSet
from hope.models import BusinessArea, Partner, PaymentPlan, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return create_afghanistan()


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        start_date="2023-01-01",
        end_date="2099-12-31",
        frequency_of_payments=Program.REGULAR,
    )
    cycle = program.cycles.first()
    cycle.title = "Default"
    cycle.status = ProgramCycle.ACTIVE
    cycle.start_date = "2023-01-02"
    cycle.end_date = "2023-01-10"
    cycle.save()
    return program


@pytest.fixture
def cycle1(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(
        program=program,
        title="Cycle 1",
        status=ProgramCycle.ACTIVE,
        start_date="2023-02-01",
        end_date="2023-02-20",
    )


@pytest.fixture
def cycle2(program: Program) -> ProgramCycle:
    return ProgramCycleFactory(
        program=program,
        title="RANDOM NAME",
        status=ProgramCycle.DRAFT,
        start_date="2023-05-01",
        end_date="2023-05-25",
    )


@pytest.fixture
def list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:cycles-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )


@pytest.fixture
def cycle_1_detail_url(afghanistan: BusinessArea, program: Program, cycle1: ProgramCycle) -> str:
    return reverse(
        "api:programs:cycles-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": str(cycle1.id),
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_list_program_cycles_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
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


def test_list_program_cycles_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrieve_program_cycle_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(cycle_1_detail_url)
    assert response.status_code == status.HTTP_200_OK


def test_retrieve_program_cycle_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(cycle_1_detail_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_program_cycle_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_CREATE],
        business_area=afghanistan,
        program=program,
    )

    data = {
        "title": "New Created Cycle",
        "start_date": parse_date("2024-05-26"),
    }
    response = authenticated_client.post(list_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert ProgramCycle.objects.count() == 4
    assert ProgramCycle.objects.last().title == "New Created Cycle"
    assert ProgramCycle.objects.last().end_date is None


def test_create_program_cycle_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    data = {
        "title": "New Created Cycle",
        "start_date": parse_date("2024-05-26"),
    }
    response = authenticated_client.post(list_url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_program_cycle_put_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        business_area=afghanistan,
        program=program,
    )

    data = {
        "title": "Updated Fully Title",
        "start_date": parse_date("2023-02-02"),
        "end_date": parse_date("2023-02-22"),
    }
    response = authenticated_client.put(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    cycle1.refresh_from_db()
    assert cycle1.title == "Updated Fully Title"
    assert cycle1.start_date.strftime("%Y-%m-%d") == "2023-02-02"
    assert cycle1.end_date.strftime("%Y-%m-%d") == "2023-02-22"


def test_update_program_cycle_patch_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        business_area=afghanistan,
        program=program,
    )

    data = {"title": "Title Title New", "start_date": parse_date("2023-02-11")}
    response = authenticated_client.patch(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    cycle1.refresh_from_db()
    assert cycle1.title == "Title Title New"
    assert cycle1.start_date.strftime("%Y-%m-%d") == "2023-02-11"


def test_update_program_cycle_put_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    data = {
        "title": "Updated Fully Title",
        "start_date": parse_date("2023-02-02"),
        "end_date": parse_date("2023-02-22"),
    }
    response = authenticated_client.put(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_program_cycle_patch_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    data = {"title": "Title Title New", "start_date": parse_date("2023-02-11")}
    response = authenticated_client.patch(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_cycle_dates_and_payment_plan(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        business_area=afghanistan,
        program=program,
    )

    payment_plan = PaymentPlanFactory(program_cycle=cycle1, start_date=None, end_date=None)
    assert payment_plan.start_date is None
    assert payment_plan.end_date is None

    # update only end_date
    data = {"end_date": parse_date("2023-02-22")}
    response = authenticated_client.patch(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    payment_plan.refresh_from_db()
    assert payment_plan.end_date.strftime("%Y-%m-%d") == "2023-02-22"
    assert payment_plan.start_date is None

    # update only start_date
    data = {"start_date": parse_date("2023-02-02")}
    response = authenticated_client.patch(cycle_1_detail_url, data, format="json")
    assert response.status_code == status.HTTP_200_OK
    payment_plan.refresh_from_db()
    assert payment_plan.start_date.strftime("%Y-%m-%d") == "2023-02-02"


def test_delete_program_cycle_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    cycle3 = ProgramCycleFactory(
        program=program,
        status=ProgramCycle.DRAFT,
    )
    # create PP
    pp = PaymentPlanFactory(program_cycle=cycle3)
    assert PaymentPlan.objects.count() == 1
    assert ProgramCycle.objects.count() == 4

    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_DELETE],
        business_area=afghanistan,
        program=program,
    )

    url = reverse(
        "api:programs:cycles-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": str(cycle3.id),
        },
    )

    bad_response = authenticated_client.delete(url)
    assert bad_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Don't allow to delete Cycle with assigned Target Population" in bad_response.data
    pp.delete(soft=False)

    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert ProgramCycle.objects.count() == 3
    assert PaymentPlan.objects.count() == 0


def test_delete_program_cycle_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    cycle3 = ProgramCycleFactory(
        program=program,
        status=ProgramCycle.DRAFT,
    )
    # create PP
    PaymentPlanFactory(program_cycle=cycle3)
    assert PaymentPlan.objects.count() == 1
    assert ProgramCycle.objects.count() == 4

    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        program=program,
    )

    url = reverse(
        "api:programs:cycles-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
            "pk": str(cycle3.id),
        },
    )

    bad_response = authenticated_client.delete(url)
    assert bad_response.status_code == status.HTTP_403_FORBIDDEN


def test_filter_by_status(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"status": "DRAFT"})
    assert ProgramCycle.objects.count() == 3
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["status"] == "Draft"


def test_filter_by_title_startswith(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"title": "Cycle"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Cycle 1"


def test_filter_by_start_date_gte(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"start_date": "2023-03-01"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["start_date"] == "2023-05-01"


def test_filter_by_end_date_lte(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"end_date": "2023-01-15"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["end_date"] == "2023-01-10"


def test_filter_by_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"program": str(program.pk)})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


def test_search_filter(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    list_url: str,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    response = authenticated_client.get(list_url, {"search": "Cycle 1"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Cycle 1"


def test_filter_total_delivered_quantity_usd(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    PaymentPlanFactory(program_cycle=cycle1, total_delivered_quantity_usd=Decimal("500.00"))
    PaymentPlanFactory(program_cycle=cycle2, total_delivered_quantity_usd=Decimal("1500.00"))
    cycle2.refresh_from_db()
    assert cycle2.total_delivered_quantity_usd == 1500
    response = authenticated_client.get(
        list_url,
        {
            "total_delivered_quantity_usd_from": "1000",
            "total_delivered_quantity_usd_to": "1900",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert str(response.data["results"][0]["total_delivered_quantity_usd"]) == "1500.00"


def test_filter_total_entitled_quantity_usd(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle2: ProgramCycle,
    list_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST],
        business_area=afghanistan,
        program=program,
    )

    PaymentPlanFactory(program_cycle=cycle1, total_entitled_quantity_usd=Decimal("750.00"))
    PaymentPlanFactory(program_cycle=cycle2, total_entitled_quantity_usd=Decimal("2000.00"))
    cycle2.refresh_from_db()
    assert cycle2.total_entitled_quantity_usd == 2000
    response = authenticated_client.get(
        list_url,
        {
            "total_entitled_quantity_usd_from": "1000",
            "total_entitled_quantity_usd_to": "2500",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert str(response.data["results"][0]["total_entitled_quantity_usd"]) == "2000.00"


def test_reactivate_program_cycle_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        business_area=afghanistan,
        program=program,
    )

    cycle1.status = ProgramCycle.FINISHED
    cycle1.save()

    cycle1.refresh_from_db()
    assert cycle1.status == ProgramCycle.FINISHED
    response = authenticated_client.post(cycle_1_detail_url + "reactivate/", {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    cycle1.refresh_from_db()
    assert cycle1.status == ProgramCycle.ACTIVE


def test_reactivate_program_cycle_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        program=program,
    )

    cycle1.status = ProgramCycle.FINISHED
    cycle1.save()

    cycle1.refresh_from_db()
    assert cycle1.status == ProgramCycle.FINISHED
    response = authenticated_client.post(cycle_1_detail_url + "reactivate/", {}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_finish_program_cycle_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PM_PROGRAMME_CYCLE_UPDATE],
        business_area=afghanistan,
        program=program,
    )

    PaymentPlanFactory(program_cycle=cycle1, status=PaymentPlan.Status.TP_OPEN)
    payment_plan = PaymentPlanFactory(program_cycle=cycle1, status=PaymentPlan.Status.IN_REVIEW)
    assert cycle1.status == ProgramCycle.ACTIVE
    assert payment_plan.status == PaymentPlan.Status.IN_REVIEW

    resp_error = authenticated_client.post(cycle_1_detail_url + "finish/", {}, format="json")
    assert resp_error.status_code == status.HTTP_400_BAD_REQUEST
    assert "All Payment Plans and Follow-Up Payment Plans have to be Reconciled." in resp_error.data

    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save()
    response = authenticated_client.post(cycle_1_detail_url + "finish/", {}, format="json")
    assert response.status_code == status.HTTP_200_OK
    cycle1.refresh_from_db()
    assert cycle1.status == ProgramCycle.FINISHED


def test_finish_program_cycle_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    cycle1: ProgramCycle,
    cycle_1_detail_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[],
        business_area=afghanistan,
        program=program,
    )

    PaymentPlanFactory(program_cycle=cycle1, status=PaymentPlan.Status.TP_OPEN)
    payment_plan = PaymentPlanFactory(program_cycle=cycle1, status=PaymentPlan.Status.IN_REVIEW)
    assert cycle1.status == ProgramCycle.ACTIVE
    assert payment_plan.status == PaymentPlan.Status.IN_REVIEW

    resp_error = authenticated_client.post(cycle_1_detail_url + "finish/", {}, format="json")
    assert resp_error.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def serializer_context(program: Program) -> Dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.get("/")
    user, _ = User.objects.get_or_create(
        username="MyUser",
        first_name="FirstName",
        last_name="LastName",
        password="PassworD",
    )
    request.user = user
    request.parser_context = {
        "kwargs": {
            "program_slug": str(program.slug),
            "business_area_slug": "afghanistan",
        }
    }
    return {"request": request}


def test_create_serializer_validate_title_unique(
    program: Program,
    serializer_context: Dict[str, Any],
) -> None:
    ProgramCycleFactory(program=program, title="Cycle 1")
    data = {
        "title": "Cycle 1",
        "start_date": parse_date("2033-01-02"),
        "end_date": parse_date("2033-01-12"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle title should be unique." in str(error.value)


def test_create_serializer_validate_if_no_end_date(
    program: Program,
    serializer_context: Dict[str, Any],
) -> None:
    ProgramCycleFactory(program=program, title="Cycle 1", end_date=None)
    data = {
        "title": "Cycle 123123",
        "start_date": parse_date("2025-01-02"),
        "end_date": parse_date("2025-01-12"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "All Programme Cycles must have an end date before creating a new one." in str(error.value)


def test_create_serializer_validate_program_status(
    program: Program,
    serializer_context: Dict[str, Any],
) -> None:
    program.status = Program.DRAFT
    program.save()
    data = {
        "title": "Cycle new",
        "start_date": program.start_date,
        "end_date": program.end_date,
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle can only be created for an Active Programme." in str(error.value)


def test_create_serializer_validate_start_date(
    program: Program,
    serializer_context: Dict[str, Any],
) -> None:
    # before program start date
    data = {
        "title": "Cycle 3",
        "start_date": parse_date("2022-01-01"),
        "end_date": parse_date("2023-01-01"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be between programme start and end dates." in str(error.value)

    # after program end date
    data = {
        "title": "Cycle 3",
        "start_date": parse_date("2100-01-01"),
        "end_date": parse_date("2100-01-11"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be between programme start and end dates." in str(error.value)

    # before latest cycle
    data = {
        "title": "Cycle 34567",
        "start_date": parse_date("2023-01-09"),
        "end_date": parse_date("2023-01-30"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Start date must be after the latest cycle end date." in str(error.value)

    # before program start date
    program.end_date = None
    program.save()
    data = {
        "title": "Cycle 3",
        "start_date": parse_date("2022-01-01"),
        "end_date": parse_date("2023-01-01"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date cannot be before programme start date." in str(error.value)

    # no error
    data = {
        "title": "Cycle new",
        "start_date": parse_date("2055-01-01"),
        "end_date": parse_date("2055-11-11"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    assert serializer.is_valid(raise_exception=True)


def test_create_serializer_validate_end_date(
    program: Program,
    serializer_context: Dict[str, Any],
) -> None:
    # after program end date
    data = {
        "title": "Cycle",
        "start_date": parse_date("2098-01-01"),
        "end_date": parse_date("2111-01-01"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle end date must be between programme start and end dates" in str(error.value)

    # before program start date
    data = {
        "title": "Cycle",
        "start_date": parse_date("2023-01-01"),
        "end_date": parse_date("2022-01-01"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "End date cannot be before start date." in str(error.value)

    # end before start date
    data = {
        "title": "Cycle",
        "start_date": parse_date("2023-02-22"),
        "end_date": parse_date("2023-02-11"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "End date cannot be before start date" in str(error.value)

    # no program end date and end date before program end date
    program.end_date = None
    program.save()
    data = {
        "title": "Cycle",
        "start_date": parse_date("2055-01-01"),
        "end_date": parse_date("2000-01-02"),
    }
    serializer = ProgramCycleCreateSerializer(data=data, context=serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle end date cannot be before programme start date." in str(error.value)


@pytest.fixture
def update_serializer_context(program: Program) -> Dict[str, Any]:
    factory = APIRequestFactory()
    request = factory.get("/")
    cycle = program.cycles.first()
    program_id = program.id
    request.parser_context = {"kwargs": {"program_id": program_id, "pk": str(cycle.id)}}
    return {"request": request}


def test_update_serializer_validate_title_unique(
    program: Program,
    update_serializer_context: Dict[str, Any],
) -> None:
    cycle = program.cycles.first()
    ProgramCycleFactory(program=program, title="Cycle 1")
    data = {"title": "Cycle 1 "}
    serializer = ProgramCycleUpdateSerializer(instance=cycle, data=data, context=update_serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle with this title already exists." in str(error.value)


def test_update_serializer_validate_program_status(
    program: Program,
    update_serializer_context: Dict[str, Any],
) -> None:
    cycle = program.cycles.first()
    program.status = Program.DRAFT
    program.save()
    data = {"title": "Cycle 2"}
    serializer = ProgramCycleUpdateSerializer(instance=cycle, data=data, context=update_serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Updating Programme Cycle is only possible for Active Programme." in str(error.value)


def test_update_serializer_validate_start_date(
    program: Program,
    update_serializer_context: Dict[str, Any],
) -> None:
    cycle = program.cycles.first()
    cycle.start_date = datetime.strptime("2023-01-02", "%Y-%m-%d").date()
    cycle.end_date = datetime.strptime("2023-12-10", "%Y-%m-%d").date()
    cycle.save()
    cycle_2 = ProgramCycleFactory(
        program=program,
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
    serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=update_serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "End date cannot be earlier than the start date." in str(error.value)

    data = {
        "start_date": parse_date("2023-12-10"),
        "end_date": parse_date("2023-12-26"),
    }
    serializer = ProgramCycleUpdateSerializer(instance=cycle_2, data=data, context=update_serializer_context)
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycles' timeframes must not overlap with the provided start date." in str(error.value)

    # before program start date (program with end_date)
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle_2,
        data={"start_date": parse_date("1999-12-10")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be within the programme's start and end dates" in str(error.value)

    # after program end date
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle_2,
        data={"start_date": parse_date("2100-01-01")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be within the programme's start and end dates." in str(error.value)

    # before program start date
    program.end_date = None
    program.save()
    cycle_2.refresh_from_db()
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle_2,
        data={"start_date": parse_date("2022-01-01")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be after the programme start date." in str(error.value)

    # start date after existing end date
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"start_date": parse_date("2023-12-26")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle start date must be before the end date." in str(error.value)

    # no error
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle_2,
        data={"start_date": parse_date("2023-12-24")},
        context=update_serializer_context,
    )
    assert serializer.is_valid()


def test_update_serializer_validate_end_date(
    program: Program,
    update_serializer_context: Dict[str, Any],
) -> None:
    cycle = program.cycles.first()
    cycle.end_date = datetime.strptime("2023-02-03", "%Y-%m-%d").date()
    cycle.save()

    # end date before program start date
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"end_date": parse_date("1999-10-10")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle end date must be within the programme's start and end dates." in str(error.value)

    # end date after program end date
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"end_date": parse_date("2100-10-10")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle end date must be within the programme's start and end dates." in str(error.value)

    # clearing end date
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"end_date": None},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Cannot clear the Programme Cycle end date if it was previously set." in str(error.value)

    # end date before existing start date
    program.end_date = None
    program.save()
    cycle.start_date = datetime.strptime("2023-02-02", "%Y-%m-%d").date()
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"end_date": parse_date("2023-02-01")},
        context=update_serializer_context,
    )
    with pytest.raises(ValidationError) as error:
        serializer.is_valid(raise_exception=True)
    assert "Programme Cycle end date must be after the start date." in str(error.value)

    # no errors
    serializer = ProgramCycleUpdateSerializer(
        instance=cycle,
        data={"end_date": parse_date("2023-12-24")},
        context=update_serializer_context,
    )
    assert serializer.is_valid()


def test_viewset_delete_non_active_program() -> None:
    BusinessAreaFactory(name="Afghanistan")
    viewset = ProgramCycleViewSet()
    program = ProgramFactory(
        status=Program.DRAFT,
        cycle__status=ProgramCycle.DRAFT,
    )
    cycle = program.cycles.first()
    with pytest.raises(ValidationError) as context:
        viewset.perform_destroy(cycle)
    assert context.value.detail[0] == "Only Programme Cycle for Active Programme can be deleted."  # type: ignore


def test_viewset_delete_non_draft_cycle() -> None:
    BusinessAreaFactory(name="Afghanistan")
    viewset = ProgramCycleViewSet()
    program = ProgramFactory(
        status=Program.ACTIVE,
        cycle__status=ProgramCycle.ACTIVE,
    )
    cycle = program.cycles.first()
    with pytest.raises(ValidationError) as context:
        viewset.perform_destroy(cycle)
    assert context.value.detail[0] == "Only Draft Programme Cycle can be deleted."  # type: ignore


def test_viewset_delete_last_cycle() -> None:
    BusinessAreaFactory(name="Afghanistan")
    viewset = ProgramCycleViewSet()
    program = ProgramFactory(
        status=Program.ACTIVE,
        cycle__status=ProgramCycle.DRAFT,
    )
    cycle = program.cycles.first()
    with pytest.raises(ValidationError) as context:
        viewset.perform_destroy(cycle)
    assert context.value.detail[0] == "Don't allow to delete last Cycle."  # type: ignore


def test_viewset_successful_delete() -> None:
    BusinessAreaFactory(name="Afghanistan")
    viewset = ProgramCycleViewSet()
    program = ProgramFactory(status=Program.ACTIVE)
    cycle1 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    cycle2 = ProgramCycleFactory(program=program, status=ProgramCycle.DRAFT)
    viewset.perform_destroy(cycle1)
    assert not ProgramCycle.objects.filter(id=cycle1.id).exists()
    assert ProgramCycle.objects.filter(id=cycle2.id).exists()
