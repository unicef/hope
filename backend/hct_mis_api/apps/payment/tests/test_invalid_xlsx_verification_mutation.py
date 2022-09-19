from io import BytesIO
from pathlib import Path

from parameterized import parameterized

from django.conf import settings
from django.core.files import File

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import (
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerificationPlan, XlsxPaymentVerificationPlanFile
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestXlsxVerificationMarkAsInvalid(APITestCase):

    INVALID_MUTATION = """
        mutation invalidCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
          invalidCashPlanPaymentVerification(cashPlanVerificationId: $cashPlanVerificationId) {
            cashPlan{
              verifications{
                edges{
                  node{
                    status
                    xlsxFileImported
                    xlsxFileExporting
                    xlsxFileWasDownloaded
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
            cash_plan=cash_plan,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )
        cls.content = Path(f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/flex_updated.xls").read_bytes()
        cls.xlsx_file = XlsxPaymentVerificationPlanFile.objects.create(
            file=File(BytesIO(cls.content), name="flex_updated.xls"),
            payment_verification_plan=cls.payment_verification_plan,
            created_by=None,
        )

    @parameterized.expand(
        [
            ("with_permission_was_downloaded_false", [Permissions.PAYMENT_VERIFICATION_INVALID], False),
            ("with_permission_was_downloaded_true", [Permissions.PAYMENT_VERIFICATION_INVALID], True),
            ("without_permission", [], True),
        ]
    )
    def test_export_xlsx_payment_verification_plan(self, _, permissions, download_status):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.xlsx_file.was_downloaded = download_status
        self.xlsx_file.save()

        self.snapshot_graphql_request(
            request_string=self.INVALID_MUTATION,
            context={"user": self.user},
            # TODO: upd vars after update intups
            variables={
                "cashPlanVerificationId": self.id_to_base64(
                    self.payment_verification_plan.id, "PaymentVerificationPlanNode"
                ),
            },
        )
