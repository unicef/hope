import logging
import zipfile
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, List

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db.models import QuerySet

import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from hct_mis_api.apps.core.models import FileTemp, FlexibleAttribute
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.validators import generate_numeric_token
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hct_mis_api.apps.utils.exceptions import log_and_raise

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


def check_if_token_or_order_number_exists_per_program(payment: Payment, field_name: str, token: int) -> bool:
    return Payment.objects.filter(parent__program=payment.parent.program, **{field_name: token}).exists()


def generate_token_and_order_numbers(payment: Payment) -> Payment:
    # AB#134721
    if payment.order_number and payment.token_number:
        return payment

    order_number = generate_numeric_token(9)
    token_number = generate_numeric_token(7)

    while check_if_token_or_order_number_exists_per_program(payment, "order_number", order_number):
        order_number = generate_numeric_token(9)

    while check_if_token_or_order_number_exists_per_program(payment, "token_number", token_number):
        token_number = generate_numeric_token(7)

    payment.order_number = order_number
    payment.token_number = token_number
    payment.save(update_fields=["order_number", "token_number"])
    return payment


class XlsxPaymentPlanExportPerFspService(XlsxExportBaseService):
    def __init__(self, payment_plan: PaymentPlan):
        self.batch_size = 5000
        self.payment_plan = payment_plan
        self.is_social_worker_program = self.payment_plan.program.is_social_worker_program
        # TODO: in future will be per BA or program flag?
        self.payment_generate_token_and_order_numbers = True
        flexible_attributes = FlexibleAttribute.objects.all()
        self.flexible_attributes = {
            flexible_attribute.name: flexible_attribute for flexible_attribute in flexible_attributes
        }

    def open_workbook(self, title: str) -> tuple[Workbook, Worksheet]:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title

        return wb, ws

    def get_template(
        self, fsp: "FinancialServiceProvider", delivery_mechanism: DeliveryMechanism
    ) -> FinancialServiceProviderXlsxTemplate:
        fsp_xlsx_template_per_delivery_mechanism = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
            delivery_mechanism=delivery_mechanism,
            financial_service_provider=fsp,
        ).first()

        if not fsp_xlsx_template_per_delivery_mechanism:
            msg = (
                f"Not possible to generate export file. "
                f"There isn't any FSP XLSX Template assigned to Payment Plan {self.payment_plan.unicef_id} "
                f"for FSP {fsp.name} and delivery mechanism {delivery_mechanism}."
            )
            log_and_raise(msg)

        return fsp_xlsx_template_per_delivery_mechanism.xlsx_template

    def _remove_column_for_people(self, fsp_template_columns: List[str]) -> List[str]:
        """remove columns and return list"""
        if self.is_social_worker_program:
            return list(
                filter(lambda col_name: col_name not in ["household_id", "household_size"], fsp_template_columns)
            )
        return list(filter(lambda col_name: col_name not in ["individual_id"], fsp_template_columns))

    def _remove_core_fields_for_people(self, fsp_template_core_fields: List[str]) -> List[str]:
        """remove columns and return list"""
        if self.is_social_worker_program:
            return list(filter(lambda col_name: col_name not in ["household_unicef_id"], fsp_template_core_fields))
        return list(fsp_template_core_fields)

    def prepare_headers(self, fsp_xlsx_template: "FinancialServiceProviderXlsxTemplate") -> List[str]:
        # get headers
        column_list = list(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS)
        if fsp_xlsx_template and fsp_xlsx_template.columns:
            template_column_list = fsp_xlsx_template.columns
            diff_columns = list(set(template_column_list).difference(set(column_list)))
            if diff_columns:
                msg = f"Please contact admin because we can't export columns: {diff_columns}"
                log_and_raise(msg)
            column_list = list(template_column_list)

        for core_field in fsp_xlsx_template.core_fields:
            column_list.append(core_field)
        for flex_field in fsp_xlsx_template.flex_fields:
            column_list.append(flex_field)

        column_list = self._remove_column_for_people(column_list)
        column_list = self._remove_core_fields_for_people(column_list)
        return column_list

    def add_rows(
        self,
        fsp_xlsx_template: "FinancialServiceProviderXlsxTemplate",
        payment_ids: List[int],
        ws: "Worksheet",
    ) -> None:
        for i in range(0, len(payment_ids), self.batch_size):
            batch_ids = payment_ids[i : i + self.batch_size]
            payment_qs = Payment.objects.filter(id__in=batch_ids).order_by("unicef_id")

            for payment in payment_qs:
                ws.append(self.get_payment_row(payment, fsp_xlsx_template))

    def get_payment_row(self, payment: Payment, fsp_xlsx_template: "FinancialServiceProviderXlsxTemplate") -> List[str]:
        fsp_template_columns = self._remove_column_for_people(fsp_xlsx_template.columns)
        fsp_template_core_fields = self._remove_core_fields_for_people(fsp_xlsx_template.core_fields)

        if self.payment_generate_token_and_order_numbers:
            payment = generate_token_and_order_numbers(payment)
        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name)
            for column_name in fsp_template_columns
        ]
        delivery_mechanism_data = payment.collector.delivery_mechanisms_data.filter(
            delivery_mechanism=payment.delivery_type
        ).first()
        core_fields_row = [
            FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
                payment, column_name, delivery_mechanism_data
            )
            for column_name in fsp_template_core_fields
        ]
        payment_row.extend(core_fields_row)
        flex_field_row = [
            self._get_flex_field_by_name(column_name, payment) for column_name in fsp_xlsx_template.flex_fields
        ]
        payment_row.extend(flex_field_row)
        return list(map(self.right_format_for_xlsx, payment_row))

    def _get_flex_field_by_name(self, name: str, payment: Payment) -> str:
        attribute: FlexibleAttribute = self.flexible_attributes[name]

        snapshot = getattr(payment, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {payment.unicef_id}")
            return ""

        snapshot_data = snapshot.snapshot_data
        primary_collector = snapshot_data.get("primary_collector", {})
        alternate_collector = snapshot_data.get("alternate_collector", {})
        collector_data = primary_collector or alternate_collector or dict()

        if attribute.associated_with == FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL:
            return collector_data.get("flex_fields", {}).get(name, "")
        else:
            return snapshot_data.get("flex_fields", {}).get(name, "")

    def save_workbook(self, zip_file: zipfile.ZipFile, wb: "Workbook", filename: str) -> None:
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            # add xlsx to zip
            zip_file.writestr(filename, tmp.read())

    def create_workbooks_per_fsp(
        self,
        delivery_mechanism_per_payment_plan_list: QuerySet["DeliveryMechanismPerPaymentPlan"],
        zip_file: zipfile.ZipFile,
    ) -> None:
        for delivery_mechanism_per_payment_plan in delivery_mechanism_per_payment_plan_list:
            fsp: FinancialServiceProvider = delivery_mechanism_per_payment_plan.financial_service_provider
            delivery_mechanism: DeliveryMechanism = delivery_mechanism_per_payment_plan.delivery_mechanism
            wb, ws_fsp = self.open_workbook(fsp.name)
            fsp_xlsx_template = self.get_template(fsp, delivery_mechanism)
            payment_ids = list(
                self.payment_plan.eligible_payments.filter(financial_service_provider=fsp)
                .order_by("unicef_id")
                .values_list("id", flat=True)
            )
            ws_fsp.append(self.prepare_headers(fsp_xlsx_template))
            self.add_rows(fsp_xlsx_template, payment_ids, ws_fsp)
            self._adjust_column_width_from_col(ws_fsp)
            self.save_workbook(
                zip_file,
                wb,
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}_{delivery_mechanism_per_payment_plan.delivery_mechanism}.xlsx",
            )

    def create_workbooks_per_split(
        self,
        delivery_mechanism_per_payment_plan_list: QuerySet["DeliveryMechanismPerPaymentPlan"],
        zip_file: zipfile.ZipFile,
    ) -> None:
        # there should be only one delivery mechanism/fsp in order to generate split file
        # this is guarded in SplitPaymentPlanMutation

        delivery_mechanism_per_payment_plan: DeliveryMechanismPerPaymentPlan = (
            delivery_mechanism_per_payment_plan_list.first()  # type: ignore
        )
        fsp: FinancialServiceProvider = delivery_mechanism_per_payment_plan.financial_service_provider
        delivery_mechanism: DeliveryMechanism = delivery_mechanism_per_payment_plan.delivery_mechanism
        for i, split in enumerate(self.payment_plan.splits.all().order_by("order")):
            wb, ws_fsp = self.open_workbook(f"{fsp.name}-chunk{i + 1}")
            fsp_xlsx_template = self.get_template(fsp, delivery_mechanism)
            payment_ids = list(split.payments.all().order_by("unicef_id").values_list("id", flat=True))
            ws_fsp.append(self.prepare_headers(fsp_xlsx_template))
            self.add_rows(fsp_xlsx_template, payment_ids, ws_fsp)
            self._adjust_column_width_from_col(ws_fsp)
            self.save_workbook(
                zip_file,
                wb,
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}_{delivery_mechanism_per_payment_plan.delivery_mechanism}_chunk{i + 1}.xlsx",
            )

    def export_per_fsp(self, user: "User") -> None:
        delivery_mechanism_per_payment_plan_list = self.payment_plan.delivery_mechanisms.select_related(
            "financial_service_provider"
        )

        if not delivery_mechanism_per_payment_plan_list.exists():
            msg = (
                f"Not possible to generate export file. "
                f"There aren't any FSP(s) assigned to Payment Plan {self.payment_plan.unicef_id}."
            )
            log_and_raise(msg)

        # create temp zip file
        with NamedTemporaryFile() as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, mode="w") as zip_file:
                if self.payment_plan.splits.exists():
                    self.create_workbooks_per_split(delivery_mechanism_per_payment_plan_list, zip_file)
                else:
                    self.create_workbooks_per_fsp(delivery_mechanism_per_payment_plan_list, zip_file)

            zip_file_name = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.zip"
            zip_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            tmp_zip.seek(0)
            # remove old file
            self.payment_plan.remove_export_files()
            zip_obj.file.save(zip_file_name, File(tmp_zip))
            self.payment_plan.export_file_per_fsp = zip_obj
            self.payment_plan.save()
