from typing import Any, List

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.models import PaymentVerificationPlan


class TestXlsxVerificationExport(APITestCase):
    EXPORT_MUTATION = """
        mutation exportXlsxPaymentVerificationPlanFile($paymentVerificationPlanId: ID!) {
          exportXlsxPaymentVerificationPlanFile(paymentVerificationPlanId: $paymentVerificationPlanId) {
            paymentPlan{
              verificationPlans{
                edges{
                  node{
                    status
                    xlsxFileImported
                    xlsxFileExporting
                    xlsxFileWasDownloaded
                    hasXlsxFile
                  }
                }
              }
            }
          }
        }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.user = UserFactory()

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            business_area=cls.business_area,
            created_by=cls.user,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        cls.payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=payment_plan,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_EXPORT]),
            ("without_permission", []),
        ]
    )
    def test_export_xlsx_cash_plan_payment_verification(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.EXPORT_MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": self.id_to_base64(
                    self.payment_verification_plan.id, "PaymentVerificationPlanNode"
                ),
            },
        )
