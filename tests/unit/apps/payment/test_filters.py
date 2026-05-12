from base64 import b64encode
from datetime import date, datetime, timezone as tz
from decimal import Decimal
from uuid import uuid4

from django.http import Http404
import pytest

from extras.test_utils.factories.activity_log import LogEntryFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.filters import (
    FinancialServiceProviderFilter,
    FinancialServiceProviderXlsxTemplateFilter,
    PaymentFilter,
    PaymentPlanFilter,
    PaymentVerificationFilter,
    PaymentVerificationLogEntryFilter,
    PaymentVerificationPlanFilter,
    PaymentVerificationSummaryFilter,
)
from hope.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    Individual,
    LogEntry,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def delivery_mechanisms():
    dm_cash = DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")
    dm_voucher = DeliveryMechanismFactory(code="voucher", name="Voucher", payment_gateway_id="dm-voucher")
    return {"cash": dm_cash, "voucher": dm_voucher}


@pytest.fixture
def template(business_area, delivery_mechanisms):
    fsp_1 = FinancialServiceProviderFactory(
        name="FSP_1",
        vision_vendor_number="149-69-111",
        distribution_limit=10_000,
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    fsp_1.allowed_business_areas.add(business_area)
    fsp_1.delivery_mechanisms.add(delivery_mechanisms["cash"], delivery_mechanisms["voucher"])

    fsp_2 = FinancialServiceProviderFactory(
        name="FSP_2",
        vision_vendor_number="666-69-111",
        distribution_limit=20_000,
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
    )
    fsp_2.allowed_business_areas.add(business_area)
    fsp_2.delivery_mechanisms.add(delivery_mechanisms["voucher"])

    template = FinancialServiceProviderXlsxTemplateFactory(name="FSP_template_1", columns=["column_1", "column_2"])

    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanisms["cash"],
        xlsx_template=template,
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanisms["voucher"],
        xlsx_template=template,
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_2,
        delivery_mechanism=delivery_mechanisms["voucher"],
        xlsx_template=template,
    )

    return template


