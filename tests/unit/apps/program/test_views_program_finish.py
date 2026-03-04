"""Tests for program finish API endpoint."""

import datetime
from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Partner, PaymentPlan, Program, ProgramCycle, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner(db: Any) -> Partner:
    return PartnerFactory(name="Test Partner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    program = ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="Test Program For Finish",
        start_date=datetime.date(2031, 1, 1),
        end_date=datetime.date(2033, 12, 31),
    )
    # There cannot be any active cycles for the program to finish
    for cycle in program.cycles.filter(status=ProgramCycle.ACTIVE):
        cycle.status = ProgramCycle.FINISHED
        cycle.save()
    return program


@pytest.fixture
def finish_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-finish",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_finish_program_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    assert program.status == Program.ACTIVE
    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.status == Program.FINISHED
    assert response.json() == {"message": "Program Finished."}


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
    ],
)
def test_finish_program_without_permission(
    permissions: list,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, whole_business_area_access=True)

    assert program.status == Program.ACTIVE
    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    program.refresh_from_db()
    assert program.status == Program.ACTIVE


def test_finish_program_already_finished(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    program.status = Program.FINISHED
    program.save()

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only active Program can be finished." in response.json()

    program.refresh_from_db()
    assert program.status == Program.FINISHED


def test_finish_program_invalid_status_draft(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    program.status = Program.DRAFT
    program.save()

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only active Program can be finished." in response.json()

    program.refresh_from_db()
    assert program.status == Program.DRAFT


def test_finish_program_without_end_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    program.end_date = None
    program.save()

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot finish programme without end date." in response.json()

    program.refresh_from_db()
    assert program.status == Program.ACTIVE


def test_finish_program_with_active_cycles(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramCycleFactory(program=program, status=ProgramCycle.ACTIVE)

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot finish Program with active cycles." in response.json()

    program.refresh_from_db()
    assert program.status == Program.ACTIVE


def test_finish_program_with_unreconciled_payment_plans(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    program_cycle = ProgramCycleFactory(
        program=program,
        status=ProgramCycle.FINISHED,
    )

    PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.IN_REVIEW,
    )

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "All Payment Plans and Follow-Up Payment Plans have to be Reconciled." in response.json()

    program.refresh_from_db()
    assert program.status == Program.ACTIVE


def test_finish_program_with_reconciled_payment_plans(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    finish_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_FINISH],
        afghanistan,
        whole_business_area_access=True,
    )

    program_cycle = ProgramCycleFactory(
        program=program,
        status=ProgramCycle.FINISHED,
    )

    PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.ACCEPTED,
    )
    PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.FINISHED,
    )
    PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.TP_LOCKED,
    )

    response = authenticated_client.post(finish_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Program Finished."}

    program.refresh_from_db()
    assert program.status == Program.FINISHED
