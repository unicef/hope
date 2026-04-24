from base64 import b64encode

import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
)
from hope.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    PaymentPlan,
    PaymentVerification,
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


def test_xlsx_template_business_area_filter_distinct(business_area, template):
    """
    even if FSP has multiple DM and the same xlsx template assigned
     only one template should be returned due to .distinct()
    """
    from hope.apps.payment.filters import FinancialServiceProviderXlsxTemplateFilter

    data = {"business_area": business_area.slug}
    queryset = FinancialServiceProviderXlsxTemplate.objects.all()
    filtered_qs = FinancialServiceProviderXlsxTemplateFilter(data=data, queryset=queryset).qs

    assert filtered_qs.count() == 1
    assert filtered_qs.first() == template


# --- Phase 2: Payment Record ID (iexact) ---


def test_payment_record_id_iexact_match(
    payment_verification_pr_42, payment_verification_pr_99, django_assert_num_queries
):
    from hope.apps.payment.filters import PaymentVerificationFilter

    ba_slug = payment_verification_pr_42.payment.business_area.slug
    data = {"search": "PR-0000042", "business_area": ba_slug}
    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(data=data, queryset=qs).qs
    with django_assert_num_queries(1):
        result = list(filtered)
    assert result == [payment_verification_pr_42]


def test_payment_record_id_partial_prefix_does_not_match(payment_verification_pr_42, payment_verification_pr_99):
    from hope.apps.payment.filters import PaymentVerificationFilter

    ba_slug = payment_verification_pr_42.payment.business_area.slug
    data = {"search": "PR-000004", "business_area": ba_slug}
    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(data=data, queryset=qs).qs
    assert list(filtered) == []


def test_payment_record_id_case_insensitive(payment_verification_pr_42, payment_verification_pr_99):
    from hope.apps.payment.filters import PaymentVerificationFilter

    ba_slug = payment_verification_pr_42.payment.business_area.slug
    data = {"search": "pr-0000042", "business_area": ba_slug}
    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(data=data, queryset=qs).qs
    assert list(filtered) == [payment_verification_pr_42]


def test_payment_verification_plan_id_iexact_still_works(payment_verification_pr_42):
    from hope.apps.payment.filters import PaymentVerificationFilter

    pvp = payment_verification_pr_42.payment_verification_plan
    pvp.unicef_id = "PVP-0000010"
    pvp.save(update_fields=["unicef_id"])

    ba_slug = payment_verification_pr_42.payment.business_area.slug
    qs = PaymentVerification.objects.all()

    data_full = {"search": "PVP-0000010", "business_area": ba_slug}
    assert list(PaymentVerificationFilter(data=data_full, queryset=qs).qs) == [payment_verification_pr_42]

    data_partial = {"search": "PVP-000001", "business_area": ba_slug}
    assert list(PaymentVerificationFilter(data=data_partial, queryset=qs).qs) == []


def test_payment_household_unicef_id_iexact_still_works(payment_verification_pr_42):
    from hope.apps.payment.filters import PaymentVerificationFilter

    hh = payment_verification_pr_42.payment.household
    hh.unicef_id = "HH-0000077"
    hh.save(update_fields=["unicef_id"])

    ba_slug = payment_verification_pr_42.payment.business_area.slug
    qs = PaymentVerification.objects.all()

    data_full = {"search": "HH-0000077", "business_area": ba_slug}
    assert list(PaymentVerificationFilter(data=data_full, queryset=qs).qs) == [payment_verification_pr_42]

    data_partial = {"search": "HH-000007", "business_area": ba_slug}
    assert list(PaymentVerificationFilter(data=data_partial, queryset=qs).qs) == []


# --- Phase 2: Payment Plan ID icontains (production filter) ---


def test_payment_plan_unicef_id_icontains_match(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "0000001", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered
    assert payment_plan_other not in filtered


def test_payment_plan_unicef_id_icontains_case_insensitive(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "pp-0000001", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered


def test_payment_plan_id_icontains_on_uuid(payment_plan_with_cycle):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    uuid_substring = str(payment_plan_with_cycle.id)[:8]
    data = {"search": uuid_substring, "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered


# --- Phase 2: Payment Plan Name icontains (production filter) ---


def test_payment_plan_name_icontains_middle_word(
    payment_plan_with_cycle, payment_plan_other, django_assert_num_queries
):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "Relief", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    with django_assert_num_queries(1):
        result = list(filtered)
    assert payment_plan_with_cycle in result
    assert payment_plan_other not in result


def test_payment_plan_name_icontains_case_insensitive(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "relief", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered


# --- Phase 2: Programme Cycle Title icontains (production filter) ---


def test_programme_cycle_title_icontains_middle_word(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "Cash", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered
    assert payment_plan_other not in filtered


def test_programme_cycle_title_icontains_case_insensitive(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "cash", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered


def test_programme_cycle_title_no_match(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import PaymentPlanFilter

    data = {"search": "xyz", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = PaymentPlanFilter(data=data, queryset=qs).qs
    assert list(filtered) == []


# --- Phase 2: Inheritance (production filter subclasses) ---


def test_target_population_filter_inherits_search(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.api.filters import TargetPopulationFilter

    data = {"search": "Relief", "business_area": payment_plan_with_cycle.business_area.slug}
    qs = PaymentPlan.objects.all()
    filtered = TargetPopulationFilter(data=data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered
    assert payment_plan_other not in filtered


# --- Phase 2: Legacy filter smoke test + scope guard ---


def test_legacy_payment_plan_search_matches_api_filter_behavior(payment_plan_with_cycle, payment_plan_other):
    from hope.apps.payment.filters import PaymentPlanFilter

    qs = PaymentPlan.objects.all()

    name_data = {"search": "Relief", "business_area": payment_plan_with_cycle.business_area.slug}
    filtered_by_name = PaymentPlanFilter(data=name_data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered_by_name

    cycle_data = {"search": "Cash", "business_area": payment_plan_with_cycle.business_area.slug}
    filtered_by_cycle = PaymentPlanFilter(data=cycle_data, queryset=qs).qs
    assert payment_plan_with_cycle in filtered_by_cycle


def test_payment_plan_filter_method_untouched(payment_verification_pr_42):
    from hope.apps.payment.filters import PaymentVerificationFilter

    pvp = payment_verification_pr_42.payment_verification_plan
    pp = pvp.payment_plan
    relay_id = b64encode(f"PaymentPlanNode:{pp.id}".encode()).decode()

    ba_slug = pp.business_area.slug
    data = {"payment_plan_id": relay_id, "business_area": ba_slug}
    qs = PaymentVerification.objects.all()
    filtered = PaymentVerificationFilter(data=data, queryset=qs).qs
    assert payment_verification_pr_42 in filtered