def test_payment_filter_order_by_created_at(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    older = PaymentFactory(parent=plan)
    newer = PaymentFactory(parent=plan)

    Payment.objects.filter(pk=older.pk).update(created_at=datetime(2023, 1, 1, tzinfo=tz.utc))
    Payment.objects.filter(pk=newer.pk).update(created_at=datetime(2023, 6, 1, tzinfo=tz.utc))

    qs = Payment.objects.filter(parent=plan)

    asc = PaymentFilter(data={"business_area": business_area.slug, "order_by": "created_at"}, queryset=qs).qs
    assert list(asc.values_list("pk", flat=True)) == [older.pk, newer.pk]

    desc = PaymentFilter(data={"business_area": business_area.slug, "order_by": "-created_at"}, queryset=qs).qs
    assert list(desc.values_list("pk", flat=True)) == [newer.pk, older.pk]


def test_xlsx_template_business_area_filter_distinct(business_area, template):
    """
    even if FSP has multiple DM and the same xlsx template assigned
     only one template should be returned due to .distinct()
    """
    data = {"business_area": business_area.slug}
    queryset = FinancialServiceProviderXlsxTemplate.objects.all()
    filtered_qs = FinancialServiceProviderXlsxTemplateFilter(data=data, queryset=queryset).qs

    assert filtered_qs.count() == 1
    assert filtered_qs.first() == template


# ---------------------------------------------------------------------------
# PaymentOrderingFilter
# ---------------------------------------------------------------------------


def test_payment_ordering_filter_orders_by_mark_ascending(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    p_pending = PaymentFactory(parent=plan)
    p_success = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=p_success.pk).update(status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    qs = Payment.objects.filter(parent=plan)
    ordered = PaymentFilter(data={"business_area": business_area.slug, "order_by": "mark"}, queryset=qs).qs

    assert list(ordered.values_list("pk", flat=True)) == [p_success.pk, p_pending.pk]


def test_payment_ordering_filter_orders_by_mark_descending(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    p_pending = PaymentFactory(parent=plan)
    p_success = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=p_success.pk).update(status=Payment.STATUS_DISTRIBUTION_SUCCESS)

    qs = Payment.objects.filter(parent=plan)
    ordered = PaymentFilter(data={"business_area": business_area.slug, "order_by": "-mark"}, queryset=qs).qs

    assert list(ordered.values_list("pk", flat=True)) == [p_pending.pk, p_success.pk]


# ---------------------------------------------------------------------------
# PaymentVerificationFilter
# ---------------------------------------------------------------------------


@pytest.fixture
def verification_setup(business_area):
    plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    pvp = PaymentVerificationPlanFactory(payment_plan=plan)
    pv = PaymentVerificationFactory(payment_verification_plan=pvp)
    return {"plan": plan, "pvp": pvp, "pv": pv}


def test_payment_verification_filter_search_matches_payment_unicef_id(business_area, verification_setup):
    Payment.objects.filter(pk=verification_setup["pv"].payment.pk).update(unicef_id="PMT-DEADBEEF")
    other_pv = PaymentVerificationFactory(payment_verification_plan=verification_setup["pvp"])
    Payment.objects.filter(pk=other_pv.payment.pk).update(unicef_id="PMT-OTHER")

    qs = PaymentVerification.objects.filter(payment_verification_plan=verification_setup["pvp"])
    filtered = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "search": "PMT-DEAD"},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_search_matches_individual_phone(business_area, verification_setup):
    payment = verification_setup["pv"].payment
    head = payment.household.head_of_household
    Payment.objects.filter(pk=payment.pk).update(head_of_household_id=head.pk)
    Individual.objects.filter(pk=head.pk).update(phone_no="+48555000111", phone_no_alternative="+48555999000")

    qs = PaymentVerification.objects.filter(payment_verification_plan=verification_setup["pvp"])
    by_primary = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "search": "+48555000"},
        queryset=qs,
    ).qs
    by_alternative = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "search": "+48555999"},
        queryset=qs,
    ).qs

    assert list(by_primary.values_list("pk", flat=True)) == [verification_setup["pv"].pk]
    assert list(by_alternative.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_search_handles_multiple_words(business_area, verification_setup):
    payment = verification_setup["pv"].payment
    head = payment.household.head_of_household
    Payment.objects.filter(pk=payment.pk).update(head_of_household_id=head.pk)
    Individual.objects.filter(pk=head.pk).update(family_name="Kowalski", given_name="Jan")

    qs = PaymentVerification.objects.filter(payment_verification_plan=verification_setup["pvp"])
    filtered = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "search": "Jan Kowalski"},
        queryset=qs,
    ).qs

    assert filtered.count() == 1
    assert filtered.first().pk == verification_setup["pv"].pk


