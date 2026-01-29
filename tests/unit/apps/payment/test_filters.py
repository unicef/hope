import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
)
from hope.models import FinancialServiceProvider, FinancialServiceProviderXlsxTemplate

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
