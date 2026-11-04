from __future__ import annotations

from io import BytesIO
import logging
from typing import IO, TYPE_CHECKING, Any, cast

from django.db import transaction
import openpyxl

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.flows import PaymentListFlow
from hope.apps.payment.services.payment_list_services import PaymentListService
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import log_payment_list_change
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_list_delivery_import_service import (
    NULL_DELIVERY_POLICIES,
    NULL_DELIVERY_POLICY_RESET,
    XlsxPaymentListDeliveryImportService,
)
from hope.models import Payment, PaymentList, PaymentPlan

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet

    from hope.models import PaymentPlan

logger = logging.getLogger(__name__)


class XlsxPaymentPlanDeliveryImportError(Exception):
    def __init__(self, errors: list[XlsxError]) -> None:
        self.errors = errors
        super().__init__("Payment Plan reconciliation XLSX validation failed")


class XlsxPaymentPlanDeliveryImportService:
    """Import and validate a single-sheet reconciliation XLSX for a single-FSP Payment Plan.

    The file can contain rows from multiple Payment Lists in the payment plan. Rows are matched to their
    owning plan by Payment.unicef_id and processed atomically through per-plan import services.
    """

    REQUIRED_COLUMNS = ("payment_id", "delivered_quantity")
    PLAN_STATUSES = (PaymentList.Status.ACCEPTED, PaymentList.Status.FINISHED)

    def __init__(
        self,
        payment_plan: "PaymentPlan",
        file: IO[bytes],
        override: bool = False,
        null_delivery_policy: str = NULL_DELIVERY_POLICY_RESET,
    ) -> None:
        if null_delivery_policy not in NULL_DELIVERY_POLICIES:
            raise ValueError(f"Unsupported null delivery policy: {null_delivery_policy}")
        self.payment_plan = payment_plan
        self.file = file
        self.override = override
        self.null_delivery_policy = null_delivery_policy
        self.errors: list[XlsxError] = []
        self.conflict_errors: list[XlsxError] = []
        self.skipped_rows: list[dict[str, Any]] = []
        self.payment_lists: list[PaymentList] = []
        self.eligible_plans: list[PaymentList] = []
        self.payment_to_plan: dict[str, PaymentList] = {}
        self.ineligible_payment_reasons: dict[str, str] = {}
        self.payment_gateway_payment_ids: set[str] = set()
        self.fsp_owned_headers: set[str] = set()
        self.source_row_numbers: dict[str, int] = {}
        self.headers: list[str] = []
        self.sheetname = ""
        self.ws: Worksheet | None = None
        self.wb: openpyxl.Workbook | None = None
        self.per_plan_services: dict[str, XlsxPaymentListDeliveryImportService] = {}

    def _load_payment_lists(self, lock: bool = False) -> None:
        queryset = self.payment_plan.payment_lists.filter(status__in=self.PLAN_STATUSES).order_by("unicef_id")
        if lock:
            queryset = queryset.select_for_update()
        self.payment_lists = list(queryset)

    def _prepare_eligible_plans(self) -> None:
        self.eligible_plans = []
        for payment_list in self.payment_lists:
            if payment_list.is_payment_gateway:
                logger.warning(
                    f"Skipping Payment List {payment_list.unicef_id}: uses payment gateway, "
                    f"manual reconciliation is not allowed."
                )
                continue
            if payment_list.status == PaymentList.Status.FINISHED and not self.override:
                continue
            self.eligible_plans.append(payment_list)

    def _build_payment_index(self, lock: bool = False) -> None:
        self.payment_to_plan = {}
        self.ineligible_payment_reasons = {}
        self.payment_gateway_payment_ids = set()
        self.fsp_owned_headers = set()

        payment_list_by_id = {payment_list.id: payment_list for payment_list in self.payment_lists}
        queryset = Payment.objects.filter(parent__in=self.payment_lists).eligible()
        if lock:
            queryset = queryset.select_for_update()
        payments = queryset.values_list("unicef_id", "parent_id", "extras")
        eligible_plan_ids = {payment_list.id for payment_list in self.eligible_plans}
        for unicef_id, parent_id, extras in payments:
            payment_id = str(unicef_id)
            payment_list = payment_list_by_id[parent_id]
            self.fsp_owned_headers.update(extras.get(Payment.FSP_EXTRA_FIELDS_KEY, {}))
            if payment_list.is_payment_gateway:
                self.payment_gateway_payment_ids.add(payment_id)
            elif payment_list.id not in eligible_plan_ids:
                self.ineligible_payment_reasons[payment_id] = (
                    f"Payment List status {payment_list.status} is not eligible for this import mode."
                )
            else:
                self.payment_to_plan[payment_id] = payment_list

    def _prepare_payment_data(self, lock: bool = False) -> None:
        self._load_payment_lists(lock=lock)
        self._prepare_eligible_plans()
        self._build_payment_index(lock=lock)

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file, data_only=True)
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

            if payment_id in self.payment_gateway_payment_ids:
                self.errors.append(
                    XlsxError(
                        self.sheetname,
                        id_cell.coordinate,
                        f"Payment id {payment_id} belongs to a payment list that uses payment gateway "
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
                        f"Payment id {payment_id} does not belong to any payment list in this payment plan.",
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
            payment_list = self.payment_to_plan.get(payment_id)
            if payment_list is None or payment_id in seen_ids:
                continue
            seen_ids.add(payment_id)
            self.source_row_numbers[payment_id] = row[payment_id_idx].row
            rows_by_plan.setdefault(str(payment_list.id), []).append(tuple(cell.value for cell in row))
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
        for payment_list in self.eligible_plans:
            rows = rows_by_plan.get(str(payment_list.id), [])
            if not rows:
                continue
            service = XlsxPaymentListDeliveryImportService(
                payment_list,
                self._build_per_plan_workbook(rows),
                fsp_owned_headers=self.fsp_owned_headers,
                override=self.override,
                null_delivery_policy=self.null_delivery_policy,
            )
            service.open_workbook()
            self.per_plan_services[str(payment_list.id)] = service

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
            # Every payment plan action locks the plan before its lists; keep that order to avoid deadlocks.
            PaymentPlan.objects.select_for_update().get(pk=self.payment_plan.pk)
            self._prepare_payment_data(lock=True)
            self.validate()
            if self.errors:
                raise XlsxPaymentPlanDeliveryImportError(self.errors)

            affected_plan_ids: list[str] = []
            for payment_list_id, service in self.per_plan_services.items():
                payment_list = service.payment_list
                old_payment_list = cast("PaymentList", copy_model_object(payment_list))
                service.import_payment_list(user_id)
                if not service.payments_to_save:
                    continue

                affected_plan_ids.append(payment_list_id)
                payment_list.remove_export_files()
                flow = PaymentListFlow(payment_list)
                flow.background_action_status_none()
                payment_list.update_money_fields()
                payment_list.save()
                log_payment_list_change(payment_list, old_payment_list, user_id)
                PaymentListService(payment_list).recalculate_signatures_in_batch()
            PaymentPlanService(self.payment_plan).sync_finished(user_id)

            if affected_plan_ids:
                logger.info(f"Imported reconciliation for Payment Lists: {affected_plan_ids}")
                self.payment_plan.remove_export_file_delivery()
                self.payment_plan.save(update_fields=["export_file_delivery", "updated_at"])
                # All payment lists in the payment plan share one cycle: invalidate the cycle-list cache once.
                self.payment_plan.cycle.save()

    def get_result_counts(self) -> dict[str, int]:
        if self.ws is None:
            raise RuntimeError("open_workbook() must be called before reading import results")
        updated_rows = sum(service.actual_updated_rows_count for service in self.per_plan_services.values())
        reset_rows = sum(service.action_counts[service.ACTION_RESET] for service in self.per_plan_services.values())
        total_rows = sum(1 for row in self.ws.iter_rows(min_row=2) if any(cell.value for cell in row))
        return {
            "total_rows": total_rows,
            "updated_rows": updated_rows,
            "reset_rows": reset_rows,
            "ignored_rows": total_rows - updated_rows - reset_rows,
        }
