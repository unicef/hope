import csv
import dataclasses
import io
import zipfile
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

from django.contrib.admin.options import get_content_type_for_model
from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string

import openpyxl
from openpyxl.styles import Font

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.celery_tasks import send_qcf_report_email_notifications
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.models.payment import (
    WesternUnionQCFFile,
    WesternUnionQCFFileReport,
)
from hct_mis_api.apps.payment.services.western_union_ftp import WesternUnionFTPClient


@dataclasses.dataclass
class QCFReportPaymentRowData:
    mtcn: str
    payment_plan_unicef_id: str
    programme: str
    fc: str
    principal_amount: float
    charges_amount: float
    refund_amount: float


@dataclasses.dataclass
class QCFReportPaymentPlanData:
    payment_plan_unicef_id: str
    principal_total: float = dataclasses.field(init=False)
    charges_total: float = dataclasses.field(init=False)
    refunds_total_positive: float = dataclasses.field(init=False)
    refunds_total_negative: float = dataclasses.field(init=False)
    payments_data: List[QCFReportPaymentRowData]

    def __post_init__(self):
        self.principal_total = sum(p.principal_amount for p in self.payments_data)
        self.charges_total = sum(p.charges_amount for p in self.payments_data)
        self.refunds_total_positive = sum(p.refund_amount for p in self.payments_data if p.refund_amount >= 0)
        self.refunds_total_negative = sum(p.refund_amount for p in self.payments_data if p.refund_amount < 0)


