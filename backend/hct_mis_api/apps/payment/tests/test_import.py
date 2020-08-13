import io
import uuid

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
from payment.models import PaymentVerification
from payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)
from payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from program.fixtures import ProgramFactory, CashPlanFactory
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


class TestTargetPopulationQuery(APITestCase):
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
        cash_plan_payment_verification = (
            CashPlanPaymentVerificationFactory()
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

    def test_validation_valid_not_changed_file(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()

        self.assertEqual(import_service.errors, [])

    def test_validation_valid_status_changed(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = PaymentVerification.STATUS_RECEIVED
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])

    def test_validation_invalid_status_changed(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = "NOT_CORRECT_STATUS"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "B2",
                    "The status of this payment verification is not correct: NOT_CORRECT_STATUS should be one of: "
                    "['PENDING', 'RECEIVED', 'NOT_RECEIVED', 'RECEIVED_WITH_ISSUES']",
                )
            ],
        )

    def test_validation_invalid_version(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        wb.properties.version = "-1"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        self.assertRaisesMessage(
            ValidationError,
            f"Unsupported file version (-1). Only version: {XlsxVerificationExportService.VERSION} is supported",
            import_service.validate,
        )

    def test_validation_payment_record_id(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        wrong_uuid = str(uuid.uuid4())
        wb.active["A2"] = wrong_uuid
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "A2",
                    f"This payment record id {wrong_uuid} is not in Cash Plan Payment Record Verification",
                )
            ],
        )

    def test_validation_wrong_type(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        wb.active["C3"] = 2
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "C3",
                    "Wrong type off cell text expected, number given.",
                )
            ],
        )

    def test_import_valid_not_changed_file(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])
        import_service.import_verifications()

    def test_import_valid_status_changed(self):
        export_service = XlsxVerificationExportService(
            TestTargetPopulationQuery.verification
        )
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_PENDING
        )
        wb.active["B2"] = PaymentVerification.STATUS_RECEIVED
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestTargetPopulationQuery.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_RECEIVED
        )
