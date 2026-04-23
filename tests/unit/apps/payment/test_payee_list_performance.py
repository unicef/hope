from collections import Counter
from typing import Any

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    DocumentFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hope.models import MergeStatusModel, Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db

PAYEE_COUNT = 50
HOUSEHOLD_SIZE = 4


@pytest.fixture
def program_active(afghanistan: Any) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def authorized_user(
    afghanistan: Any,
    program_active: Program,
    create_user_role_with_permissions: Any,
) -> Any:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        afghanistan,
        program_active,
    )
    return user


@pytest.fixture
def large_payment_plan(
    afghanistan: Any,
    authorized_user: Any,
    program_active: Program,
) -> PaymentPlan:
    cycle = ProgramCycleFactory(program=program_active, title="Perf Test Cycle")
    fsp = FinancialServiceProviderFactory(
        name="Perf FSP",
        vision_vendor_number="999",
        communication_channel="XLSX",
    )
    payment_plan = PaymentPlanFactory(
        name="Perf test PP",
        business_area=afghanistan,
        program_cycle=cycle,
        status=PaymentPlan.Status.LOCKED,
        created_by=authorized_user,
        financial_service_provider=fsp,
    )
    for _ in range(PAYEE_COUNT):
        household = HouseholdFactory(
            business_area=afghanistan,
            program=program_active,
            size=HOUSEHOLD_SIZE,
            create_role=False,
        )
        head = household.head_of_household
        rdi = head.registration_data_import
        IndividualFactory.create_batch(
            HOUSEHOLD_SIZE - 1,
            household=household,
            business_area=afghanistan,
            program=program_active,
            registration_data_import=rdi,
        )
        DocumentFactory(individual=head, program=program_active)
        primary = IndividualFactory(
            household=None,
            business_area=afghanistan,
            program=program_active,
            registration_data_import=rdi,
        )
        alternate = IndividualFactory(
            household=None,
            business_area=afghanistan,
            program=program_active,
            registration_data_import=rdi,
        )
        IndividualRoleInHouseholdFactory(
            household=household,
            individual=primary,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        IndividualRoleInHouseholdFactory(
            household=household,
            individual=alternate,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        PaymentFactory(
            parent=payment_plan,
            program=program_active,
            financial_service_provider=fsp,
            household=household,
            head_of_household=head,
            collector=primary,
            status=Payment.STATUS_PENDING,
        )
    create_payment_plan_snapshot_data(payment_plan)
    return payment_plan


@pytest.fixture
def payee_list_url(
    afghanistan: Any,
    program_active: Program,
    large_payment_plan: PaymentPlan,
) -> str:
    return reverse(
        "api:payments:payments-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_code": program_active.code,
            "payment_plan_pk": large_payment_plan.pk,
        },
    )


def _shape(sql: str) -> str:
    return " ".join(sql.strip().split()[:6])


def _format_query_counts(queries: list[dict]) -> str:
    counter = Counter(_shape(q["sql"]) for q in queries)
    return "\n".join(f"{count:5d}  {shape}" for shape, count in counter.most_common(30))


def test_payee_list_query_count(
    api_client: Any,
    authorized_user: Any,
    payee_list_url: str,
) -> None:
    client = api_client(authorized_user)

    with CaptureQueriesContext(connection) as ctx:
        response = client.get(payee_list_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == PAYEE_COUNT

    total = len(ctx.captured_queries)
    breakdown = _format_query_counts(ctx.captured_queries)
    assert total <= 30, (
        f"\nPayee-list query count: {total} (ceiling: 30) for {PAYEE_COUNT} rows\n\nTop query shapes:\n{breakdown}\n"
    )