class QCFReportsService:
    class QCFReportsServiceException(Exception):
        pass

    def __init__(self):
        self.ftp_client = WesternUnionFTPClient()

    def process_zip_file(self, filename, file_like) -> None:
        with zipfile.ZipFile(io.BytesIO(file_like.read())) as z:
            for zip_info in z.infolist():
                if zip_info.filename.endswith(".cf") or zip_info.filename.endswith(".CF"):
                    with z.open(zip_info) as txt_file:
                        self.process_report_file(filename, txt_file)

    def process_files_since(self, date_from: datetime) -> None:
        files = self.ftp_client.get_files_since(date_from)
        for filename, file_like in files:
            if not WesternUnionQCFFile.objects.filter(name=filename).exists():
                self.process_zip_file(filename, file_like)

    def store_qu_qcf_file(self, filename: str, file_content: str) -> WesternUnionQCFFile:
        content_file = ContentFile(file_content, name=filename)
        wu_qcf_file = WesternUnionQCFFile.objects.create(
            name=filename,
        )
        file_temp = FileTemp.objects.create(
            object_id=wu_qcf_file.pk,
            content_type=get_content_type_for_model(wu_qcf_file),
            file=content_file,
        )
        file_temp.file.save(filename, content_file)
        wu_qcf_file.file = file_temp
        wu_qcf_file.save()

        return wu_qcf_file

    def process_report_file(self, filename: str, txt_file) -> None:
        file_content = txt_file.read()
        wu_qcf_file = self.store_qu_qcf_file(filename, file_content)

        payment_plan_id_payments_lines_map = defaultdict(list)

        decoded_content = file_content.decode("utf-8")
        lines = list(csv.reader(io.StringIO(decoded_content)))
        for fields in lines[1:-1]:
            record_type = fields[0]
            payment_unicef_id = f"RC{fields[9].strip('\"')}"

            if int(record_type) == 1:  # regular transaction
                try:
                    payment = Payment.objects.get(unicef_id=payment_unicef_id)
                    payment_plan_id_payments_lines_map[payment.parent_id].append((payment, fields))
                except Payment.DoesNotExist:
                    print(f"Payment {payment_unicef_id} does not exist")
                    continue

        for payment_plan_id, payment_raw_data in payment_plan_id_payments_lines_map.items():
            payment_plan = PaymentPlan.objects.get(id=payment_plan_id)

            with transaction.atomic():
                report = self.generate_report(payment_plan, payment_raw_data)

                wu_qcf_report = WesternUnionQCFFileReport.objects.create(
                    name=report.name,
                    qcf_file=wu_qcf_file,
                    payment_plan=payment_plan,
                )
                file_temp = FileTemp.objects.create(
                    object_id=wu_qcf_report.pk,
                    content_type=get_content_type_for_model(wu_qcf_report),
                    file=report,
                )
                file_temp.file.save(filename, report)
                wu_qcf_file.report_file = file_temp
                wu_qcf_file.save()

                transaction.on_commit(
                    lambda wu_qcf_report_id=wu_qcf_report.id: send_qcf_report_email_notifications.delay(
                        wu_qcf_report_id
                    )
                )

    def generate_report(self, payment_plan: PaymentPlan, payment_raw_data: List[Tuple[Payment, dict]]) -> ContentFile:
        no_of_qcf_reports_for_pp = WesternUnionQCFFileReport.objects.filter(payment_plan=payment_plan).count()
        report_filename = (
            f"QCF_{payment_plan.business_area.slug}_{payment_plan.unicef_id}_{no_of_qcf_reports_for_pp + 1}.xlsx"
        )

        funds_commitments = (
            payment_plan.funds_commitments.all().values_list("rec_serial_number", flat=True) or []
        )  # TODO rec_serial_number?
        funds_commitments_str = ", ".join(str(v) for v in funds_commitments) if funds_commitments else "No FC assigned"

        payments_data = []
        for payment, fields in payment_raw_data:
            mtcn = fields[1]
            if mtcn != payment.fsp_auth_code:
                # TODO should we raise it and expose mtcn?
                raise self.QCFReportsServiceException(
                    f"MTCN {mtcn} does not match payment fsp_auth_code for payment {payment.id}"
                )

            payments_data.append(
                QCFReportPaymentRowData(
                    mtcn=fields[1],
                    payment_plan_unicef_id=payment_plan.unicef_id,
                    programme=payment_plan.program_cycle.program.name,
                    fc=funds_commitments_str,
                    principal_amount=fields[10],
                    charges_amount=fields[11],
                    refund_amount=fields[0],
                )
            )

        report_data = QCFReportPaymentPlanData(
            payment_plan_unicef_id=payment_plan.unicef_id, payments_data=payments_data
        )

        return self.generate_report_xlsx(report_filename, report_data)

    def generate_report_xlsx(self, filename: str, report_data: QCFReportPaymentPlanData) -> ContentFile:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"QCF Report - {report_data.payment_plan_unicef_id}"

        headers = ["MTCN", "Payment Plan ID", "Programme", "FC", "Principal Amount", "Charges Amount", "Refund Amount"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for p in report_data.payments_data:
            ws.append(
                [
                    p.mtcn,
                    p.payment_plan_unicef_id,
                    p.programme,
                    p.fc,
                    p.principal_amount,
                    p.charges_amount,
                    p.refund_amount,
                ]
            )

        # empty row before totals
        ws.append([])

        ws.append(["Principal Total", "", "", "", report_data.principal_total])
        ws.append(["Charges Total", "", "", "", report_data.charges_total])
        ws.append(["Refunds Total (positive)", "", "", "", report_data.refunds_total_positive])
        ws.append(["Refunds Total (negative)", "", "", "", report_data.refunds_total_negative])

        last_row = ws.max_row
        for row in range(last_row - 3, last_row + 1):
            ws[f"A{row}"].font = Font(bold=True)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        content_file = ContentFile(output.read(), name=filename)

        return content_file

    def send_notification_emails(self, report: WesternUnionQCFFileReport) -> None:
        """
        # TODO refactor to 'dev' new perms
        role_assignments = RoleAssignment.objects.filter(
            role__permissions__contains=[Permissions.RECEIVE_PARSED_WU_QCF.name],
            business_area=business_area,
        ).exclude(expiry_date__lt=timezone.now())
        users = User.objects.filter(
            Q(role_assignments__in=role_assignments) |
            Q(partner__role_assignments__in=role_assignments)
        ).distinct()
        """
        business_area = report.payment_plan.business_area
        users = [
            user
            for user in User.objects.all()
            if user.has_permission(Permissions.RECEIVE_PARSED_WU_QCF.name, business_area)
        ]

        for user in users:
            self.send_report_email_to_user(user, report)

    def send_report_email_to_user(self, user: User, report: WesternUnionQCFFileReport) -> None:
        text_template = "payment/qcf_report_email.txt"
        html_template = "payment/qcf_report_email.html"

        context = {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": f"Payment Plan {report.payment_plan.unicef_id} Payment List export file's Passwords.",
            "title": f"Payment Plan {report.report_file.file.name} Western Union QCF Report",
            "link": f"Western Union QCF Report file: {report.report_file.file.url}",
        }

        user.email_user(
            subject=context["title"],
            html_body=render_to_string(html_template, context=context),
            text_body=render_to_string(text_template, context=context),
        )
