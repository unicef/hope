from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import FinancialServiceProvider, GenericPayment


QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATES = """
query AllFinancialServiceProviderXlsxTemplates(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $name: String
    $createdBy: ID
    $orderBy: String
) {
allFinancialServiceProviderXlsxTemplates(
        offset: $offset
        before: $before
        after: $after
        first: $first
        last: $last
        name: $name
        createdBy: $createdBy
        orderBy: $orderBy
    ) {
 edges {
        node {
            name
            columns
        }
    }
}
}
"""


class TestPaymentSchema(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        # Generate FinancialServiceProviders
        cls.fsp_1 = FinancialServiceProviderFactory(
            name="FSP_1",
            vision_vendor_number="149-69-3686",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_CASH],
            distribution_limit=10_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        cls.fsp_2 = FinancialServiceProviderFactory(
            name="FSP_2",
            vision_vendor_number="666-69-3686",
            delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_VOUCHER],
            distribution_limit=20_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        )

        # Generate FinancialServiceProvidersXlsxTemplates
        cls.fsp_xlsx_template_1 = FinancialServiceProviderXlsxTemplateFactory(
            name="FSP_template_1", columns=["column_1", "column_2"]
        )
        cls.fsp_xlsx_template_2 = FinancialServiceProviderXlsxTemplateFactory(
            name="FSP_template_2", columns=["column_3", "column_4"]
        )

        # Generate FspXlsxTemplatePerDeliveryMechanismFactory
        cls.fsp_xlsx_template_per_delivery_mechanism_1 = FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_1,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
            xlsx_template=cls.fsp_xlsx_template_1,
        )
        cls.fsp_xlsx_template_per_delivery_mechanism_2 = FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_2,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CHEQUE,
            xlsx_template=cls.fsp_xlsx_template_2,
        )

        cls.delivery_mechanism_per_payment_plan_factory_1 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=PaymentPlanFactory(),
            financial_service_provider=cls.fsp_1,
            created_by=cls.user,
            sent_by=cls.user,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
            delivery_mechanism_order=1,
        )
        cls.delivery_mechanism_per_payment_plan_factory_2 = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=PaymentPlanFactory(),
            financial_service_provider=cls.fsp_2,
            created_by=cls.user,
            sent_by=cls.user,
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH_BY_FSP,
            delivery_mechanism_order=2,
        )

    def test_query_all_fsp_xlsx_templates(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATES,
            context={"user": self.user}
        )

