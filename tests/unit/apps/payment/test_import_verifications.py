import io
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, List
from unittest.mock import patch

from django.conf import settings

from graphql import GraphQLError
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import (
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.payment.xlsx.xlsx_verification_export_service import (
    XlsxVerificationExportService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_verification_import_service import (
    XlsxVerificationImportService,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestXlsxVerificationImport(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        create_afghanistan()
        payments_amount = 10
        self.business_area = BusinessArea.objects.get(slug="afghanistan")

        self.user = UserFactory()

        program = ProgramFactory(business_area=self.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(program_cycle=program.cycles.first(), business_area=self.business_area)
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
        for _ in range(payments_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=self.user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                    "program": program,
                },
                {"registration_data_import": registration_data_import},
            )

            payment = PaymentFactory(
                parent=payment_plan,
                household=household,
                head_of_household=household.head_of_household,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment=payment,
                payment_verification_plan=payment_verification_plan,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        self.payment_plan = payment_plan
        self.verification = payment_plan.payment_verification_plans.first()

    @parameterized.expand(
        [
            ("from_pending", PaymentVerification.STATUS_PENDING, None),
            ("from_not_received", PaymentVerification.STATUS_NOT_RECEIVED, "NO"),
            ("from_received", PaymentVerification.STATUS_RECEIVED, "YES"),
            ("from_received_with_issues", PaymentVerification.STATUS_RECEIVED_WITH_ISSUES, "YES"),
        ]
    )
    def test_export_received_from_pending(self, _: Any, initial_status: str, result: Any) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PAYMENT_VERIFICATION_IMPORT], self.business_area, whole_business_area_access=True
        )

        self.verification.payment_record_verifications.all().update(status=initial_status)
        export_service = XlsxVerificationExportService(self.verification)

        wb = export_service.generate_workbook()
        self.assertEqual(wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"].value, result)

    def test_validation_valid_not_changed_file(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()

        self.assertEqual(import_service.errors, [])

    def test_validation_valid_status_changed_for_people(self) -> None:
        dct = self.verification.payment_plan.program_cycle.program.data_collecting_type
        dct.type = DataCollectingType.Type.SOCIAL
        dct.save()
        export_service = XlsxVerificationExportService(self.verification)
        self.verification.refresh_from_db()
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER_PEOPLE}2"] = 2
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])

    def test_validation_valid_status_changed(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        self.assertEqual(import_service.errors, [])

    def test_validation_invalid_received_changed(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NOT_CORRECT_RECEIVED"
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()

        error = import_service.errors[0]
        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Payment Verifications",
                f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                "The received of this payment verification is not correct: NOT_CORRECT_RECEIVED should be one of: "
                "(None, 'YES', 'NO')",
            ],
        )

    def test_validation_invalid_version(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb[XlsxVerificationExportService.META_SHEET][XlsxVerificationExportService.VERSION_CELL_COORDINATES] = "-1"
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        self.assertRaisesMessage(
            GraphQLError,
            f"Unsupported file version (-1). Only version: {XlsxVerificationExportService.VERSION} is supported",
            import_service.validate,
        )

    def test_validation_payment_record_id(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wrong_uuid = str(uuid.uuid4())
        wb.active["A2"] = wrong_uuid
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        error = import_service.errors[0]
        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Payment Verifications",
                "A2",
                f"This payment record id {wrong_uuid} is not in Cash Plan Payment Record Verification",
            ],
        )

    def test_validation_wrong_type(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3"] = "A"
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        error = import_service.errors[0]

        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Payment Verifications",
                f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}3",
                "Wrong type off cell number expected, text given.",
            ],
        )

    def test_validation_invalid_received_not_received_with_amount(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 10
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        error = import_service.errors[0]
        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Payment Verifications",
                f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                "If received_amount(10.00) is not 0, you should set received to YES",
            ],
        )

    def test_validation_invalid_received_received_with_0_amount(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = 0
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        error = import_service.errors[0]
        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Payment Verifications",
                f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2",
                "Amount Received' equals to 0, please set status as 'Not Received'",
            ],
        )

    def test_import_valid_status_changed_received_no(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "NO"
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_NOT_RECEIVED)

    def test_import_valid_status_changed_received_yes_not_full(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = (
            payment_verification.payment.delivered_quantity - 1
        )
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment.delivered_quantity - 1,
        )

    def test_import_valid_status_changed_received_yes_full(self) -> None:
        export_service = XlsxVerificationExportService(self.verification)
        wb = export_service.generate_workbook()
        payment_record_id = wb.active["A2"].value
        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        wb.active[f"{XlsxVerificationExportService.RECEIVED_COLUMN_LETTER}2"] = "YES"
        wb.active[f"{XlsxVerificationExportService.RECEIVED_AMOUNT_COLUMN_LETTER}2"] = (
            payment_verification.payment.delivered_quantity
        )
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            file = io.BytesIO(tmp.read())
        import_service = XlsxVerificationImportService(self.verification, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_verifications()
        self.assertEqual(import_service.errors, [])

        payment_verification = PaymentVerification.objects.get(payment_id=payment_record_id)
        self.assertEqual(
            payment_verification.status,
            PaymentVerification.STATUS_RECEIVED,
        )
        self.assertEqual(
            payment_verification.received_amount,
            payment_verification.payment.delivered_quantity,
        )

    @parameterized.expand(
        [
            ("unordered_columns_1", []),
            ("unordered_columns_2", []),
            ("unordered_columns_3", []),
        ]
    )
    @patch(
        "hct_mis_api.apps.payment.xlsx.xlsx_verification_import_service.XlsxVerificationImportService._check_version",
        return_value=None,
    )
    def test_validation_of_unordered_columns(self, file_name: str, error_list: List, mock_check_version: Any) -> None:
        """
        1st scenario - unordered columns with missing standard columns
        2nd scenario - missing standard columns and additional user columns
        3rd scenario - like above + one null header
        """

        payment_plan = PaymentPlanFactory()

        hoh1 = IndividualFactory(household=None)
        household_1 = HouseholdFactory(head_of_household=hoh1)
        payment_1 = PaymentFactory(
            id="0329a41f-affd-4669-9e38-38ec2d6699b3",
            parent=payment_plan,
            household=household_1,
            entitlement_quantity=120,
            delivered_quantity=150,
            currency="PLN",
        )

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        payment_2 = PaymentFactory(
            id="299811ef-b123-427d-b77d-9fd5d1bc8946",
            parent=payment_plan,
            household=household_2,
            entitlement_quantity=120,
            delivered_quantity=150,
            currency="PLN",
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)

        PaymentVerificationFactory(
            payment=payment_1,
            payment_verification_plan=payment_verification_plan,
            status=PaymentVerification.STATUS_PENDING,
        )
        PaymentVerificationFactory(
            payment=payment_2,
            payment_verification_plan=payment_verification_plan,
            status=PaymentVerification.STATUS_PENDING,
        )

        content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/{file_name}.xlsx").read_bytes()
        xlsx_verification_import_service = XlsxVerificationImportService(payment_verification_plan, io.BytesIO(content))
        xlsx_verification_import_service.open_workbook()
        xlsx_verification_import_service.validate()

        self.assertEqual(xlsx_verification_import_service.errors, error_list)
