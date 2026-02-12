import base64
import datetime
import io
import json
from typing import Any
from unittest.mock import patch

from constance.test import override_config
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import pytest

from extras.test_utils.factories import SanctionListIndividualFactory
from hope.apps.sanction_list.tasks.check_against_sanction_list import (
    CheckAgainstSanctionListTask,
)
from hope.models import SanctionListIndividualDateOfBirth, UploadedXLSXFile

pytestmark = pytest.mark.django_db


@pytest.fixture
def uploaded_file():
    return UploadedXLSXFile.objects.create(
        file=SimpleUploadedFile("test.xlsx", b"test"),
        associated_email="test_email@email.com",
    )


@patch("hope.apps.utils.celery_tasks.requests.post")
@patch("hope.apps.sanction_list.tasks.check_against_sanction_list.load_workbook")
@override_settings(EMAIL_SUBJECT_PREFIX="test")
@override_config(ENABLE_MAILJET=True)
@freeze_time("2024-01-10 01:01:01")
def test_sanction_list_email(
    mocked_load_workbook: Any,
    mocked_requests_post: Any,
    uploaded_file,
) -> None:
    class MockLoadWorkbook:
        class MockSheet:
            def iter_rows(self, min_row: int):
                return []

            def __getitem__(self, key: int):
                return []

        worksheets = [MockSheet()]

    mocked_load_workbook.return_value = MockLoadWorkbook()

    CheckAgainstSanctionListTask().execute(uploaded_file.id, "test.xlsx")

    # Build expected attachment
    attachment_wb = Workbook()
    attachment_ws = attachment_wb.active
    attachment_ws.title = "Sanction List Check Results"

    headers = (
        "FIRST NAME",
        "SECOND NAME",
        "THIRD NAME",
        "FOURTH NAME",
        "DATE OF BIRTH",
        "ORIGINAL FILE ROW NUMBER",
    )
    attachment_ws.append(headers)

    for i in range(1, len(headers) + 1):
        attachment_ws.column_dimensions[get_column_letter(i)].width = 30

    buffer = io.BytesIO()
    attachment_wb.save(buffer)
    buffer.seek(0)

    base64_encoded_content = base64.b64encode(buffer.getvalue()).decode("utf-8")

    original_file_name = "test.xlsx"
    subject = (
        f"Sanction List Check - file: {original_file_name}, "
        f"date: {timezone.now().strftime('%Y-%m-%d %I:%M %p')}"
    )

    context = {
        "results": {},
        "results_count": 0,
        "file_name": original_file_name,
        "today_date": timezone.now(),
        "title": "Sanction List Check",
    }

    expected_payload = json.dumps(
        {
            "Messages": [
                {
                    "From": {
                        "Email": settings.DEFAULT_EMAIL,
                        "Name": settings.DEFAULT_EMAIL_DISPLAY,
                    },
                    "Subject": f"[test] {subject}",
                    "To": [{"Email": "test_email@email.com"}],
                    "Cc": [{"Email": settings.SANCTION_LIST_CC_MAIL}],
                    "HTMLPart": render_to_string(
                        "sanction_list/check_results.html",
                        context=context,
                    ),
                    "TextPart": render_to_string(
                        "sanction_list/check_results.txt",
                        context=context,
                    ),
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
        data=expected_payload,
        timeout=30,
    )


def test_join_names_and_birthday_db():
    wb = Workbook()
    ws = wb.active

    individual = SanctionListIndividualFactory(
        first_name="FirstName",
        second_name="SecondName",
        third_name="ThirdName",
        fourth_name="FourthName",
    )

    SanctionListIndividualDateOfBirth.objects.create(
        individual=individual,
        date=datetime.date(1980, 2, 1),
    )
    SanctionListIndividualDateOfBirth.objects.create(
        individual=individual,
        date=datetime.date(1981, 1, 1),
    )

    results_dict = {2: individual}

    task = CheckAgainstSanctionListTask()
    task.join_names_and_birthday(ws, results_dict)

    rows = list(ws.iter_rows(values_only=True))

    assert rows[0][4] == "1980-02-01, 1981-01-01"
    assert rows[0][5] == 2
