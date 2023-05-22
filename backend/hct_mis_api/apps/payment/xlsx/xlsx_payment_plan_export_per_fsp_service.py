import logging
import zipfile
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

import openpyxl
from graphql import GraphQLError

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import (
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.utils import generate_numeric_token
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


def token_or_order_number_exists_per_program(payment: Payment, field_name: str, token: int) -> bool:
    return Payment.objects.filter(parent__program=payment.parent.program, **{field_name: token}).exists()


def generate_token_and_order_numbers(payment: Payment) -> Payment:
    # AB#134721
    if payment.order_number or payment.token_number:
        return payment

    order_number = generate_numeric_token(9)
    token_number = generate_numeric_token(7)

    while token_or_order_number_exists_per_program(payment, "order_number", order_number):
        order_number = generate_numeric_token(9)

    while token_or_order_number_exists_per_program(payment, "token_number", token_number):
        token_number = generate_numeric_token(7)

    payment.order_number = order_number
    payment.token_number = token_number
    payment.save(update_fields=["order_number", "token_number"])
    return payment


class XlsxPaymentPlanExportPerFspService(XlsxExportBaseService):
    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.eligible_payments.select_related(
            "household", "collector", "financial_service_provider"
        ).order_by("unicef_id")
        # TODO: in future will be per BA or program flag?
        self.payment_generate_token_and_order_numbers = True

    def export_per_fsp(self, user: "User") -> None:
        # TODO this should be refactored
        # fsp_ids = self.payment_plan.delivery_mechanisms.values_list("financial_service_provider_id", flat=True)
        delivery_mechanism_per_payment_plan_list = self.payment_plan.delivery_mechanisms.select_related(
            "financial_service_provider"
        )

        # fsp_qs = FinancialServiceProvider.objects.filter(id__in=fsp_ids).distinct()
        if not delivery_mechanism_per_payment_plan_list.exists():
            msg = (
                f"Not possible to generate export file. "
                f"There aren't any FSP(s) assigned to Payment Plan {self.payment_plan.unicef_id}."
            )
            logger.error(msg)
            raise GraphQLError(msg)

        # create temp zip file
        with NamedTemporaryFile() as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, mode="w") as zip_file:
                for delivery_mechanism_per_payment_plan in delivery_mechanism_per_payment_plan_list:
                    fsp = delivery_mechanism_per_payment_plan.financial_service_provider
                    wb = openpyxl.Workbook()
                    ws_fsp = wb.active
                    ws_fsp.title = fsp.name
                    fsp_xlsx_template_per_delivery_mechanism = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                        delivery_mechanism=delivery_mechanism_per_payment_plan.delivery_mechanism,
                        financial_service_provider=fsp,
                    ).first()

                    if not fsp_xlsx_template_per_delivery_mechanism:
                        msg = (
                            f"Not possible to generate export file. "
                            f"There isn't any FSP XLSX Template assigned to Payment Plan {self.payment_plan.unicef_id} "
                            f"for FSP {fsp.name} and delivery mechanism {delivery_mechanism_per_payment_plan.delivery_mechanism}."
                        )
                        logger.error(msg)
                        raise GraphQLError(msg)
                    fsp_xlsx_template = fsp_xlsx_template_per_delivery_mechanism.xlsx_template
                    payment_qs = self.payment_list.filter(financial_service_provider=fsp)

                    # get headers
                    column_list = list(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS)
                    template_column_list = []
                    if fsp_xlsx_template and fsp_xlsx_template.columns:
                        template_column_list = fsp_xlsx_template.columns
                        diff_columns = list(set(template_column_list).difference(set(column_list)))
                        if diff_columns:
                            msg = f"Please contact admin because we can't export columns: {diff_columns}"
                            logger.error(msg)
                            raise GraphQLError(msg)
                        column_list = list(template_column_list)

                    for core_field in fsp_xlsx_template.core_fields:
                        column_list.append(core_field)

                    # add headers
                    ws_fsp.append(column_list)

                    # add rows
                    for payment in payment_qs:
                        if self.payment_generate_token_and_order_numbers:
                            payment = generate_token_and_order_numbers(payment)

                        payment_row = [
                            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name)
                            for column_name in template_column_list
                        ]
                        core_fields_row = [
                            FinancialServiceProviderXlsxTemplate.get_column_from_core_field(payment, column_name)
                            for column_name in fsp_xlsx_template.core_fields
                        ]
                        payment_row.extend(core_fields_row)

                        ws_fsp.append(list(map(self.right_format_for_xlsx, payment_row)))

                    self._adjust_column_width_from_col(ws_fsp)

                    filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}_{delivery_mechanism_per_payment_plan.delivery_mechanism}.xlsx"

                    with NamedTemporaryFile() as tmp:
                        wb.save(tmp.name)
                        tmp.seek(0)
                        # add xlsx to zip
                        zip_file.writestr(filename, tmp.read())

            zip_file_name = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.zip"
            zip_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            tmp_zip.seek(0)
            # remove old file
            self.payment_plan.remove_export_file()
            zip_obj.file.save(zip_file_name, File(tmp_zip))
            self.payment_plan.export_file_per_fsp = zip_obj
            self.payment_plan.save()
