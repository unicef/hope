from io import BytesIO

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.payment.services.create_cash_plan_from_reconciliation import (
    CreateCashPlanReconciliationService,
    ValidationError,
)


class TestCreateCashPlanFromReconciliation(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

    def test_parse_header_assign_indexes(self) -> None:
        column_mapping = {
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_ID: "Payment ID",
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_STATUS: "Reconciliation status",
            CreateCashPlanReconciliationService.COLUMN_DELIVERED_AMOUNT: "Delivered Amount",
            CreateCashPlanReconciliationService.COLUMN_ENTITLEMENT_QUANTITY: "Entitlement Quantity",
        }
        header_row = ["Payment ID", "Reconciliation status", "Delivered Amount", "Entitlement Quantity"]
        column_index_mapping = {
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_ID: 0,
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_STATUS: 1,
            CreateCashPlanReconciliationService.COLUMN_DELIVERED_AMOUNT: 2,
            CreateCashPlanReconciliationService.COLUMN_ENTITLEMENT_QUANTITY: 3,
        }
        service = CreateCashPlanReconciliationService(
            self.business_area, BytesIO(), column_mapping, {}, "HRVN", PaymentRecord.DELIVERY_TYPE_CASH, ""
        )
        service._parse_header(header_row)

        self.assertEqual(service.column_index_mapping, column_index_mapping)

    def test_parse_header_raise_validation_error(self) -> None:
        column_mapping = {
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_ID: "id",
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_STATUS: "status",
            CreateCashPlanReconciliationService.COLUMN_DELIVERED_AMOUNT: "amount",
            CreateCashPlanReconciliationService.COLUMN_ENTITLEMENT_QUANTITY: "NOT_A_COLUMN",
        }
        header_row = ["id", "status", "amount", "Entitlement Quantity"]
        service = CreateCashPlanReconciliationService(
            self.business_area, BytesIO(), column_mapping, {}, "HRVN", PaymentRecord.DELIVERY_TYPE_CASH, ""
        )
        with self.assertRaises(ValidationError):
            service._parse_header(header_row)

    def test_parse_header_raise_validation_error2(self) -> None:
        column_mapping = {
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_ID: "id",
            CreateCashPlanReconciliationService.COLUMN_PAYMENT_STATUS: "status",
            CreateCashPlanReconciliationService.COLUMN_DELIVERED_AMOUNT: "amount",
            "NOT_A_COLUMN": "Entitlement Quantity",
        }
        header_row = ["id", "status", "amount", "Entitlement Quantity"]
        service = CreateCashPlanReconciliationService(
            self.business_area, BytesIO(), column_mapping, {}, "HRVN", PaymentRecord.DELIVERY_TYPE_CASH, ""
        )
        with self.assertRaises(ValidationError):
            service._parse_header(header_row)
