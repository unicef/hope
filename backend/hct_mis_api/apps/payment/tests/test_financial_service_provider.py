from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory, FinancialServiceProviderXlsxTemplateFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan


class TestAllFinancialServiceProviders(APITestCase):
    QUERY_COUNT_ALL_FSP_QUERY = """
    query CountFinancialServiceProviders {
        allFinancialServiceProviders {
            totalCount
            edgeCount
        }
    }
    """

    QUERY_LIST_ALL_FSP_QUERY = """
    query AllFinancialServiceProviders {
        allFinancialServiceProviders {
            edges {
                node {
                    id
                    createdAt
                    fspXlsxTemplate {
                        id
                        name
                        # columns
                    }
                    financialserviceproviderxlsxreportSet {
                        edges {
                            node {
                                id
                                status
                                reportUrl
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    MUTATION_CREATE_FSP = """
    mutation CreateFSP(
        $businessAreaSlug: String!
        $input: CreateFinancialServiceProviderInput!
    ) {
        createFinancialServiceProvider(
            businessAreaSlug: $businessAreaSlug
            input: $input
        ) {
            financialServiceProvider {
                id
                name
                visionVendorNumber
                deliveryMechanisms
                communicationChannel
                distributionLimit
            }
        }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.FINANCIAL_SERVICE_PROVIDER_VIEW_LIST_AND_DETAILS], BusinessArea.objects.get(slug="afghanistan")
        )
        FinancialServiceProviderFactory.create_batch(10)

    def test_fetch_count_financial_service_providers(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_COUNT_ALL_FSP_QUERY,
            context={"user": self.user},
            variables={
                # "businessArea": "afghanistan",
            },
        )

    def test_fetch_all_financial_service_providers(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST_ALL_FSP_QUERY,
            context={"user": self.user},
            variables={
                # "businessArea": "afghanistan",
            },
        )
    
    def test_create_financial_service_provider(self):
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory.create()
        self.snapshot_graphql_request(
            request_string=self.MUTATION_CREATE_FSP,
            context={"user": self.user},
            variables={
                "businessAreaSlug": "afghanistan",
                "input": {
                    "name": "XYZ Bank",
                    "visionVendorNumber": "XYZB-123456789",
                    "delivery_mechanisms": "email",
                    "distributionLimit": "123456789",
                    "communicationChannel": "XLSX",
                    "fspXlsxTemplateId": fsp_xlsx_template.id,
                },
            },
        )
