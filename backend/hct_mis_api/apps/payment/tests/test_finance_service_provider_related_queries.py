from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxReportFactory,
    FinancialServiceProviderXlsxTemplateFactory,
)
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    GenericPayment,
)

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
            deliveryMechanisms
            communicationChannel
        }
    }
  }
}
"""

QUERY_FINANCIAL_SERVICE_PROVIDER_XLSX_REPORT = """
query financialServiceProviderXlsxReport($id: ID!) {
financialServiceProviderXlsxReport(id: $id) {
    status
    financialServiceProvider {
        name
    }
}
}
"""

QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_REPORTS = """
query AllFinancialServiceProviderXlsxReports(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $orderBy: String
) {
allFinancialServiceProviderXlsxReports(
        offset: $offset
        before: $before
        after: $after
        first: $first
        last: $last
        orderBy: $orderBy
    ) {
edges {
        node {
            status
            financialServiceProvider {
                name
            }
        }
    }
}
}
"""


class TestFSPRelatedSchema(APITestCase):
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

        # Generate FinancialServiceProviderXlsxReports
        cls.financial_service_provider_xlsx_report_1 = FinancialServiceProviderXlsxReportFactory(
            status=FinancialServiceProviderXlsxReport.COMPLETED, financial_service_provider=cls.fsp_1
        )
        cls.financial_service_provider_xlsx_report_2 = FinancialServiceProviderXlsxReportFactory(
            status=FinancialServiceProviderXlsxReport.IN_PROGRESS, financial_service_provider=cls.fsp_2
        )

    def test_query_all_financial_service_provider_xlsx_templates(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATES, context={"user": self.user}
        )

    def test_query_all_financial_service_providers(self) -> None:
        self.snapshot_graphql_request(request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDERS, context={"user": self.user})

    def test_query_all_financial_service_provider_xlsx_reports(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_ALL_FINANCIAL_SERVICE_PROVIDER_XLSX_REPORTS, context={"user": self.user}
        )

    def test_query_single_financial_service_provider(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_FINANCIAL_SERVICE_PROVIDER,
            context={"user": self.user},
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

    def test_query_single_financial_service_provider_xlsx_report(self) -> None:
        self.snapshot_graphql_request(
            request_string=QUERY_FINANCIAL_SERVICE_PROVIDER_XLSX_REPORT,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.financial_service_provider_xlsx_report_1.id, "FinancialServiceProviderXlsxReportNode"
                )
            },
        )
