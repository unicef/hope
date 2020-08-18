import io
import uuid
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.core.management import call_command
from openpyxl.writer.excel import save_virtual_workbook

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea, AdminArea
from household.fixtures import (
    create_household,
    EntitlementCardFactory,
)
from payment.fixtures import (
    PaymentRecordFactory,
    CashPlanPaymentVerificationFactory,
    PaymentVerificationFactory,
)
from payment.models import PaymentVerification, CashPlanPaymentVerification
from payment.tasks.CheckRapidProVerificationTask import (
    CheckRapidProVerificationTask,
)
from payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)
from payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from program.fixtures import ProgramFactory, CashPlanFactory
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


class TestRapidProVerificationTask(APITestCase):
    verification = None

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        payment_record_amount = 10

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            candidate_list_targeting_criteria=targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan = CashPlanFactory.build(
            program=program, business_area=BusinessArea.objects.first(),
        )
        cash_plan.save()
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            status=CashPlanPaymentVerification.STATUS_ACTIVE,
            verification_method=CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO,
        )
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": AdminArea.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import,},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                cash_plan=cash_plan,
                household=household,
                target_population=target_population,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verifications.first()

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_not_received(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verifications = TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
            "payment_record__household__head_of_household"
        ).order_by(
            "?"
        )[
            :3
        ]
        self.assertEqual(
            payment_record_verifications[0].status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": payment_record_verifications[
                    0
                ].payment_record.household.head_of_household.phone_no,
                "received": False,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "payment.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verifications[0].refresh_from_db()
            self.assertEqual(
                payment_record_verifications[0].status,
                PaymentVerification.STATUS_NOT_RECEIVED,
            )
