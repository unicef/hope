from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.services.create_cash_plan_from_reconciliation import \
    CreateCashPlanFromReconciliationService, ValidationError


class TestCreateCashPlanFromReconciliation(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

    def test_parse_header_assign_indexes(self):
        column_mapping = {
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_ID: "id",
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_STATUS: "status",
            CreateCashPlanFromReconciliationService.COLUMN_DELIVERED_AMOUNT: "amount",
            CreateCashPlanFromReconciliationService.COLUMN_CURRENCY: "currency",
        }
        header_row = ("id", "status", "amount", "currency")
        column_index_mapping = {
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_ID: 0,
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_STATUS: 1,
            CreateCashPlanFromReconciliationService.COLUMN_DELIVERED_AMOUNT: 2,
            CreateCashPlanFromReconciliationService.COLUMN_CURRENCY: 3,
        }
        service = CreateCashPlanFromReconciliationService(self.business_area.slug, None, column_mapping, None)
        service._parse_header(header_row)

        self.assertEqual(service.column_index_mapping, column_index_mapping)

    def test_parse_header_raise_validation_error(self):
        column_mapping = {
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_ID: "id",
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_STATUS: "status",
            CreateCashPlanFromReconciliationService.COLUMN_DELIVERED_AMOUNT: "amount",
            CreateCashPlanFromReconciliationService.COLUMN_CURRENCY: "NOT_A_COLUMN",
        }
        header_row = ("id", "status", "amount", "currency")
        service = CreateCashPlanFromReconciliationService(self.business_area.slug, None, column_mapping, None)
        with self.assertRaises(ValidationError):
            service._parse_header(header_row)


    def test_parse_header_raise_validation_error2(self):
        column_mapping = {
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_ID: "id",
            CreateCashPlanFromReconciliationService.COLUMN_PAYMENT_STATUS: "status",
            CreateCashPlanFromReconciliationService.COLUMN_DELIVERED_AMOUNT: "amount",
            'NOT_A_COLUMN': "currency",
        }
        header_row = ("id", "status", "amount", "currency")
        service = CreateCashPlanFromReconciliationService(self.business_area.slug, None, column_mapping, None)
        with self.assertRaises(ValidationError):
            service._parse_header(header_row)