def test_payment_verification_filter_payment_plan_id_decodes_base64(business_area, verification_setup):
    other_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    other_pvp = PaymentVerificationPlanFactory(payment_plan=other_plan)
    PaymentVerificationFactory(payment_verification_plan=other_pvp)

    encoded = b64encode(f"PaymentPlanNode:{verification_setup['plan'].pk}".encode()).decode()
    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "payment_plan_id": encoded},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_business_area_filters_by_slug(business_area, verification_setup):
    other_ba = BusinessAreaFactory(slug="ukraine")
    other_plan = PaymentPlanFactory(business_area=other_ba, status=PaymentPlan.Status.FINISHED)
    other_pvp = PaymentVerificationPlanFactory(payment_plan=other_plan)
    PaymentVerificationFactory(payment_verification_plan=other_pvp)

    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_by_verification_channel(business_area, verification_setup):
    rapidpro_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    rapidpro_pvp = PaymentVerificationPlanFactory(
        payment_plan=rapidpro_plan,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
    )
    PaymentVerificationFactory(payment_verification_plan=rapidpro_pvp)

    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(
        data={
            "business_area": business_area.slug,
            "verification_channel": PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_by_status(business_area, verification_setup):
    received_pv = PaymentVerificationFactory(payment_verification_plan=verification_setup["pvp"])
    PaymentVerification.objects.filter(pk=received_pv.pk).update(status=PaymentVerification.STATUS_RECEIVED)

    qs = PaymentVerification.objects.filter(payment_verification_plan=verification_setup["pvp"])
    filtered = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "status": PaymentVerification.STATUS_PENDING},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [verification_setup["pv"].pk]


def test_payment_verification_filter_order_by_received_amount(business_area, verification_setup):
    high = PaymentVerificationFactory(payment_verification_plan=verification_setup["pvp"])
    PaymentVerification.objects.filter(pk=verification_setup["pv"].pk).update(received_amount=Decimal("10.00"))
    PaymentVerification.objects.filter(pk=high.pk).update(received_amount=Decimal("999.00"))

    qs = PaymentVerification.objects.filter(payment_verification_plan=verification_setup["pvp"])
    asc = PaymentVerificationFilter(
        data={"business_area": business_area.slug, "order_by": "received_amount"},
        queryset=qs,
    ).qs

    assert list(asc.values_list("pk", flat=True)) == [verification_setup["pv"].pk, high.pk]


# ---------------------------------------------------------------------------
# PaymentVerificationPlanFilter
# ---------------------------------------------------------------------------


def test_payment_verification_plan_filter_by_program_id(business_area):
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentPlanFactory(business_area=business_area, program_cycle=cycle, status=PaymentPlan.Status.FINISHED)
    pvp = PaymentVerificationPlanFactory(payment_plan=plan)

    other_program = ProgramFactory(business_area=business_area)
    other_cycle = ProgramCycleFactory(program=other_program)
    other_plan = PaymentPlanFactory(
        business_area=business_area, program_cycle=other_cycle, status=PaymentPlan.Status.FINISHED
    )
    PaymentVerificationPlanFactory(payment_plan=other_plan)

    qs = PaymentVerificationPlan.objects.all()
    filtered = PaymentVerificationPlanFilter(data={"program_id": str(program.id)}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [pvp.pk]


# ---------------------------------------------------------------------------
# PaymentVerificationSummaryFilter
# ---------------------------------------------------------------------------


def test_payment_verification_summary_filter_returns_all(business_area):
    plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    summary = PaymentVerificationSummary.objects.get(payment_plan=plan)

    qs = PaymentVerificationSummary.objects.all()
    filtered = PaymentVerificationSummaryFilter(data={}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [summary.pk]


# ---------------------------------------------------------------------------
# PaymentVerificationLogEntryFilter
# ---------------------------------------------------------------------------


@pytest.mark.enable_activity_log
def test_payment_verification_log_entry_filter_object_id(business_area):
    plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    pvp_a = PaymentVerificationPlanFactory(payment_plan=plan)
    pvp_b = PaymentVerificationPlanFactory(payment_plan=plan)
    matching_a = LogEntryFactory(business_area=business_area, object_id=pvp_a.pk)
    matching_b = LogEntryFactory(business_area=business_area, object_id=pvp_b.pk)
    LogEntryFactory(business_area=business_area, object_id=uuid4())

    qs = LogEntry.objects.all()
    filtered = PaymentVerificationLogEntryFilter(data={"object_id": str(plan.pk)}, queryset=qs).qs

    assert set(filtered.values_list("pk", flat=True)) == {matching_a.pk, matching_b.pk}


# ---------------------------------------------------------------------------
# FinancialServiceProviderXlsxTemplateFilter
# ---------------------------------------------------------------------------


def test_xlsx_template_filter_by_name():
    keep = FinancialServiceProviderXlsxTemplateFactory(name="Alpha")
    FinancialServiceProviderXlsxTemplateFactory(name="Beta")

    qs = FinancialServiceProviderXlsxTemplate.objects.all()
    filtered = FinancialServiceProviderXlsxTemplateFilter(data={"name": "Alpha"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


# ---------------------------------------------------------------------------
# FinancialServiceProviderFilter
# ---------------------------------------------------------------------------


def test_fsp_filter_by_name():
    keep = FinancialServiceProviderFactory(name="Wanted FSP")
    FinancialServiceProviderFactory(name="Other FSP")

    qs = FinancialServiceProvider.objects.all()
    filtered = FinancialServiceProviderFilter(data={"name": "Wanted FSP"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_fsp_filter_by_vision_vendor_number():
    keep = FinancialServiceProviderFactory(vision_vendor_number="VN-MATCH")
    FinancialServiceProviderFactory(vision_vendor_number="VN-OTHER")

    qs = FinancialServiceProvider.objects.all()
    filtered = FinancialServiceProviderFilter(data={"vision_vendor_number": "VN-MATCH"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_fsp_filter_order_by_lower_name():
    fsp_b = FinancialServiceProviderFactory(name="banana FSP")
    fsp_a = FinancialServiceProviderFactory(name="Apple FSP")
    fsp_c = FinancialServiceProviderFactory(name="Cherry FSP")

    qs = FinancialServiceProvider.objects.filter(pk__in=[fsp_a.pk, fsp_b.pk, fsp_c.pk])
    ordered = FinancialServiceProviderFilter(data={"order_by": "name"}, queryset=qs).qs

    assert [obj.name for obj in ordered] == ["Apple FSP", "banana FSP", "Cherry FSP"]


# ---------------------------------------------------------------------------
# PaymentPlanFilter
# ---------------------------------------------------------------------------


def test_payment_plan_filter_business_area_required(business_area):
    plan_in = PaymentPlanFactory(business_area=business_area)
    other_ba = BusinessAreaFactory(slug="ukraine")
    PaymentPlanFactory(business_area=other_ba)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [plan_in.pk]


def test_payment_plan_filter_search_by_name(business_area):
    keep = PaymentPlanFactory(business_area=business_area, name="HopePlan-001")
    PaymentPlanFactory(business_area=business_area, name="OtherPlan")

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "search": "HopePlan"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_status_with_assigned_pseudo_value(business_area):
    locked = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.LOCKED)
    finished = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "status": ["ASSIGNED"]}, queryset=qs).qs

    assert set(filtered.values_list("pk", flat=True)) == {locked.pk, finished.pk}


def test_payment_plan_filter_status_without_assigned(business_area):
    open_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.LOCKED)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "status": [PaymentPlan.Status.OPEN]}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [open_plan.pk]


def test_payment_plan_filter_status_not(business_area):
    open_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.ABORTED)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "status_not": PaymentPlan.Status.ABORTED}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [open_plan.pk]


def test_payment_plan_filter_verification_status(business_area):
    plan_active = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    plan_other = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.FINISHED)
    PaymentVerificationSummary.objects.filter(payment_plan=plan_active).update(
        status=PaymentVerificationSummary.STATUS_ACTIVE
    )
    PaymentVerificationSummary.objects.filter(payment_plan=plan_other).update(
        status=PaymentVerificationSummary.STATUS_FINISHED
    )

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "verification_status": [PaymentVerificationSummary.STATUS_ACTIVE],
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [plan_active.pk]


def test_payment_plan_filter_total_entitled_quantity_from_to(business_area):
    low = PaymentPlanFactory(business_area=business_area, total_entitled_quantity=Decimal("100.00"))
    mid = PaymentPlanFactory(business_area=business_area, total_entitled_quantity=Decimal("500.00"))
    PaymentPlanFactory(business_area=business_area, total_entitled_quantity=Decimal("1000.00"))

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "total_entitled_quantity_from": "100",
            "total_entitled_quantity_to": "500",
        },
        queryset=qs,
    ).qs

    assert set(filtered.values_list("pk", flat=True)) == {low.pk, mid.pk}


