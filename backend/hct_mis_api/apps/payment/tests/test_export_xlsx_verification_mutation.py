from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import PaymentVerificationPlanFactory, CashPlanFactory
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory


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
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.user = UserFactory()

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        cash_plan = CashPlanFactory(program=program, business_area=cls.business_area)
        cash_plan.save()
        cls.payment_verification_plan = PaymentVerificationPlanFactory(
            generic_fk_obj=cash_plan,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_EXPORT]),
            ("without_permission", []),
        ]
    )
    def test_export_xlsx_cash_plan_payment_verification(self, _, permissions):
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
