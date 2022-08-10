import logging
import openpyxl

from openpyxl.utils import get_column_letter
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


class XlsxBaseExportService:
    TITLE = "Xlsx Export"
    HEADERS = tuple()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_active = wb.active
        ws_active.title = XlsxBaseExportService.TITLE
        self.wb = wb
        self.ws_export_list = ws_active
        return wb

    def _add_headers(self):
        self.ws_export_list.append(XlsxBaseExportService.HEADERS)

    def generate_workbook(self):
        self._create_workbook()
        self._add_headers()
        # add export items and what you need
        return self.wb

    def generate_file(self, filename):
        self.generate_workbook()
        self.wb.save(filename=filename)

    @staticmethod
    def _adjust_column_width_from_col(ws, min_row, min_col, max_col):
        column_widths = []

        for i, col in enumerate(ws.iter_cols(min_col=min_col, max_col=max_col, min_row=min_row)):

            for cell in col:
                value = cell.value
                if value is not None:

                    if isinstance(value, str) is False:
                        value = str(value)

                    try:
                        column_widths[i] = max(column_widths[i], len(value))
                    except IndexError:
                        column_widths.append(len(value))

        for i, width in enumerate(column_widths):
            col_name = get_column_letter(min_col + i)
            value = column_widths[i] + 2
            ws.column_dimensions[col_name].width = value

    @staticmethod
    def get_link(api_url=None) -> str:
        protocol = "http" if settings.IS_DEV else "https"
        link = f"{protocol}://{settings.FRONTEND_HOST}{api_url}"
        if api_url:
            return link
        return ""

    def send_email(self, context):
        text_body = render_to_string("payment/xlsx_file_generated_email.txt", context=context)
        html_body = render_to_string("payment/xlsx_file_generated_email.html", context=context)

        email = EmailMultiAlternatives(
            subject=context["title"],
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")