def test_payment_plan_filter_dispersion_dates(business_area):
    keep = PaymentPlanFactory(
        business_area=business_area,
        dispersion_start_date=date(2024, 6, 1),
        dispersion_end_date=date(2024, 6, 30),
    )
    PaymentPlanFactory(
        business_area=business_area,
        dispersion_start_date=date(2024, 1, 1),
        dispersion_end_date=date(2024, 1, 31),
    )

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "dispersion_start_date": "2024-05-01",
            "dispersion_end_date": "2024-07-31",
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_start_end_dates(business_area):
    keep = PaymentPlanFactory(
        business_area=business_area,
        start_date=datetime(2024, 6, 1, tzinfo=tz.utc),
        end_date=datetime(2024, 6, 30, tzinfo=tz.utc),
    )
    PaymentPlanFactory(
        business_area=business_area,
        start_date=datetime(2024, 1, 1, tzinfo=tz.utc),
        end_date=datetime(2024, 1, 31, tzinfo=tz.utc),
    )

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "start_date": "2024-05-01",
            "end_date": "2024-07-31",
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_is_follow_up(business_area):
    follow_up = PaymentPlanFactory(business_area=business_area, plan_type=PaymentPlan.PlanType.FOLLOW_UP)
    PaymentPlanFactory(business_area=business_area, plan_type=PaymentPlan.PlanType.REGULAR)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "plan_type": "FOLLOW_UP"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [follow_up.pk]


