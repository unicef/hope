import io
import uuid

from graphql import GraphQLError
from openpyxl.writer.excel import save_virtual_workbook
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentVerificationPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)
from hct_mis_api.apps.payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.payment.fixtures import CashPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestXlsxVerificationImport(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        payment_record_amount = 10
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.user = UserFactory()

        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=cls.user, targeting_criteria=targeting_criteria, business_area=cls.business_area
        )
        cash_plan = CashPlanFactory(program=program, business_area=cls.business_area)
        cash_plan.save()
        payment_verification_plan = PaymentVerificationPlanFactory(cash_plan=cash_plan)
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=cls.user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                parent=cash_plan,
                household=household,
                head_of_household=household.head_of_household,
                target_population=target_population,
            )

            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verification_plans.first()

    @parameterized.expand(
        [
            ("from_pending", PaymentVerification.STATUS_PENDING, None),
            ("from_not_received", PaymentVerification.STATUS_NOT_RECEIVED, "NO"),
            ("from_received", PaymentVerification.STATUS_RECEIVED, "YES"),
            ("from_received_with_issues", PaymentVerification.STATUS_RECEIVED_WITH_ISSUES, "YES"),
        ]
    )
    def test_export_received_from_pending(self, _, initial_status, result):
        self.create_user_role_with_permissions(self.user, [Permissions.PAYMENT_VERIFICATION_IMPORT], self.business_area)

        TestXlsxVerificationImport.verification.payment_record_verifications.all().update(status=initial_status)
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)

        wb = export_service.generate_workbook()
        self.assertEqual(wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"].value, result)

    def test_validation_valid_not_changed_file(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()

        self.assertEqual(import_service.errors, [])

    def test_validation_valid_status_changed(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])

    def test_validation_invalid_received_changed(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NOT_CORRECT_RECEIVED"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                    "The received of this payment verification is not correct: NOT_CORRECT_RECEIVED should be one of: "
                    "[None, 'YES', 'NO']",
                )
            ],
        )

    def test_validation_invalid_version(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb[XlsxVerificationExportService.META_SHEET][XlsxVerificationExportService.VERSION_CELL_COORDINATES] = "-1"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        self.assertRaisesMessage(
            GraphQLError,
            f"Unsupported file version (-1). Only version: {XlsxVerificationExportService.VERSION} is supported",
            import_service.validate,
        )

    def test_validation_payment_record_id(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wrong_uuid = str(uuid.uuid4())
        wb.active["A2"] = wrong_uuid
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
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
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3"] = "A"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3",
                    "Wrong type off cell number expected, text given.",
                )
            ],
        )

    def test_validation_invalid_received_not_received_with_amount(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 10
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                    "If received_amount(10.00) is not 0, you should set received to YES",
                )
            ],
        )

    def test_validation_invalid_received_received_with_0_amount(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(
            import_service.errors,
            [
                (
                    "Payment Verifications",
                    f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                    "If received_amount is 0, you should set received to NO",
                )
            ],
        )

    def test_import_valid_status_changed_received_no(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_NOT_RECEIVED)

    def test_import_valid_status_changed_received_yes_not_full(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = (
            payment_verification.payment_record.delivered_quantity - 1
        )
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment_record.delivered_quantity - 1,
        )

    def test_import_valid_status_changed_received_yes_full(self):
        export_service = XlsxVerificationExportService(TestXlsxVerificationImport.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[
            f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"
        ] = payment_verification.payment_record.delivered_quantity
        file = io.BytesIO(save_virtual_workbook(wb))
        import_service = XlsxVerificationImportService(TestXlsxVerificationImport.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_record__id=payment_record_id)
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment_record.delivered_quantity,
        )
