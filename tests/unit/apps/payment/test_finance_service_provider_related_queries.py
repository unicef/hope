from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    generate_delivery_mechanisms,
)

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import DeliveryMechanism, FinancialServiceProvider

QUERY_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATE = """
query financialServiceProviderXlsxTemplate($id:ID!) {
  financialServiceProviderXlsxTemplate(id:$id) {
    name
    columns
  }
}
"""

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
    $businessArea: String!
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
        businessArea: $businessArea
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

QUERY_FINANCIAL_SERVICE_PROVIDER = """
query FinancialServiceProvider($id:ID!) {
  financialServiceProvider(id:$id) {
    name
    visionVendorNumber
    distributionLimit
  }
}
"""

QUERY_ALL_FINANCIAL_SERVICE_PROVIDERS = """
query allFinancialServiceProviders(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $createdBy: ID
    $name: String
    $visionVendorNumber: String
    $deliveryMechanisms: [String]
    $distributionLimit: Float
    $communicationChannel: String
    $xlsxTemplates: [ID]
    $orderBy: String
) {
allFinancialServiceProviders(
    offset: $offset
    before: $before
    after: $after
    first: $first
    last: $last
    createdBy: $createdBy
    name: $name
    visionVendorNumber: $visionVendorNumber
    deliveryMechanisms: $deliveryMechanisms
    distributionLimit: $distributionLimit
    communicationChannel: $communicationChannel
    xlsxTemplates: $xlsxTemplates
    orderBy: $orderBy
) {
    edges {
        node {
            name,
            visionVendorNumber
            deliveryMechanisms {
                edges {
                    node {
                        name
                    }
                }
            }
            communicationChannel
        }
    }
  }
}
"""


class TestFSPRelatedSchema(APITestCase):
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
            vision_vendor_number="149-69-3686",
            distribution_limit=10_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        cls.fsp_1.allowed_business_areas.add(cls.business_area)
        cls.fsp_1.delivery_mechanisms.add(cls.dm_cash)
        cls.fsp_2 = FinancialServiceProviderFactory(
            name="FSP_2",
            vision_vendor_number="666-69-3686",
            distribution_limit=20_000,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        )
        cls.fsp_2.allowed_business_areas.add(cls.business_area)
        cls.fsp_2.delivery_mechanisms.add(cls.dm_voucher)

        # Generate FinancialServiceProvidersXlsxTemplates
        cls.fsp_xlsx_template_1 = FinancialServiceProviderXlsxTemplateFactory(
            name="FSP_template_1", columns=["column_1", "column_2"]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_1, delivery_mechanism=cls.dm_cash, xlsx_template=cls.fsp_xlsx_template_1
        )
        cls.fsp_xlsx_template_2 = FinancialServiceProviderXlsxTemplateFactory(
            name="FSP_template_2", columns=["column_3", "column_4"]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=cls.fsp_2,
            delivery_mechanism=cls.dm_voucher,
            xlsx_template=cls.fsp_xlsx_template_2,
        )

    def test_query_all_financial_service_provider_xlsx_templates(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATES,
            context={"user": self.user},
            variables={"businessArea": self.business_area.slug},
        )

    def test_query_all_financial_service_providers(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDERS,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"orderBy": "name"},
        )

    def test_query_single_financial_service_provider(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_FINANCIAL_SERVICE_PROVIDER,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"id": self.id_to_base64(self.fsp_1.id, "FinancialServiceProviderNode")},
        )

    def test_query_single_financial_service_provider_xlsx_template(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATE,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(self.fsp_xlsx_template_1.id, "FinancialServiceProviderXlsxTemplateNode")
            },
        )
