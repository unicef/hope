from io import BytesIO
from pathlib import Path

from parameterized import parameterized
from django.conf import settings
from django.core.files import File

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import AdminArea, BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import (
    CashPlanPaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, XlsxCashPlanPaymentVerificationFile
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory


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
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        program.admin_areas_new.set(Area.objects.order_by("?")[:3])

        cash_plan = CashPlanFactory(program=program, business_area=cls.business_area)
        cash_plan.save()
        cls.cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            cash_plan=cash_plan,
            verification_channel=CashPlanPaymentVerification.VERIFICATION_CHANNEL_XLSX,
            status=CashPlanPaymentVerification.STATUS_ACTIVE,
        )
        cls.content = Path(f"{settings.PROJECT_ROOT}/apps/core/tests/test_files/flex_updated.xls").read_bytes()
        cls.xlsx_file = XlsxCashPlanPaymentVerificationFile.objects.create(
            file=File(BytesIO(cls.content), name="flex_updated.xls"),
            cash_plan_payment_verification=cls.cash_plan_payment_verification,
            created_by=None,
        )

    @parameterized.expand(
        [
            ("with_permission_was_downloaded_false", [Permissions.PAYMENT_VERIFICATION_INVALID], False),
            ("with_permission_was_downloaded_true", [Permissions.PAYMENT_VERIFICATION_INVALID], True),
            ("without_permission", [], True),
        ]
    )
    def test_export_xlsx_cash_plan_payment_verification(self, _, permissions, download_status):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.xlsx_file.was_downloaded = download_status
        self.xlsx_file.save()

        self.snapshot_graphql_request(
            request_string=self.INVALID_MUTATION,
            context={"user": self.user},
            variables={
                "cashPlanVerificationId": self.id_to_base64(
                    self.cash_plan_payment_verification.id, "CashPlanPaymentVerificationNode"
                ),
            },
        )
