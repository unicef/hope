from tempfile import NamedTemporaryFile

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.urls import reverse

from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.payment.xlsx.BaseXlsxExportService import XlsxExportBaseService
from hct_mis_api.apps.core.models import XLSXFileTemp
from hct_mis_api.apps.core.utils import encode_id_base64


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

    def __init__(self, payment_plan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments

    def _add_payment_row(self, payment: Payment):
        household = payment.household

        payment_row = (
            str(payment.unicef_id),
            str(getattr(household, "unicef_id", "")),
            household.size,
            str(household.admin2.title) if household.admin2 else "",
            str(payment.collector.full_name) if payment.collector else "",
            str(payment.assigned_payment_channel.delivery_mechanism) if payment.assigned_payment_channel else "",
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
        self._adjust_column_width_from_col(self.ws_export_list, 0, 1, 7)
        self._add_col_bgcolor([6, 9])
        return self.wb

    def save_xlsx_file(self, user):
        filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id or self.payment_plan.id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = XLSXFileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
                type=XLSXFileTemp.EXPORT
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))

    def get_context(self, user):
        payment_verification_id = encode_id_base64(self.payment_plan.id, "PaymentPlan")
        link = self.get_link(reverse("download-payment-plan-payment-list", args=[payment_verification_id]))

        msg = "Payment Plan Payment List xlsx file was generated and below You have the link to download this file."

        context = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": msg,
            "link": link,
            "title": "Payment Plan Payment List XLSX file generated",
        }

        return context
