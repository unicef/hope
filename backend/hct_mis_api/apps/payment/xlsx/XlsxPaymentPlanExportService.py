import logging
import zipfile
import openpyxl

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.urls import reverse
from graphql import GraphQLError
from tempfile import NamedTemporaryFile

from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
)
from hct_mis_api.apps.payment.xlsx.BaseXlsxExportService import XlsxExportBaseService
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.core.utils import encode_id_base64


logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportService(XlsxExportBaseService):
    TITLE = "Payment Plan - Payment List"
    HEADERS = (
        "payment_id",
        "household_id",
        "household_size",
        "admin2",
        "collector",
        "payment_channel",
        "fsp",
        "currency",
        "entitlement",
        "entitlement_usd",
    )
    ID_COLUMN_INDEX = 0
    PAYMENT_CHANNEL_COLUMN_INDEX = 5
    ENTITLEMENT_COLUMN_INDEX = 8

    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments

    def _add_payment_row(self, payment: Payment):
        household = payment.household

        payment_row = (
            str(payment.unicef_id),
            str(getattr(household, "unicef_id", "")),
            household.size,
            str(household.admin2.name) if household.admin2 else "",
            str(payment.collector.full_name) if payment.collector else "",
            str(payment.assigned_payment_channel.get_delivery_mechanism_display()) if payment.assigned_payment_channel else "",
            str(payment.financial_service_provider.name) if payment.financial_service_provider else "",
            str(payment.currency),
            payment.entitlement_quantity,
            payment.entitlement_quantity_usd,
        )
        self.ws_export_list.append(payment_row)

    def _add_payment_list(self):
        for payment in self.payment_list:
            self._add_payment_row(payment)

    def generate_workbook(self):
        self._create_workbook()
        self._add_headers()
        self._add_payment_list()
        self._adjust_column_width_from_col(ws=self.ws_export_list, min_row=0, min_col=1, max_col=10)
        self._add_col_bgcolor(
            [
                self.PAYMENT_CHANNEL_COLUMN_INDEX + 1,
                self.ENTITLEMENT_COLUMN_INDEX + 1,
            ]
        )
        return self.wb

    def save_xlsx_file(self, user):
        filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id or self.payment_plan.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.payment_plan.export_xlsx_file = xlsx_obj
            self.payment_plan.save()

    def get_email_context(self, user, per_fsp=False):
        payment_verification_id = encode_id_base64(self.payment_plan.id, "PaymentPlan")
        if per_fsp:
            path_name = "download-payment-plan-payment-list-per-fsp"
        else:
            path_name = "download-payment-plan-payment-list"
        link = self.get_link(reverse(path_name, args=[payment_verification_id]))

        msg = "Payment Plan Payment List xlsx file(s) were generated and below You have the link to download this file."

        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": msg,
            "link": link,
            "title": "Payment Plan Payment List files generated",
        }

        return context

    def export_per_fsp(self, user):
        # after updating this list
        # please update 'map_obj_name_column' as well
        possible_exported_column = [
            "payment_id",
            "household_id",
            "admin_leve_2",
            "collector_name",
            "payment_channel",
            "fsp_name",
            "entitlement_quantity",
            "delivered_quantity",
        ]
        fsp_ids = self.payment_list.values_list("financial_service_provider_id", flat=True)
        fsp_qs = FinancialServiceProvider.objects.filter(id__in=fsp_ids).distinct()

        # create temp zip file
        with NamedTemporaryFile() as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, mode="w") as zip_file:
                for fsp in fsp_qs:
                    wb = openpyxl.Workbook()
                    ws_fsp = wb.active
                    ws_fsp.title = fsp.name

                    payment_qs = self.payment_list.filter(financial_service_provider=fsp)

                    # get headers
                    col_list = FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS
                    if fsp.fsp_xlsx_template and fsp.fsp_xlsx_template.columns:
                        col_list = fsp.fsp_xlsx_template.columns

                    diff_columns = list(set(col_list).difference(set(possible_exported_column)))
                    if diff_columns:
                        msg = f"Please contact admin because we can't export columns: {diff_columns}"
                        logger.error(msg)
                        raise GraphQLError(msg)

                    # add headers
                    ws_fsp.append(col_list)

                    # add rows
                    for payment in payment_qs:
                        self._add_rows(ws_fsp, col_list, fsp, payment)

                    self._adjust_column_width_from_col(ws_fsp, 0, 1, 7)

                    filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}.xlsx"

                    with NamedTemporaryFile() as tmp:
                        wb.save(tmp.name)
                        tmp.seek(0)
                        # add xlsx to zip
                        zip_file.writestr(filename, tmp.read())

            xlsx_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            tmp_zip.seek(0)
            zip_file_name = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.zip"
            xlsx_obj.file.save(zip_file_name, File(tmp_zip))
            self.payment_plan.export_per_fsp_zip_file = xlsx_obj
            self.payment_plan.save()

    @staticmethod
    def _add_rows(ws_fsp, col_list: list, fsp: FinancialServiceProvider, payment: Payment):
        map_obj_name_column = {
            "payment_id": (payment, "unicef_id"),
            "household_id": (payment.household, "unicef_id"),
            "admin_leve_2": (payment.household.admin2, "title"),
            "collector_name": (payment.collector, "full_name"),
            "fsp_name": (fsp, "name"),
            "payment_channel": (payment.assigned_payment_channel, lambda pch: pch.delivery_mechanism),
            "entitlement_quantity": (payment, "entitlement_quantity"),
            "delivered_quantity": (payment, "delivered_quantity"),
        }

        payment_row = tuple()
        for column_name in col_list:
            if column_name not in map_obj_name_column:
                value = "wrong_column_name"
            else:
                obj, value = map_obj_name_column[column_name]
                if callable(value):
                    value = value(obj)
                else:
                    value = getattr(obj, value, "")
                value = value or ""
            payment_row = (*payment_row, value)

        ws_fsp.append(payment_row)
