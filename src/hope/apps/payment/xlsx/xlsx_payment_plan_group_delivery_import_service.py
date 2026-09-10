from __future__ import annotations

from decimal import Decimal
from io import BytesIO
import logging
from typing import IO, TYPE_CHECKING, Any, cast

from django.db import transaction
import openpyxl

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import log_payment_plan_change
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import (
    NULL_DELIVERY_POLICIES,
    NULL_DELIVERY_POLICY_RESET,
    XlsxPaymentPlanDeliveryImportService,
)
from hope.models import Payment, PaymentPlan

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

    from hope.models import PaymentPlanGroup

logger = logging.getLogger(__name__)


class XlsxPaymentPlanGroupDeliveryImportError(Exception):
    def __init__(self, errors: list[XlsxError]) -> None:
        self.errors = errors
        super().__init__("Payment Plan Group reconciliation XLSX validation failed")


class XlsxPaymentPlanGroupDeliveryImportService:
    """Validate and atomically import manual reconciliation rows for a Payment Plan Group."""

    REQUIRED_COLUMNS = ("payment_id", "delivered_quantity")
    PLAN_STATUSES = (PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED, PaymentPlan.Status.CLOSED)

    def __init__(
        self,
        payment_plan_group: "PaymentPlanGroup",
        file: IO[bytes],
        override: bool = False,
        null_delivery_policy: str = NULL_DELIVERY_POLICY_RESET,
    ) -> None:
        if null_delivery_policy not in NULL_DELIVERY_POLICIES:
            raise ValueError(f"Unsupported null delivery policy: {null_delivery_policy}")
        self.payment_plan_group = payment_plan_group
        self.file = file
        self.override = override
        self.null_delivery_policy = null_delivery_policy
        self.errors: list[XlsxError] = []
        self.conflict_errors: list[XlsxError] = []
        self.skipped_rows: list[dict[str, Any]] = []
        self.payment_plans: list[PaymentPlan] = []
        self.eligible_plans: list[PaymentPlan] = []
        self.payment_to_plan: dict[str, PaymentPlan] = {}
        self.ineligible_payment_reasons: dict[str, str] = {}
        self.closed_payments: dict[str, tuple[str, Decimal | None, str]] = {}
        self.payment_gateway_payment_ids: set[str] = set()
        self.fsp_owned_headers: set[str] = set()
        self.source_row_numbers: dict[str, int] = {}
        self.headers: list[str] = []
        self.sheetname = ""
        self.ws: Worksheet | None = None
        self.wb: openpyxl.Workbook | None = None
        self.per_plan_services: dict[str, XlsxPaymentPlanDeliveryImportService] = {}

    def _load_payment_plans(self, lock: bool = False) -> None:
        queryset = self.payment_plan_group.payment_plans.filter(status__in=self.PLAN_STATUSES).order_by("unicef_id")
        if lock:
            queryset = queryset.select_for_update()
        self.payment_plans = list(queryset)

    def _prepare_eligible_plans(self) -> None:
        self.eligible_plans = []
        for payment_plan in self.payment_plans:
            if payment_plan.is_payment_gateway:
                logger.warning(
                    f"Skipping Payment Plan {payment_plan.unicef_id}: uses payment gateway, "
                    f"manual reconciliation is not allowed."
                )
                continue
            if payment_plan.status == PaymentPlan.Status.CLOSED:
                continue
            if payment_plan.status == PaymentPlan.Status.FINISHED and not self.override:
                continue
            self.eligible_plans.append(payment_plan)

    def _build_payment_index(self, lock: bool = False) -> None:
        self.payment_to_plan = {}
        self.ineligible_payment_reasons = {}
        self.closed_payments = {}
        self.payment_gateway_payment_ids = set()
        self.fsp_owned_headers = set()

        payment_plan_by_id = {payment_plan.id: payment_plan for payment_plan in self.payment_plans}
        queryset = Payment.objects.filter(parent__in=self.payment_plans)
        if lock:
            queryset = queryset.select_for_update()
        payments = queryset.values_list(
            "unicef_id",
            "parent_id",
            "extras",
            "conflicted",
            "excluded",
            "has_valid_wallet",
            "delivered_quantity",
            "status",
        )
        eligible_plan_ids = {payment_plan.id for payment_plan in self.eligible_plans}
        for (
            unicef_id,
            parent_id,
            extras,
            conflicted,
            excluded,
            has_valid_wallet,
            delivered_quantity,
            payment_status,
        ) in payments:
            payment_id = str(unicef_id)
            payment_plan = payment_plan_by_id[parent_id]
            self.fsp_owned_headers.update(extras.get(Payment.FSP_EXTRA_FIELDS_KEY, {}))
            if payment_plan.status == PaymentPlan.Status.CLOSED:
                self.closed_payments[payment_id] = (
                    str(payment_plan.unicef_id),
                    delivered_quantity,
                    payment_status,
                )
            elif payment_plan.is_payment_gateway:
                self.payment_gateway_payment_ids.add(payment_id)
            elif payment_plan.id not in eligible_plan_ids:
                self.ineligible_payment_reasons[payment_id] = (
                    f"Payment Plan status {payment_plan.status} is not eligible for this import mode."
                )
            elif conflicted or excluded or has_valid_wallet is False:
                continue
            else:
                self.payment_to_plan[payment_id] = payment_plan

    def _prepare_payment_data(self, lock: bool = False) -> None:
        self._load_payment_plans(lock=lock)
        self._prepare_eligible_plans()
        self._build_payment_index(lock=lock)

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(cast("Any", self.file), data_only=True)
        self.wb = wb
        self.ws = wb[wb.sheetnames[0]]
        self.sheetname = wb.sheetnames[0]
        self.headers = [cell.value for cell in self.ws[1]]
        self._prepare_payment_data()
        return wb

    def _validate_required_headers(self) -> bool:
        missing = [column for column in self.REQUIRED_COLUMNS if column not in self.headers]
        if missing:
            self.errors.append(
                XlsxError(
                    self.sheetname,
                    None,
                    f"Provided headers {self.headers} do not match expected headers. "
                    f"{list(self.REQUIRED_COLUMNS)} are required headers.",
                )
            )
            return False
        return True

    def _validate_row_payment_ids(self) -> None:
        if self.ws is None:
            return
        seen_ids: set[str] = set()
        payment_id_idx = self.headers.index("payment_id")
        delivered_quantity_idx = self.headers.index("delivered_quantity")
        for row in self.ws.iter_rows(min_row=2):
            if not any(cell.value for cell in row):
                continue
            id_cell = row[payment_id_idx]
            if id_cell.value is None:
                continue
            payment_id = str(id_cell.value)
            if payment_id in seen_ids:
                self.errors.append(
                    XlsxError(
                        self.sheetname,
                        id_cell.coordinate,
                        f"Payment id {payment_id} appears multiple times in the import file",
                    )
                )
            else:
                seen_ids.add(payment_id)

            if payment_id in self.closed_payments:
                self._validate_closed_payment_row(payment_id, id_cell, row[delivered_quantity_idx])
            elif payment_id in self.payment_gateway_payment_ids:
                self.errors.append(
                    XlsxError(
                        self.sheetname,
                        id_cell.coordinate,
                        f"Payment id {payment_id} belongs to a payment plan that uses payment gateway "
                        f"and cannot be manually reconciled.",
                    )
                )
            elif reason := self.ineligible_payment_reasons.get(payment_id):
                self.skipped_rows.append({"row": id_cell.row, "payment_id": payment_id, "reason": reason})
            elif payment_id not in self.payment_to_plan:
                self.errors.append(
                    XlsxError(
                        self.sheetname,
                        id_cell.coordinate,
                        f"Payment id {payment_id} does not belong to any payment plan in this group.",
                    )
                )

    def _validate_closed_payment_row(self, payment_id: str, id_cell: Any, quantity_cell: Any) -> None:
        payment_plan_id, stored_quantity, stored_status = self.closed_payments[payment_id]
        try:
            file_quantity = XlsxPaymentPlanDeliveryImportService._parse_delivered_quantity(quantity_cell.value)
        except ValueError:
            self.errors.append(
                XlsxError(
                    self.sheetname,
                    quantity_cell.coordinate,
                    f"Payment {payment_id}: Delivered quantity {quantity_cell.value} must be a number greater than "
                    "or equal to zero, exactly -1, or empty.",
                )
            )
            return

        matches_stored_result = file_quantity == stored_quantity or (
            file_quantity == Decimal(-1) and stored_quantity is None and stored_status == Payment.STATUS_ERROR
        )
        if file_quantity is None or matches_stored_result:
            self.skipped_rows.append(
                {
                    "row": id_cell.row,
                    "payment_id": payment_id,
                    "reason": f"Payment belongs to CLOSED Payment Plan {payment_plan_id}; existing data was preserved.",
                }
            )
            return

        self.errors.append(
            XlsxError(
                self.sheetname,
                id_cell.coordinate,
                f"Payment id {payment_id} belongs to CLOSED Payment Plan {payment_plan_id} and the XLSX delivered "
                "quantity does not match its stored result. The entire file cannot be imported.",
            )
        )

    def _row_groups_by_plan(self) -> dict[str, list[tuple[Any, ...]]]:
        if self.ws is None:
            return {}
        rows_by_plan: dict[str, list[tuple[Any, ...]]] = {}
        self.source_row_numbers = {}
        seen_ids: set[str] = set()
        payment_id_idx = self.headers.index("payment_id")
        for row in self.ws.iter_rows(min_row=2):
            if not any(cell.value for cell in row):
                continue
            payment_id_value = row[payment_id_idx].value
            if payment_id_value is None:
                continue
            payment_id = str(payment_id_value)
            payment_plan = self.payment_to_plan.get(payment_id)
            if payment_plan is None or payment_id in seen_ids:
                continue
            seen_ids.add(payment_id)
            self.source_row_numbers[payment_id] = row[payment_id_idx].row
            rows_by_plan.setdefault(str(payment_plan.id), []).append(tuple(cell.value for cell in row))
        return rows_by_plan

    def _build_per_plan_workbook(self, rows: list[tuple[Any, ...]]) -> BytesIO:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.sheetname or "Sheet"
        ws.append(self.headers)
        current_row = 1
        payment_id_idx = self.headers.index("payment_id")
        for row_values in rows:
            payment_id = str(row_values[payment_id_idx])
            source_row = self.source_row_numbers[payment_id]
            while current_row < source_row - 1:
                ws.append([None])
                current_row += 1
            ws.append(list(row_values))
            current_row += 1
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    def _build_per_plan_services(self) -> None:
        self.per_plan_services = {}
        rows_by_plan = self._row_groups_by_plan()
        for payment_plan in self.eligible_plans:
            rows = rows_by_plan.get(str(payment_plan.id), [])
            if not rows:
                continue
            service = XlsxPaymentPlanDeliveryImportService(
                payment_plan,
                self._build_per_plan_workbook(rows),
                fsp_owned_headers=self.fsp_owned_headers,
                override=self.override,
                null_delivery_policy=self.null_delivery_policy,
            )
            service.open_workbook()
            self.per_plan_services[str(payment_plan.id)] = service

    def validate(self) -> None:
        self.errors = []
        self.conflict_errors = []
        self.skipped_rows = []
        if not self._validate_required_headers():
            return
        self._validate_row_payment_ids()
        self._build_per_plan_services()
        for service in self.per_plan_services.values():
            service._validate_headers()
            if not service.errors:
                service._validate_rows()
            self.errors.extend(service.errors)
            self.conflict_errors.extend(service.conflict_errors)
            self.skipped_rows.extend(
                {
                    **skipped_row,
                    "row": self.source_row_numbers.get(skipped_row["payment_id"]),
                }
                for skipped_row in service.skipped_rows
            )

    def import_payment_list(self, user_id: str | None = None) -> None:
        if self.ws is None:
            raise RuntimeError("open_workbook() must be called before import_payment_list()")

        with transaction.atomic():
            self._prepare_payment_data(lock=True)
            self.validate()
            if self.errors:
                raise XlsxPaymentPlanGroupDeliveryImportError(self.errors)

            affected_plan_ids: list[str] = []
            for payment_plan_id, service in self.per_plan_services.items():
                payment_plan = service.payment_plan
                old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
                service.import_payment_list(user_id)
                if not service.payments_to_save:
                    continue

                affected_plan_ids.append(payment_plan_id)
                payment_plan.remove_export_files()
                flow = PaymentPlanFlow(payment_plan)
                flow.background_action_status_none()
                payment_plan.update_money_fields()
                if payment_plan.is_reconciled and payment_plan.status == PaymentPlan.Status.ACCEPTED:
                    flow.status_finished()
                elif not payment_plan.is_reconciled and payment_plan.status == PaymentPlan.Status.FINISHED:
                    flow.status_reopen_for_reconciliation()
                payment_plan.save()
                log_payment_plan_change(payment_plan, old_payment_plan, user_id)
                PaymentPlanService(payment_plan).recalculate_signatures_in_batch()

            if affected_plan_ids:
                logger.info(f"Imported reconciliation for Payment Plans: {affected_plan_ids}")
                self.payment_plan_group.cycle.save()