def test_payment_plan_filter_is_payment_plan_true_excludes_pre_payment(business_area):
    real_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "is_payment_plan": "true"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [real_plan.pk]


def test_payment_plan_filter_is_payment_plan_false_returns_unchanged(business_area):
    open_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    draft_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "is_payment_plan": "false"}, queryset=qs).qs

    assert set(filtered.values_list("pk", flat=True)) == {open_plan.pk, draft_plan.pk}


def test_payment_plan_filter_is_target_population_true_keeps_pre_payment(business_area):
    draft_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)
    PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "is_target_population": "true"}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [draft_plan.pk]


def test_payment_plan_filter_is_target_population_false_returns_unchanged(business_area):
    open_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    draft_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "is_target_population": "false"}, queryset=qs
    ).qs

    assert set(filtered.values_list("pk", flat=True)) == {open_plan.pk, draft_plan.pk}


def test_payment_plan_filter_source_payment_plan_id(business_area):
    source = PaymentPlanFactory(business_area=business_area)
    follow_up = PaymentPlanFactory(business_area=business_area, source_payment_plan=source)
    PaymentPlanFactory(business_area=business_area)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "source_payment_plan_id": str(source.pk)},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [follow_up.pk]


def test_payment_plan_filter_by_program(business_area):
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    keep = PaymentPlanFactory(business_area=business_area, program_cycle=cycle)
    PaymentPlanFactory(business_area=business_area)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "program": str(program.id)}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_by_program_cycle(business_area):
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    other_cycle = ProgramCycleFactory(program=program)
    keep = PaymentPlanFactory(business_area=business_area, program_cycle=cycle)
    PaymentPlanFactory(business_area=business_area, program_cycle=other_cycle)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "program_cycle": str(cycle.id)}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_name_startswith(business_area):
    keep = PaymentPlanFactory(business_area=business_area, name="HopePlan-001")
    PaymentPlanFactory(business_area=business_area, name="MyHopePlan-002")

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "name": "Hope"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_total_households_count_min_max(business_area):
    plan_small = PaymentPlanFactory(business_area=business_area)
    plan_large = PaymentPlanFactory(business_area=business_area)
    PaymentFactory(parent=plan_small)
    PaymentFactory(parent=plan_large)
    PaymentFactory(parent=plan_large)
    PaymentFactory(parent=plan_large)

    qs = PaymentPlan.objects.all()
    min_filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "total_households_count_min": "2"}, queryset=qs
    ).qs
    max_filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "total_households_count_max": "2"}, queryset=qs
    ).qs

    assert list(min_filtered.values_list("pk", flat=True)) == [plan_large.pk]
    assert list(max_filtered.values_list("pk", flat=True)) == [plan_small.pk]


def test_payment_plan_filter_total_households_count_with_valid_phone_no_max(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    valid_payment = PaymentFactory(parent=plan)
    invalid_payment = PaymentFactory(parent=plan)

    Individual.objects.filter(pk=valid_payment.household.head_of_household.pk).update(phone_no_valid=True)
    Individual.objects.filter(pk=invalid_payment.household.head_of_household.pk).update(
        phone_no_valid=False, phone_no_alternative_valid=False
    )

    qs = PaymentPlan.objects.all()
    matched = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "total_households_count_with_valid_phone_no_max": "1",
        },
        queryset=qs,
    ).qs
    excluded = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "total_households_count_with_valid_phone_no_max": "0",
        },
        queryset=qs,
    ).qs

    assert plan.pk in matched.values_list("pk", flat=True)
    assert plan.pk not in excluded.values_list("pk", flat=True)


