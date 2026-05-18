from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.models import FileTemp, FollowUpInstruction, Payment, PaymentPlan

if TYPE_CHECKING:
    from openpyxl import Workbook

    from hope.models import User


class XlsxFollowUpInstructionBaseExportService(XlsxExportBaseService, ABC):
    TITLE = "Follow Up Instruction"
    SUMMABLE_HEADERS = {
        "entitlement_quantity",
        "entitlement_quantity_usd",
        "delivered_quantity",
    }

    def __init__(self, instruction: FollowUpInstruction):
        self.instruction = instruction
        self.payment_plan = self._get_representative_payment_plan()
        self.headers = self._prepare_headers()

    def _get_representative_payment_plan(self) -> PaymentPlan:
        payment_plan = (
            self.instruction.payment_plans.select_related(
                "delivery_mechanism",
                "financial_service_provider",
            )
            .order_by("created_at")
            .first()
        )
        if payment_plan is None:
            raise ValueError("Follow Up Instruction has no child Payment Plans.")
        return payment_plan

    def _prepare_headers(self) -> list[str]:
        headers = list(self.get_source_headers())
        if "payment_id" in headers:
            headers[headers.index("payment_id")] = "household_unicef_id"
        elif "household_unicef_id" not in headers:
            headers.insert(0, "household_unicef_id")
        return list(dict.fromkeys(headers))

    @staticmethod
    def _is_empty(value: Any) -> bool:
        return value in (None, "")

    @staticmethod
    def _as_decimal(value: Any) -> Decimal:
        if value in (None, ""):
            return Decimal(0)
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _build_payment_row(self, payment: Payment) -> dict[str, Any]:
        payment_row = self.get_payment_row_data(payment)
        payment_row.pop("payment_id", None)
        payment_row["household_unicef_id"] = payment_row.get("household_id") or payment.household.unicef_id
        return {header: payment_row.get(header, "") for header in self.headers}

    def _merge_rows(self, existing_row: dict[str, Any], payment_row: dict[str, Any]) -> dict[str, Any]:
        merged = dict(existing_row)
        for header in self.headers:
            if header == "household_unicef_id":
                continue
            if header in self.SUMMABLE_HEADERS:
                merged[header] = self._as_decimal(existing_row.get(header)) + self._as_decimal(payment_row.get(header))
                continue
            if self._is_empty(merged.get(header)) and not self._is_empty(payment_row.get(header)):
                merged[header] = payment_row.get(header)
        return merged

    def _iter_aggregated_rows(self) -> list[dict[str, Any]]:
        aggregated_rows: dict[str, dict[str, Any]] = {}
        payments = (
            Payment.objects.filter(parent__follow_up_instruction=self.instruction)
            .eligible()
            .select_related(
                "household",
                "household_snapshot",
                "currency",
                "delivery_type",
                "financial_service_provider",
                "parent",
            )
            .order_by("parent__created_at", "created_at", "unicef_id")
        )
        for payment in payments.iterator(chunk_size=2000):
            payment_row = self._build_payment_row(payment)
            household_unicef_id = str(payment_row["household_unicef_id"])
            if household_unicef_id not in aggregated_rows:
                aggregated_rows[household_unicef_id] = payment_row
                continue
            aggregated_rows[household_unicef_id] = self._merge_rows(aggregated_rows[household_unicef_id], payment_row)
        return list(aggregated_rows.values())

    def generate_workbook(self) -> Workbook:
        self._create_workbook()
        self.ws_export_list.append(self.headers)
        for payment_row in self._iter_aggregated_rows():
            self.ws_export_list.append([self.right_format_for_xlsx(payment_row.get(header)) for header in self.headers])
        self._adjust_column_width_from_col(self.ws_export_list)
        highlighted_columns = [
            self.headers.index(header) + 1
            for header in ("entitlement_quantity", "delivered_quantity")
            if header in self.headers
        ]
        self._add_col_bgcolor(highlighted_columns)
        return self.wb

    def save_xlsx_file(self, user: User) -> None:
        filename = f"{self.filename_prefix}_{self.instruction.unicef_id or self.instruction.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            xlsx_obj = FileTemp(
                object_id=str(self.instruction.pk),
                content_type=get_content_type_for_model(self.instruction),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            if self.instruction.export_file:
                self.instruction.remove_export_file()
            xlsx_obj.file.save(filename, File(tmp))
            self.instruction.export_file = xlsx_obj
            self.instruction.save(update_fields=["export_file", "updated_at"])

    @property
    @abstractmethod
    def filename_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_source_headers(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_payment_row_data(self, payment: Payment) -> dict[str, Any]:
        raise NotImplementedError
