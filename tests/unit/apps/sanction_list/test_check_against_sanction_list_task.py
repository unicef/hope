import base64
import io
import json
from typing import Any
from unittest.mock import patch

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.utils import timezone

from constance.test import override_config
from freezegun import freeze_time
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from hct_mis_api.apps.sanction_list.models import UploadedXLSXFile
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list import (
    CheckAgainstSanctionListTask,
)


class TestSanctionList(TestCase):
    def setUp(self) -> None:
        self.uploaded_file = UploadedXLSXFile.objects.create(
            file=SimpleUploadedFile("test.xlsx", b"test"),
            associated_email="test_email@email.com",
        )

    @patch("hct_mis_api.apps.utils.celery_tasks.requests.post")
    @patch("hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list.load_workbook")
    @override_settings(EMAIL_SUBJECT_PREFIX="test")
    @override_config(ENABLE_MAILJET=True)
    @freeze_time("2024-01-10 01:01:01")
    def test_sanction_list_email(self, mocked_load_workbook: Any, mocked_requests_post: Any) -> None:
        class MockLoadWorkbook:
            class MockSheet:
                def iter_rows(self, min_row: int) -> list:
                    return []

                def __getitem__(self, key: int) -> list:
                    return []

            worksheets = [MockSheet()]

        mocked_load_workbook.returned_value = MockLoadWorkbook()

        CheckAgainstSanctionListTask().execute(self.uploaded_file.id, "test.xlsx")

        attachment_wb = Workbook()
        attachment_ws = attachment_wb.active
        attachment_ws.title = "Sanction List Check Results"

        header_row_names = (
            "FIRST NAME",
            "SECOND NAME",
            "THIRD NAME",
            "FOURTH NAME",
            "DATE OF BIRTH",
            "ORIGINAL FILE ROW NUMBER",
        )
        attachment_ws.append(header_row_names)
        for i in range(1, len(header_row_names) + 1):
            attachment_ws.column_dimensions[get_column_letter(i)].width = 30
        buffer = io.BytesIO()
        attachment_wb.save(buffer)
        buffer.seek(0)

        attachment_content = buffer.getvalue()
        base64_encoded_content = base64.b64encode(attachment_content).decode("utf-8")

        original_file_name = "test.xlsx"
        context = {
            "results": {},
            "results_count": 0,
            "file_name": original_file_name,
            "today_date": timezone.now(),
            "title": "Sanction List Check",
        }
        subject = (
            f"Sanction List Check - file: {original_file_name}, "
            f"date: {timezone.now().strftime('%Y-%m-%d %I:%M %p')}"
        )
        expected_data = json.dumps(
            {
                "Messages": [
                    {
                        "From": {"Email": settings.DEFAULT_EMAIL, "Name": settings.DEFAULT_EMAIL_DISPLAY},
                        "Subject": f"[test] {subject}",
                        "To": [{"Email": "test_email@email.com"}],
                        "Cc": [{"Email": settings.SANCTION_LIST_CC_MAIL}],
                        "HTMLPart": render_to_string("sanction_list/check_results.html", context=context),
                        "TextPart": render_to_string("sanction_list/check_results.txt", context=context),
                        "Attachments": [
                            {
                                "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "Filename": f"{subject}.xlsx",
                                "Base64Content": base64_encoded_content,
                            }
                        ],
                    }
                ]
            }
        )

        mocked_requests_post.assert_called_once_with(
            "https://api.mailjet.com/v3.1/send",
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            data=expected_data,
        )