def test_payment_plan_filter_total_households_count_with_valid_phone_no_min(business_area):
    plan_with_one_valid = PaymentPlanFactory(business_area=business_area)
    plan_without_valid = PaymentPlanFactory(business_area=business_area)

    valid_payment = PaymentFactory(parent=plan_with_one_valid)
    invalid_payment = PaymentFactory(parent=plan_without_valid)

    Individual.objects.filter(pk=valid_payment.household.head_of_household.pk).update(phone_no_alternative_valid=True)
    Individual.objects.filter(pk=invalid_payment.household.head_of_household.pk).update(
        phone_no_valid=False, phone_no_alternative_valid=False
    )

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "total_households_count_with_valid_phone_no_min": "1",
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [plan_with_one_valid.pk]


def test_payment_plan_filter_created_at_range(business_area):
    keep = PaymentPlanFactory(business_area=business_area)
    older = PaymentPlanFactory(business_area=business_area)
    PaymentPlan.objects.filter(pk=keep.pk).update(created_at=datetime(2024, 6, 15, tzinfo=tz.utc))
    PaymentPlan.objects.filter(pk=older.pk).update(created_at=datetime(2023, 1, 1, tzinfo=tz.utc))

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={
            "business_area": business_area.slug,
            "created_at_after": "2024-01-01",
            "created_at_before": "2024-12-31",
        },
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_service_provider(business_area):
    fsp = FinancialServiceProviderFactory(name="Western Union")
    other_fsp = FinancialServiceProviderFactory(name="MoneyGram")
    keep = PaymentPlanFactory(business_area=business_area, financial_service_provider=fsp)
    PaymentPlanFactory(business_area=business_area, financial_service_provider=other_fsp)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "service_provider": "Western Union"},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_delivery_types(business_area, delivery_mechanisms):
    keep = PaymentPlanFactory(business_area=business_area, delivery_mechanism=delivery_mechanisms["cash"])
    PaymentPlanFactory(business_area=business_area, delivery_mechanism=delivery_mechanisms["voucher"])

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "delivery_types": ["cash"]},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_plan_filter_default_order_by_created_at_desc(business_area):
    older = PaymentPlanFactory(business_area=business_area)
    newer = PaymentPlanFactory(business_area=business_area)
    PaymentPlan.objects.filter(pk=older.pk).update(created_at=datetime(2023, 1, 1, tzinfo=tz.utc))
    PaymentPlan.objects.filter(pk=newer.pk).update(created_at=datetime(2024, 6, 1, tzinfo=tz.utc))

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [newer.pk, older.pk]


def test_payment_plan_filter_explicit_order_by_skips_default(business_area):
    plan_a = PaymentPlanFactory(business_area=business_area, name="AAA")
    plan_z = PaymentPlanFactory(business_area=business_area, name="ZZZ")
    PaymentPlan.objects.filter(pk=plan_a.pk).update(created_at=datetime(2023, 1, 1, tzinfo=tz.utc))
    PaymentPlan.objects.filter(pk=plan_z.pk).update(created_at=datetime(2024, 6, 1, tzinfo=tz.utc))

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data={"business_area": business_area.slug, "order_by": "name"}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [plan_a.pk, plan_z.pk]


# ---------------------------------------------------------------------------
# PaymentFilter
# ---------------------------------------------------------------------------


