from pathlib import Path

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import PaymentPlan

from .conftest import payment_plan_url

pytestmark = pytest.mark.django_db()

DOCUMENT_PATH = Path(__file__).resolve().parents[2] / "helpers" / "document_example.png"
DOCUMENT_ITEM = 'div[data-cy="document-item"]'


def test_upload_supporting_document(login: HopeTestBrowser, open_payment_plan: PaymentPlan) -> None:
    login.open(payment_plan_url(open_payment_plan))
    login.wait_for_text("No documents uploaded", 'div[data-cy="supporting-documents-empty"]')

    login.wait_for_element_clickable('button[data-cy="upload-file-button"]').click()
    login.wait_for_element_visible('[data-cy="dialog-import"]')
    login.choose_file('div[role="dialog"] input[type="file"]', str(DOCUMENT_PATH))
    login.type('div[data-cy="title-input"] input', "title input")
    login.wait_for_element_clickable('button[data-cy="button-import-submit"]').click()
    login.wait_for_text("File uploaded successfully")

    # The uploaded document is listed in a collapsed section.
    login.wait_for_element_clickable('button[data-cy="expand-button"]').click()
    login.wait_for_text("title input", DOCUMENT_ITEM)
    login.assert_text("document_example", DOCUMENT_ITEM)
    login.assert_element_absent('div[data-cy="supporting-documents-empty"]')
    document = open_payment_plan.documents.get()
    assert document.title == "title input"
    assert Path(document.file.name).name.startswith("document_example")
