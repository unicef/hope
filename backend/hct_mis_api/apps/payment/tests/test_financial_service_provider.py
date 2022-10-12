from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
)


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
                    fspXlsxTemplate {
                        name
                    }
                    financialserviceproviderxlsxreportSet {
                        edges {
                            node {
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
        $inputs: CreateFinancialServiceProviderInput!
    ) {
        createFinancialServiceProvider(
            businessAreaSlug: $businessAreaSlug
            inputs: $inputs
        ) {
            financialServiceProvider {
                name
                visionVendorNumber
                deliveryMechanisms {
                }
                communicationChannel
                distributionLimit
                fspXlsxTemplate {
                    name
                    createdBy {
                        username
                        firstName
                    }
                }
            }
        }
    }
    """

    MUTATION_UPDATE_FSP = """
    mutation UpdateFSP (
        $financialServiceProviderId: ID!
        $businessAreaSlug: String!
        $inputs: CreateFinancialServiceProviderInput!
    ) {
        editFinancialServiceProvider (
            financialServiceProviderId: $financialServiceProviderId
            businessAreaSlug: $businessAreaSlug
            inputs: $inputs
        ) {
            financialServiceProvider {
                name
                visionVendorNumber
                deliveryMechanisms {
                }
                communicationChannel
                distributionLimit
                fspXlsxTemplate {
                    name
                    createdBy {
                        username
                        firstName
                    }
                }
            }
        }
    }
    """

    BUSINESS_AREA_SLUG = "afghanistan"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        permissions = [
            Permissions.FINANCIAL_SERVICE_PROVIDER_VIEW_LIST_AND_DETAILS,
            Permissions.FINANCIAL_SERVICE_PROVIDER_CREATE,
            Permissions.FINANCIAL_SERVICE_PROVIDER_UPDATE,
        ]
        cls.create_user_role_with_permissions(
            cls.user, permissions, BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG)
        )
        FinancialServiceProviderFactory.create_batch(
            10, fsp_xlsx_template=FinancialServiceProviderXlsxTemplateFactory(name="TestName123")
        )

    def test_fetch_count_financial_service_providers(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_COUNT_ALL_FSP_QUERY,
            context={"user": self.user},
        )

    def test_fetch_all_financial_service_providers(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST_ALL_FSP_QUERY,
            context={"user": self.user},
        )

    def test_create_financial_service_provider(self):
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory.create()

        self.graphql_request(
            request_string=self.MUTATION_CREATE_FSP,
            context={"user": self.user},
            variables={
                "businessAreaSlug": self.BUSINESS_AREA_SLUG,
                "inputs": {
                    "name": "Web3 Bank",
                    "visionVendorNumber": "XYZB-123456789",
                    "deliveryMechanisms": {"Cash", "Mobile Money"},
                    "distributionLimit": "123456789",
                    "communicationChannel": "XLSX",
                    "fspXlsxTemplateId": encode_id_base64(fsp_xlsx_template.id, "FinancialServiceProviderXlsxTemplate"),
                },
            },
        )

    def test_update_financial_service_provider(self):
        fsp = FinancialServiceProviderFactory.create()
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory.create()

        self.graphql_request(
            request_string=self.MUTATION_UPDATE_FSP,
            context={"user": self.user},
            variables={
                "financialServiceProviderId": encode_id_base64(fsp.id, "FinancialServiceProvider"),
                "businessAreaSlug": self.BUSINESS_AREA_SLUG,
                "inputs": {
                    "name": "New Gen Bank",
                    "visionVendorNumber": "XYZB-123456789",
                    "deliveryMechanisms": ["Transfer"],
                    "distributionLimit": "123456789",
                    "communicationChannel": "XLSX",
                    "fspXlsxTemplateId": encode_id_base64(fsp_xlsx_template.id, "FinancialServiceProviderXlsxTemplate"),
                },
            },
        )
