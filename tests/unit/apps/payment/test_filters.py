from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    generate_delivery_mechanisms,
)

from hope.models.business_area import BusinessArea
from hope.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
)


class TestFinancialServiceProviderXlsxTemplateFilter(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.dm_voucher = DeliveryMechanism.objects.get(code="voucher")
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        # Generate FinancialServiceProviders
        cls.fsp_1 = FinancialServiceProviderFactory(
            name="FSP_1",
            vision_vendor_number="149-69-111",
            distribution_limit=10_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        cls.fsp_1.allowed_business_areas.add(cls.business_area)
        cls.fsp_1.delivery_mechanisms.add(cls.dm_cash)
        cls.fsp_1.delivery_mechanisms.add(cls.dm_voucher)
        cls.fsp_2 = FinancialServiceProviderFactory(
            name="FSP_2",
            vision_vendor_number="666-69-111",
            distribution_limit=20_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        cls.fsp_2.allowed_business_areas.add(cls.business_area)
        cls.fsp_2.delivery_mechanisms.add(cls.dm_voucher)

        # Generate FinancialServiceProvidersXlsxTemplates the same template for two DM
        cls.fsp_xlsx_template_1 = FinancialServiceProviderXlsxTemplateFactory(
            name="FSP_template_1", columns=["column_1", "column_2"]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_1,
            delivery_mechanism=cls.dm_cash,
            xlsx_template=cls.fsp_xlsx_template_1,
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_1,
            delivery_mechanism=cls.dm_voucher,
            xlsx_template=cls.fsp_xlsx_template_1,
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_2,
            delivery_mechanism=cls.dm_voucher,
            xlsx_template=cls.fsp_xlsx_template_1,
        )

    def test_xlsx_template_business_area_filter_distinct(self) -> None:
        from hope.apps.payment.filters import FinancialServiceProviderXlsxTemplateFilter

        """
        even if FSP has multiple DM and the same xlsx template assigned
         only one template should be returned due to .distinct()
        """
        data = {"business_area": "afghanistan"}
        queryset = FinancialServiceProviderXlsxTemplate.objects.all()
        filtered_qs = FinancialServiceProviderXlsxTemplateFilter(data=data, queryset=queryset).qs

        assert filtered_qs.count() == 1
        assert filtered_qs.first() == self.fsp_xlsx_template_1
