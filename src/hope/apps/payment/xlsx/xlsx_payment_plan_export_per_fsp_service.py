from io import BytesIO
import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING
import zipfile

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
import msoffcrypto
import openpyxl
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
import pyzipper

from hope.apps.core.field_attributes.core_fields_attributes import (
    FieldFactory,
    get_core_fields_attributes,
)
from hope.apps.payment.validators import generate_numeric_token
from hope.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService
from hope.apps.utils.exceptions import log_and_raise
from hope.models import (
    DeliveryMechanism,
    FileTemp,
    FinancialServiceProviderXlsxTemplate,
    FlexibleAttribute,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    Program,
)

if TYPE_CHECKING:
    from hope.models import FinancialServiceProvider, User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportPerFspService(XlsxExportBaseService):
    def __init__(self, payment_plan: PaymentPlan, fsp_xlsx_template_id: str | None = None):
        self.batch_size = 2000
        self.payment_plan = payment_plan
        self.is_social_worker_program = self.payment_plan.is_social_worker_program
        # TODO: in future will be per BA or program flag?
        self.payment_generate_token_and_order_numbers = True
        self.flexible_attributes = {
            flexible_attribute.name: flexible_attribute for flexible_attribute in FlexibleAttribute.objects.all()
        }
        self.allow_export_fsp_auth_code = self.payment_plan.is_payment_gateway_and_all_sent_to_fsp
        self.fsp_xlsx_template_id = fsp_xlsx_template_id
        self.fsp_xlsx_template: FinancialServiceProviderXlsxTemplate | None = None
        self.account_fields_headers = self.get_account_fields_headers()
        self.header_list = []
        self.template_columns = []
        self.core_fields = []
        self.flex_fields = []
        self.document_fields = []
        self.core_fields_attributes = FieldFactory(get_core_fields_attributes()).to_dict_by("name")
        self.admin_areas_dict = FinancialServiceProviderXlsxTemplate.get_areas_dict()
        self.countries_dict = FinancialServiceProviderXlsxTemplate.get_countries_dict()

    def generate_token_and_order_numbers(
        self,
        qs: QuerySet[Payment],
        program: Program,
    ) -> None:
        """Ensure order_number/token_number for all rows in qs."""
        existing_orders: set[int] = set(
            Payment.objects.filter(order_number__isnull=False, parent__program_cycle__program=program).values_list(
                "order_number", flat=True
            )
        )
        existing_tokens: set[int] = set(
            Payment.objects.filter(token_number__isnull=False, parent__program_cycle__program=program).values_list(
                "token_number", flat=True
            )
        )

        missing_qs = qs.filter(Q(order_number__isnull=True) | Q(token_number__isnull=True))
        payments_ids = list(missing_qs.order_by("id").values_list("id", flat=True))

        if not payments_ids:
            return

        payments = list(qs.only("id", "order_number", "token_number"))
        if not payments:  # pragma: no cover
            return

        to_update: list[Payment] = []

        for payment in payments:
            need_order = payment.order_number is None
            need_token = payment.token_number is None

            if not (need_order or need_token):  # pragma: no cover
                continue

            if need_order:
                n9 = generate_numeric_token(9)
                while n9 in existing_orders:  # pragma: no cover
                    n9 = generate_numeric_token(9)
                payment.order_number = n9
                existing_orders.add(n9)

            if need_token:
                n7 = generate_numeric_token(7)
                while n7 in existing_tokens:  # pragma: no cover
                    n7 = generate_numeric_token(7)
                payment.token_number = n7
                existing_tokens.add(n7)

            to_update.append(payment)

        if to_update:
            Payment.objects.bulk_update(to_update, ["order_number", "token_number"])

    def get_account_fields_headers(self) -> list[str]:
        # Iterate over eligible payments to find the first with valid account_data
        qs = (
            self.payment_plan.eligible_payments.select_related("household_snapshot")
            .only("id", "household_snapshot__snapshot_data")  # keep it minimal
            .filter(
                Q(household_snapshot__snapshot_data__primary_collector__has_key="account_data")
                | Q(household_snapshot__snapshot_data__alternate_collector__has_key="account_data")
            )
            .order_by("unicef_id")
        )
        for payment in qs:
            snapshot = getattr(payment, "household_snapshot", None)
            snapshot_data = snapshot.snapshot_data if snapshot else {}
            collector_data = (
                snapshot_data.get("primary_collector", {}) or snapshot_data.get("alternate_collector", {}) or {}
            )
            account_data = collector_data.get("account_data", {})
            if account_data:
                headers = list(account_data.keys())
                if "financial_institution_pk" not in headers:
                    headers.append("financial_institution_pk")
                if "financial_institution_name" not in headers:
                    headers.append("financial_institution_name")
                if "number" not in headers:
                    headers.append("number")
                return headers
        return []

    def open_workbook(self, title: str) -> tuple[Workbook, Worksheet]:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title

        return wb, ws

    def get_template(
        self, fsp: "FinancialServiceProvider", delivery_mechanism: DeliveryMechanism
    ) -> FinancialServiceProviderXlsxTemplate | None:
        if self.fsp_xlsx_template_id:
            self.fsp_xlsx_template = get_object_or_404(
                FinancialServiceProviderXlsxTemplate, pk=self.fsp_xlsx_template_id
            )
            return self.fsp_xlsx_template

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
        self.fsp_xlsx_template = fsp_xlsx_template_per_delivery_mechanism.xlsx_template
        return self.fsp_xlsx_template

    def _remove_column_for_people(self, fsp_template_columns: list[str]) -> list[str]:
        """Remove columns and return list."""
        if self.is_social_worker_program:
            return list(
                filter(
                    lambda col_name: col_name not in ["household_id", "household_size"],
                    fsp_template_columns,
                )
            )
        return list(filter(lambda col_name: col_name not in ["individual_id"], fsp_template_columns))

    def _remove_core_fields_for_people(self, fsp_template_core_fields: list[str]) -> list[str]:
        """Remove columns and return list."""
        if self.is_social_worker_program:
            return list(
                filter(
                    lambda col_name: col_name not in ["household_unicef_id"],
                    fsp_template_core_fields,
                )
            )
        return list(fsp_template_core_fields)

    def prepare_headers(self, fsp_xlsx_template: "FinancialServiceProviderXlsxTemplate") -> list[str]:
        # get headers
        add_accounts_fields = False
        column_list = list(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS)
        if fsp_xlsx_template and fsp_xlsx_template.columns:
            template_column_list = fsp_xlsx_template.columns
            diff_columns = list(set(template_column_list).difference(set(column_list)))
            if diff_columns:
                msg = f"Please contact admin because we can't export columns: {diff_columns}"
                log_and_raise(msg)
            column_list = list(template_column_list)

        # remove fsp_auth_code if exporting is not allowed
        if not self.allow_export_fsp_auth_code and "fsp_auth_code" in column_list:
            column_list.remove("fsp_auth_code")

        if "account_data" in column_list:
            column_list.remove("account_data")
            add_accounts_fields = True

        column_list = self._remove_column_for_people(column_list)
        self.template_columns = column_list.copy()

        self.core_fields = self._remove_core_fields_for_people(fsp_xlsx_template.core_fields)
        column_list.extend(self.core_fields)

        self.flex_fields = list(fsp_xlsx_template.flex_fields)
        column_list.extend(self.flex_fields)

        self.document_fields = list(fsp_xlsx_template.document_types)
        column_list.extend(self.document_fields)

        # add headers for Account from FSP in PaymentPlan
        if add_accounts_fields:
            column_list.extend(self.account_fields_headers)

        self.header_list = column_list
        return self.header_list

    def add_rows(
        self,
        split: PaymentPlanSplit,
        ws: "Worksheet",
    ) -> None:
        qs = (
            split.split_payment_items.eligible()
            .select_related(
                "household_snapshot",
                "delivery_type",
                "financial_service_provider",
            )
            .order_by("unicef_id")
        )
        for payment in qs.iterator(chunk_size=self.batch_size):
            ws.append(self.get_payment_row(payment))

    def get_payment_row(self, payment: Payment) -> list[str]:
        payment_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
                payment, column_name, self.admin_areas_dict
            )
            for column_name in self.template_columns
        ]
        core_fields_row = [
            FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
                payment, column_name, self.admin_areas_dict, self.countries_dict
            )
            for column_name in self.core_fields
        ]
        payment_row.extend(core_fields_row)
        flex_field_row = [self._get_flex_field_by_name(column_name, payment) for column_name in self.flex_fields]
        payment_row.extend(flex_field_row)
        # get document number by document type key
        documents_row = [
            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
                payment, doc_type_key, self.admin_areas_dict
            )
            for doc_type_key in self.document_fields
        ]
        payment_row.extend(documents_row)

        accounts_row = [
            FinancialServiceProviderXlsxTemplate.get_account_value_from_payment(payment, account_key)
            for account_key in self.account_fields_headers
        ]
        payment_row.extend(accounts_row)

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
        collector_data = primary_collector or alternate_collector or {}

        if attribute.associated_with == FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL:
            return collector_data.get("flex_fields", {}).get(name, "")
        return snapshot_data.get("flex_fields", {}).get(name, "")

    def save_workbook(
        self,
        zip_file: zipfile.ZipFile,
        wb: "Workbook",
        filename: str,
        password: str | None = None,
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
        password: str | None = None,
    ) -> None:
        # there should be only one delivery mechanism/fsp in order to generate split file
        # this is guarded in SplitPaymentPlanMutation

        fsp: "FinancialServiceProvider" = self.payment_plan.financial_service_provider
        delivery_mechanism: DeliveryMechanism = self.payment_plan.delivery_mechanism
        splits = self.payment_plan.splits.all().order_by("order")
        splits_count = splits.count()
        for i, split in enumerate(splits):
            filename = fsp.name
            if splits_count > 1:
                filename += f"-chunk{i + 1}"
            wb, ws_fsp = self.open_workbook(filename)
            fsp_xlsx_template = self.get_template(fsp, delivery_mechanism)
            ws_fsp.append(self.prepare_headers(fsp_xlsx_template))  # type: ignore
            self.add_rows(split, ws_fsp)
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

            # generate passwords only if allow_export_fsp_auth_code=True
            password, xlsx_password, encryption_arg = None, None, {}
            if self.allow_export_fsp_auth_code:
                password = get_random_string(12)
                xlsx_password = get_random_string(12)
                encryption_arg = {"encryption": pyzipper.WZ_AES}

            with pyzipper.AESZipFile(
                tmp_zip, mode="w", compression=pyzipper.ZIP_DEFLATED, **encryption_arg
            ) as zip_file:
                # set password only for auth code export
                if self.allow_export_fsp_auth_code:
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
            with transaction.atomic():
                self.payment_plan.remove_export_files()
                file_temp_obj.file.save(zip_file_name, File(tmp_zip))
                self.payment_plan.export_file_per_fsp = file_temp_obj
                self.payment_plan.background_action_status_none()
                self.payment_plan.save(update_fields=["background_action_status", "export_file_per_fsp", "updated_at"])

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
