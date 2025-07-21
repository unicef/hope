from io import BytesIO
from pathlib import Path
from typing import Any, List

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

from parameterized import parameterized

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.geo.models import Area
from tests.extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestXlsxVerificationMarkAsInvalid(APITestCase):
    INVALID_MUTATION = """
        mutation invalidPaymentVerificationPlan($paymentVerificationPlanId: ID!) {
          invalidPaymentVerificationPlan(paymentVerificationPlanId: $paymentVerificationPlanId) {
            paymentPlan{
              verificationPlans{
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
        cls.content = Path(f"{settings.TESTS_ROOT}/apps/core/test_files/flex_updated.xls").read_bytes()
        cls.xlsx_file = FileTemp.objects.create(
            file=File(BytesIO(cls.content), name="flex_updated.xls"),
            object_id=cls.payment_verification_plan.pk,
            content_type=get_content_type_for_model(cls.payment_verification_plan),
            created_by=None,
        )

    @parameterized.expand(
        [
            ("with_permission_was_downloaded_false", [Permissions.PAYMENT_VERIFICATION_INVALID], False),
            ("with_permission_was_downloaded_true", [Permissions.PAYMENT_VERIFICATION_INVALID], True),
            ("without_permission", [], True),
        ]
    )
    def test_export_xlsx_payment_verification_plan(
        self, _: Any, permissions: List[Permissions], download_status: str
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.xlsx_file.was_downloaded = download_status
        self.xlsx_file.save()

        self.snapshot_graphql_request(
            request_string=self.INVALID_MUTATION,
            context={"user": self.user},
            variables={
                "paymentVerificationPlanId": self.id_to_base64(
                    self.payment_verification_plan.id, "PaymentVerificationPlanNode"
                ),
            },
        )
