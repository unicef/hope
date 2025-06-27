import logging
import string
import zipfile
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import List, Optional

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

import msoffcrypto
import openpyxl
import pyzipper
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import FileTemp, FlexibleAttribute
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.validators import generate_numeric_token
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


def check_if_token_or_order_number_exists_per_program(payment: Payment, field_name: str, token: int) -> bool:
    return Payment.objects.filter(
        parent__program_cycle__program=payment.parent.program_cycle.program, **{field_name: token}
    ).exists()


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
    def __init__(self, payment_plan: PaymentPlan, fsp_xlsx_template_id: Optional[str] = None):
        self.batch_size = 5000
        self.payment_plan = payment_plan
        self.is_social_worker_program = self.payment_plan.is_social_worker_program
        # TODO: in future will be per BA or program flag?
        self.payment_generate_token_and_order_numbers = True
        flexible_attributes = FlexibleAttribute.objects.all()
        self.flexible_attributes = {
            flexible_attribute.name: flexible_attribute for flexible_attribute in flexible_attributes
        }
        self.export_fsp_auth_code = bool(fsp_xlsx_template_id)
        self.fsp_xlsx_template_id = fsp_xlsx_template_id

    def open_workbook(self, title: str) -> tuple[Workbook, Worksheet]:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title

        return wb, ws

    def get_template(
        self, fsp: "FinancialServiceProvider", delivery_mechanism: DeliveryMechanism
    ) -> FinancialServiceProviderXlsxTemplate:
        if (
            self.fsp_xlsx_template_id
            and fsp.communication_channel == FinancialServiceProvider.COMMUNICATION_CHANNEL_API
        ):
            return get_object_or_404(FinancialServiceProviderXlsxTemplate, pk=self.fsp_xlsx_template_id)

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
            # remove fsp_auth_code if fsp_xlsx_template_id not provided
            if not self.export_fsp_auth_code and "fsp_auth_code" in column_list:
                column_list.remove("fsp_auth_code")

        for core_field in fsp_xlsx_template.core_fields:
            column_list.append(core_field)
        for flex_field in fsp_xlsx_template.flex_fields:
            column_list.append(flex_field)
        for document_field in fsp_xlsx_template.document_types:
            column_list.append(document_field)

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
        # remove fsp_auth_code if fsp_xlsx_template_id not provided
        if not self.export_fsp_auth_code and "fsp_auth_code" in fsp_template_columns:
            fsp_template_columns.remove("fsp_auth_code")
        fsp_template_core_fields = self._remove_core_fields_for_people(fsp_xlsx_template.core_fields)
        fsp_template_document_fields = fsp_xlsx_template.document_types

        if self.payment_generate_token_and_order_numbers:
            payment = generate_token_and_order_numbers(payment)

        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name)
            for column_name in fsp_template_columns
        ]
        core_fields_row = [
            FinancialServiceProviderXlsxTemplate.get_column_from_core_field(payment, column_name)
            for column_name in fsp_template_core_fields
        ]
        payment_row.extend(core_fields_row)
        flex_field_row = [
            self._get_flex_field_by_name(column_name, payment) for column_name in fsp_xlsx_template.flex_fields
        ]
        payment_row.extend(flex_field_row)
        # get document number by document type key
        documents_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, doc_type_key)
            for doc_type_key in fsp_template_document_fields
        ]
        payment_row.extend(documents_row)

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

    def save_workbook(
        self, zip_file: zipfile.ZipFile, wb: "Workbook", filename: str, password: Optional[str] = None
    ) -> None:
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)

            if password:
                # encrypt workbook
                output = BytesIO()
                office_file = msoffcrypto.OfficeFile(tmp)
                office_file.load_key(password=password)
                office_file.encrypt(password, output)
                output.seek(0)
                # add xlsx to zip
                zip_file.writestr(filename, output.getvalue())
            else:
                # add xlsx to zip
                zip_file.writestr(filename, tmp.read())

    def create_workbooks_per_split(
        self,
        zip_file: zipfile.ZipFile,
        password: Optional[str] = None,
    ) -> None:
        # there should be only one delivery mechanism/fsp in order to generate split file
        # this is guarded in SplitPaymentPlanMutation

        fsp: FinancialServiceProvider = self.payment_plan.financial_service_provider
        delivery_mechanism: DeliveryMechanism = self.payment_plan.delivery_mechanism
        splits = self.payment_plan.splits.all().order_by("order")
        splits_count = splits.count()
        for i, split in enumerate(splits):
            filename = fsp.name
            if splits_count > 1:
                filename += f"-chunk{i + 1}"
            wb, ws_fsp = self.open_workbook(filename)
            fsp_xlsx_template = self.get_template(fsp, delivery_mechanism)
            payment_ids = list(split.split_payment_items.eligible().order_by("unicef_id").values_list("id", flat=True))
            ws_fsp.append(self.prepare_headers(fsp_xlsx_template))
            self.add_rows(fsp_xlsx_template, payment_ids, ws_fsp)
            self._adjust_column_width_from_col(ws_fsp)
            workbook_name = (
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}_{delivery_mechanism}"
            )
            if splits_count > 1:
                workbook_name += f"_chunk{i + 1}"
            workbook_name += ".xlsx"
            self.save_workbook(
                zip_file,
                wb,
                workbook_name,
                password,
            )

    def export_per_fsp(self, user: "User") -> None:
        with NamedTemporaryFile(suffix=".zip") as tmp_zip:
            zip_file_name = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.zip"

            # generate passwords only if export_fsp_auth_code=True
            password, xlsx_password, encryption_arg = None, None, {}
            if self.export_fsp_auth_code:
                allowed_chars = f"{string.ascii_lowercase}{string.ascii_uppercase}{string.digits}{string.punctuation}"
                password = User.objects.make_random_password(length=12, allowed_chars=allowed_chars)
                xlsx_password = User.objects.make_random_password(length=12, allowed_chars=allowed_chars)
                encryption_arg = {"encryption": pyzipper.WZ_AES}

            with pyzipper.AESZipFile(
                tmp_zip, mode="w", compression=pyzipper.ZIP_DEFLATED, **encryption_arg
            ) as zip_file:
                # set password only for auth code export
                if self.export_fsp_auth_code:
                    zip_file.setpassword(password.encode("utf-8"))

                self.create_workbooks_per_split(zip_file, xlsx_password)

            file_temp_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
                password=password,
                xlsx_password=xlsx_password,
            )
            tmp_zip.seek(0)
            # remove old file
            self.payment_plan.remove_export_files()
            file_temp_obj.file.save(zip_file_name, File(tmp_zip))
            self.payment_plan.export_file_per_fsp = file_temp_obj
            self.payment_plan.save()

    @staticmethod
    def send_email_with_passwords(user: "User", payment_plan: PaymentPlan) -> None:
        text_template = "payment/xlsx_file_password_email.txt"
        html_template = "payment/xlsx_file_password_email.html"

        msg = (
            f"Payment Plan {payment_plan.unicef_id} Payment List export file's Passwords.\n"
            f"ZIP file password: {payment_plan.export_file_per_fsp.password}\n"
            f"XLSX file password: {payment_plan.export_file_per_fsp.xlsx_password}\n"
        )

        context = {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "title": f"Payment Plan {payment_plan.unicef_id} Payment List file's Passwords",
            "link": "",
        }
        user.email_user(
            subject=context["title"],
            html_body=render_to_string(html_template, context=context),
            text_body=render_to_string(text_template, context=context),
        )
