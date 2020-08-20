import io
import uuid

from django.core.management import call_command
from graphql import GraphQLError
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


class TestXlsxVerificationImport(APITestCase):
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
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory()
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

    def test_export_received_from_pending(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        self.assertEqual(wb.active["B2"].value, None)

    def test_export_received_from_not_received(self):
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_NOT_RECEIVED
        )
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_PENDING
        )
        self.assertEqual(wb.active["B2"].value, "NO")

    def test_export_received_from_received(self):
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_RECEIVED
        )
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_PENDING
        )
        self.assertEqual(wb.active["B2"].value, "YES")

    def test_export_received_from_received_with_issues(self):
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        )
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(
            status=PaymentVerification.STATUS_PENDING
        )
        self.assertEqual(wb.active["B2"].value, "YES")

    def test_validation_valid_not_changed_file(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        export_service.generate_file("test.xlsx")
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()

        self.assertEqual(import_service.errors, [])

    #
    def test_validation_valid_status_changed(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = "NO"
        wb.active["F2"] = 0
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])

    def test_validation_invalid_received_changed(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = "NOT_CORRECT_RECEIVED"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "B2",
                    "The received of this payment verification is not correct: NOT_CORRECT_RECEIVED should be one of: "
                    "[None, 'YES', 'NO']",
                )
            ],
        )

    def test_validation_invalid_version(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb[XlsxVerificationExportService.META_SHEET][
            XlsxVerificationExportService.VERSION_CELL_COORDINATES
        ] = "-1"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        self.assertRaisesMessage(
            GraphQLError,
            f"Unsupported file version (-1). Only version: {XlsxVerificationExportService.VERSION} is supported",
            import_service.validate,
        )

    def test_validation_payment_record_id(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wrong_uuid = str(uuid.uuid4())
        wb.active["A2"] = wrong_uuid
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
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
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb.active["C3"] = 2
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
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

    def test_validation_invalid_received_not_received_with_amount(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = "NO"
        wb.active["F2"] = 10
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "B2",
                    "If received_amount(10.00) is not 0, you should set received to YES",
                )
            ],
        )

    def test_validation_invalid_received_received_with_0_amount(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        wb.active["B2"] = "YES"
        wb.active["F2"] = 0
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    "B2",
                    "If received_amount is 0, you should set received to NO",
                )
            ],
        )

    def test_import_valid_status_changed_received_no(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_PENDING
        )
        wb.active["B2"] = "NO"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_NOT_RECEIVED
        )

    def test_import_valid_status_changed_received_yes_not_full(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_PENDING
        )
        wb.active["B2"] = "YES"
        wb.active["F2"] = (
            payment_verification.payment_record.delivered_quantity - 1
        )
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment_record.delivered_quantity - 1,
        )

    def test_import_valid_status_changed_received_yes_full(self):
        export_service = XlsxVerificationExportService(
            TestXlsxVerificationImport.verification
        )
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status, PaymentVerification.STATUS_PENDING
        )
        wb.active["B2"] = "YES"
        wb.active["F2"] = (
            payment_verification.payment_record.delivered_quantity
        )
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(
            TestXlsxVerificationImport.verification, file
        )
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(
            payment_record__id=payment_record_id
        )
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment_record.delivered_quantity,
        )