def test_payment_filter_business_area_filters_by_parent(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    other_ba = BusinessAreaFactory(slug="ukraine")
    other_plan = PaymentPlanFactory(business_area=other_ba)
    payment_in = PaymentFactory(parent=plan)
    PaymentFactory(parent=other_plan)

    qs = Payment.objects.all()
    filtered = PaymentFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [payment_in.pk]


def test_payment_filter_payment_plan_id_open_excludes_excluded(business_area):
    plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    keep = PaymentFactory(parent=plan)
    excluded = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=excluded.pk).update(excluded=True)

    qs = Payment.objects.all()
    filtered = PaymentFilter(
        data={"business_area": business_area.slug, "payment_plan_id": str(plan.pk)},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_filter_payment_plan_id_non_open_calls_eligible(business_area):
    plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.LOCKED)
    keep = PaymentFactory(parent=plan)
    conflicted = PaymentFactory(parent=plan)
    excluded = PaymentFactory(parent=plan)
    no_wallet = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=conflicted.pk).update(conflicted=True)
    Payment.objects.filter(pk=excluded.pk).update(excluded=True)
    Payment.objects.filter(pk=no_wallet.pk).update(has_valid_wallet=False)

    qs = Payment.objects.all()
    filtered = PaymentFilter(
        data={"business_area": business_area.slug, "payment_plan_id": str(plan.pk)},
        queryset=qs,
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_filter_payment_plan_id_404_when_missing(business_area):
    qs = Payment.objects.all()

    with pytest.raises(Http404):
        PaymentFilter(
            data={"business_area": business_area.slug, "payment_plan_id": str(uuid4())},
            queryset=qs,
        ).qs.count()


def test_payment_filter_by_program_id(business_area):
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentPlanFactory(business_area=business_area, program_cycle=cycle)
    other_plan = PaymentPlanFactory(business_area=business_area)
    keep = PaymentFactory(parent=plan)
    PaymentFactory(parent=other_plan)

    qs = Payment.objects.all()
    filtered = PaymentFilter(data={"business_area": business_area.slug, "program_id": str(program.id)}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


def test_payment_filter_by_household_id_excludes_pre_payment_plan_statuses(business_area):
    real_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.OPEN)
    draft_plan = PaymentPlanFactory(business_area=business_area, status=PaymentPlan.Status.DRAFT)
    household = HouseholdFactory(business_area=business_area)
    keep = PaymentFactory(parent=real_plan, household=household)
    PaymentFactory(parent=draft_plan, household=household)

    qs = Payment.objects.all()
    filtered = PaymentFilter(
        data={"business_area": business_area.slug, "household_id": str(household.id)}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [keep.pk]


@pytest.mark.parametrize(
    ("status", "expected_mark"),
    [
        (Payment.STATUS_DISTRIBUTION_SUCCESS, 1),
        (Payment.STATUS_DISTRIBUTION_PARTIAL, 2),
        (Payment.STATUS_NOT_DISTRIBUTED, 3),
        (Payment.STATUS_ERROR, 4),
        (Payment.STATUS_FORCE_FAILED, 5),
        (Payment.STATUS_MANUALLY_CANCELLED, 6),
        (Payment.STATUS_PENDING, 7),
    ],
)
def test_payment_filter_queryset_annotates_mark(business_area, status, expected_mark):
    plan = PaymentPlanFactory(business_area=business_area)
    payment = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=payment.pk).update(status=status)

    qs = Payment.objects.filter(parent=plan)
    filtered = PaymentFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert filtered.values_list("mark", flat=True).first() == expected_mark


def test_payment_filter_queryset_default_order_by_created_at_desc(business_area):
    plan = PaymentPlanFactory(business_area=business_area)
    older = PaymentFactory(parent=plan)
    newer = PaymentFactory(parent=plan)
    Payment.objects.filter(pk=older.pk).update(created_at=datetime(2023, 1, 1, tzinfo=tz.utc))
    Payment.objects.filter(pk=newer.pk).update(created_at=datetime(2024, 6, 1, tzinfo=tz.utc))

    qs = Payment.objects.filter(parent=plan)
    filtered = PaymentFilter(data={"business_area": business_area.slug}, queryset=qs).qs

    assert list(filtered.values_list("pk", flat=True)) == [newer.pk, older.pk]


def test_payment_plan_filter_by_payment_plan_group(business_area):
    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanGroupFactory(cycle=cycle)
    other_group = PaymentPlanGroupFactory(cycle=cycle)
    pp = PaymentPlanFactory(business_area=business_area, program_cycle=cycle, payment_plan_group=group)
    PaymentPlanFactory(business_area=business_area, program_cycle=cycle, payment_plan_group=other_group)

    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(
        data={"business_area": business_area.slug, "payment_plan_group": str(group.id)}, queryset=qs
    ).qs

    assert list(filtered.values_list("pk", flat=True)) == [pp.pk]
