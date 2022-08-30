import openpyxl

from django.contrib.admin.options import get_content_type_for_model
from django.utils import timezone

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import GenericPayment, Payment, PaymentChannel
from hct_mis_api.apps.payment.utils import float_to_decimal
from hct_mis_api.apps.payment.xlsx.BaseXlsxImportService import XlsxImportBaseService
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService


class XlsxPaymentPlanImportService(XlsxImportBaseService):
    COLUMNS_TYPES = ("s", "s", "n", "s", "s", "s", "s", "s", "n", "n")

    def __init__(self, payment_plan, file):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.all_active_payments
        self.payment_plan_content_type = get_content_type_for_model(payment_plan)
        self.file = file
        self.errors = []
        self.updates = None
        self.payments_dict = {
            str(x.unicef_id): x for x in self.payment_list
        }
        self.payment_ids = [str(x.unicef_id) for x in self.payment_list]

        self.payments_to_save = []
        self.payment_channel_update = False
        self.entitlement_update = False

    def open_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.load_workbook(self.file, data_only=True)
        self.wb = wb
        self.ws_payments = wb[XlsxPaymentPlanExportService.TITLE]
        return wb

    def validate(self):
        self._validate_headers()
        self._validate_rows()
        self._validate_imported_file()

    def import_payment_list(self):
        for row in self.ws_payments.iter_rows(min_row=2):
            if not any([cell.value for cell in row]):
                continue
            self._import_row(row)

        Payment.objects.bulk_update(
            self.payments_to_save, ("entitlement_quantity", "entitlement_date", "assigned_payment_channel")
        )

        if self.payments_to_save:
            self.remove_old_export_xlsx_files()

    def _validate_headers(self):
        headers_row = self.ws_payments[1]
        accepted_headers = XlsxPaymentPlanExportService.HEADERS
        if len(headers_row) != len(accepted_headers):
            self.errors.append(
                (
                    XlsxPaymentPlanExportService.TITLE,
                    None,
                    f"Different count of headers. Acceptable headers are: [{accepted_headers}]",
                )
            )
        column = 0
        for header in headers_row:
            if column >= len(accepted_headers):
                self.errors.append(
                    (
                        XlsxPaymentPlanExportService.TITLE,
                        header.coordinate,
                        f"Unexpected header {header.value}",
                    )
                )
            elif header.value != accepted_headers[column]:
                self.errors.append(
                    (
                        XlsxPaymentPlanExportService.TITLE,
                        header.coordinate,
                        f"Unexpected header {header.value} expected {accepted_headers[column]}",
                    )
                )
            column += 1

    def _validate_row_types(self, row):
        column = 0
        for cell in row:
            if cell.value is None:
                column += 1
                continue
            if cell.data_type != XlsxPaymentPlanImportService.COLUMNS_TYPES[column]:
                readable_cell_error = XlsxPaymentPlanImportService.TYPES_READABLE_MAPPING[
                    XlsxPaymentPlanImportService.COLUMNS_TYPES[column]
                ]
                self.errors.append(
                    (
                        XlsxPaymentPlanExportService.TITLE,
                        cell.coordinate,
                        f"Wrong type off cell {readable_cell_error} "
                        f"expected, {XlsxPaymentPlanImportService.TYPES_READABLE_MAPPING[cell.data_type]} given.",
                    )
                )
            column += 1

    def _validate_payment_id(self, row):
        cell = row[XlsxPaymentPlanExportService.ID_COLUMN_INDEX]
        if cell.value not in self.payment_ids:
            self.errors.append(
                (
                    XlsxPaymentPlanExportService.TITLE,
                    cell.coordinate,
                    f"This payment id {cell.value} is not in Payment Plan Payment List",
                )
            )

    def _validate_entitlement(self, row):
        payment_id = row[XlsxPaymentPlanExportService.ID_COLUMN_INDEX].value
        payment = self.payments_dict.get(payment_id)
        if payment is None:
            return
        entitlement_amount = row[XlsxPaymentPlanExportService.ENTITLEMENT_COLUMN_INDEX].value
        if entitlement_amount is not None and entitlement_amount != "":
            entitlement_amount = float_to_decimal(entitlement_amount)
            if entitlement_amount != payment.entitlement_quantity:
                self.entitlement_update = True

    def _validate_payment_channel(self, row):
        payment_id = row[XlsxPaymentPlanExportService.ID_COLUMN_INDEX].value
        payment = self.payments_dict.get(payment_id)
        if payment is None:
            return
        payment_channel = row[XlsxPaymentPlanExportService.PAYMENT_CHANNEL_COLUMN_INDEX].value
        payment_channel_cell = row[XlsxPaymentPlanExportService.PAYMENT_CHANNEL_COLUMN_INDEX]
        if payment_channel not in [x[0] for x in GenericPayment.DELIVERY_TYPE_CHOICE]:
            self.errors.append(
                (
                    XlsxPaymentPlanExportService.TITLE,
                    payment_channel_cell.coordinate,
                    f"Payment_channel should be one of {[x[0] for x in GenericPayment.DELIVERY_TYPE_CHOICE]} "
                    f"but received {payment_channel}",
                )
            )

        if payment.assigned_payment_channel and payment_channel and payment_channel != str(
                payment.assigned_payment_channel.delivery_mechanism):
            self.errors.append(
                (
                    XlsxPaymentPlanExportService.TITLE,
                    payment_channel_cell.coordinate,
                    f"You can't set payment_channel {payment_channel} for Payment with already assigned payment "
                    f"channel {str(payment.assigned_payment_channel.delivery_mechanism)}",
                )
            )
        if not payment.assigned_payment_channel and payment_channel:
            self.payment_channel_update = True

    def _validate_imported_file(self):
        if not self.payment_channel_update and not self.entitlement_update:
            self.errors.append(
                (
                    XlsxPaymentPlanExportService.TITLE,
                    None,
                    "Wrong data. There are no any updates in imported file, please add changes and try again",
                )
            )

    def _validate_rows(self):
        for row in self.ws_payments.iter_rows(min_row=2):
            if not any([cell.value for cell in row]):
                continue
            self._validate_row_types(row)
            self._validate_payment_id(row)
            self._validate_entitlement(row)
            self._validate_payment_channel(row)

    def _import_row(self, row):
        payment_id = row[XlsxPaymentPlanExportService.ID_COLUMN_INDEX].value
        entitlement_amount = row[XlsxPaymentPlanExportService.ENTITLEMENT_COLUMN_INDEX].value
        payment_channel = row[XlsxPaymentPlanExportService.PAYMENT_CHANNEL_COLUMN_INDEX].value
        payment = self.payments_dict[payment_id]
        update = False
        payment_channel_obj = None

        if payment is None:
            return

        if payment_channel is not None and payment_channel != "" and not payment.assigned_payment_channel:
            payment_channel_obj = PaymentChannel.objects.create(
                individual=payment.collector,
                delivery_mechanism=payment_channel
            )

        if entitlement_amount is not None and entitlement_amount != "":
            entitlement_amount = float_to_decimal(entitlement_amount)
            if entitlement_amount != payment.entitlement_quantity:
                payment.entitlement_quantity = entitlement_amount
                payment.entitlement_date = timezone.now()
                update = True
        if payment_channel_obj:
            payment.assigned_payment_channel = payment_channel_obj
            update = True

        if update:
            self.payments_to_save.append(payment)

    def remove_old_export_xlsx_files(self):
        qs = FileTemp.objects.filter(
            object_id=self.payment_plan.pk,
            content_type=self.payment_plan_content_type
        )
        for obj in qs:
            obj.file.delete(save=False)
            obj.delete()

    def remove_old_and_create_new_import_xlsx(self, user):
        # remove old imported file
        if self.payment_plan.imported_xlsx_file:
            self.payment_plan.imported_xlsx_file.file.delete(save=False)
            self.payment_plan.imported_xlsx_file.delete()

        # save new import xlsx file
        xlsx_file = FileTemp.objects.create(
            object_id=self.payment_plan.pk,
            content_type=self.payment_plan_content_type,
            created_by=user,
            file=self.file,
        )
        return xlsx_file
