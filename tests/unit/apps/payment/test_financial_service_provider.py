from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    generate_delivery_mechanisms,
)

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import DeliveryMechanism, FinancialServiceProvider


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
                    deliveryMechanisms {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                    communicationChannel
                    distributionLimit
                    xlsxTemplates {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
            }
        }
    }
    """

    BUSINESS_AREA_SLUG = "afghanistan"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create()
        permissions = [
            Permissions.PM_LOCK_AND_UNLOCK_FSP,
        ]
        cls.create_user_role_with_permissions(
            cls.user, permissions, BusinessArea.objects.get(slug=cls.BUSINESS_AREA_SLUG)
        )
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(name="TestName123")
        fsps = FinancialServiceProviderFactory.create_batch(
            9,
            distribution_limit=9999,
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        for fsp in fsps:
            fsp.allowed_business_areas.add(cls.business_area)
            fsp.delivery_mechanisms.add(cls.dm_cash)
            FspXlsxTemplatePerDeliveryMechanismFactory(
                financial_service_provider=fsp,
                xlsx_template=fsp_xlsx_template,
            )

    def test_fetch_count_financial_service_providers(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_COUNT_ALL_FSP_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )

    def test_fetch_all_financial_service_providers(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_LIST_ALL_FSP_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
