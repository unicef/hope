"""Query-count profiling for the payee-list endpoint (ticket 311246).

Seeds a payment plan with PAYEE_COUNT households (each with members, primary
and alternate collectors, documents, and a materialized PaymentHouseholdSnapshot),
hits the list endpoint, and captures the actual SQL queries.

Prints a query-shape breakdown so N+1 hotspots are visible, then asserts a
ceiling. The first run is expected to fail — the failure message tells us the
actual query count. After the fix lands, update QUERY_CEILING to the new
baseline and this becomes a regression guard for the behaviour Nikola asked for.
"""

from collections import Counter
from typing import Any

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
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
QUERY_CEILING = 30


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program_active(business_area: Any) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def cycle(program_active: Program) -> Any:
    return ProgramCycleFactory(program=program_active, title="Perf Test Cycle")


@pytest.fixture
def fsp() -> Any:
    return FinancialServiceProviderFactory(
        name="Perf FSP",
        vision_vendor_number="999",
        communication_channel="XLSX",
    )


@pytest.fixture
def large_payment_plan(
    business_area: Any,
    user: Any,
    program_active: Program,
    cycle: Any,
    fsp: Any,
) -> PaymentPlan:
    payment_plan = PaymentPlanFactory(
        name="Perf test PP",
        business_area=business_area,
        program_cycle=cycle,
        status=PaymentPlan.Status.LOCKED,
        created_by=user,
        financial_service_provider=fsp,
    )
    for _ in range(PAYEE_COUNT):
        household = HouseholdFactory(
            business_area=business_area,
            program=program_active,
            size=HOUSEHOLD_SIZE,
            create_role=False,
        )
        head = household.head_of_household
        rdi = head.registration_data_import
        IndividualFactory.create_batch(
            HOUSEHOLD_SIZE - 1,
            household=household,
            business_area=business_area,
            program=program_active,
            registration_data_import=rdi,
        )
        DocumentFactory(individual=head, program=program_active)
        primary = IndividualFactory(
            household=None,
            business_area=business_area,
            program=program_active,
            registration_data_import=rdi,
        )
        alternate = IndividualFactory(
            household=None,
            business_area=business_area,
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


def _shape(sql: str) -> str:
    return " ".join(sql.strip().split()[:6])


def _format_query_counts(queries: list[dict]) -> str:
    counter = Counter(_shape(q["sql"]) for q in queries)
    return "\n".join(f"{count:5d}  {shape}" for shape, count in counter.most_common(30))


def test_payee_list_query_count(
    api_client: Any,
    business_area: Any,
    user: Any,
    program_active: Program,
    large_payment_plan: PaymentPlan,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_active,
    )
    client = api_client(user)
    url = reverse(
        "api:payments:payments-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_active.code,
            "payment_plan_pk": large_payment_plan.pk,
        },
    )

    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == PAYEE_COUNT

    total = len(ctx.captured_queries)
    breakdown = _format_query_counts(ctx.captured_queries)
    assert total <= QUERY_CEILING, (
        f"\nPayee-list query count: {total} (ceiling: {QUERY_CEILING}) "
        f"for {PAYEE_COUNT} rows\n\n"
        f"Top query shapes:\n{breakdown}\n"
    )
