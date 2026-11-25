import pytest

from e2e.new_selenium.accountability.conftest import (
    RECIPIENT_COLUMNS,
    TARGET_POPULATION_NAME,
    assert_single_page,
    assert_texts,
    open_accountability_page,
)
from extras.test_utils.factories import CommunicationMessageFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Message, PaymentList, Program, User

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_TITLE = 'h6[data-cy="table-title"]'
ROWS = 'tr[role="checkbox"]'
BUTTON_NEW_MESSAGE = 'a[data-cy="button-communication-create-new"]'
FILTERS = {
    'div[data-cy="filters-target-population-autocomplete"]': "Target Population",
    'div[data-cy="Target Population-input"]': "Target Population",
    'div[data-cy="filters-created-by-autocomplete"]': "Created by",
    'div[data-cy="Created by-input"]': "Created by",
    'div[data-cy="filters-creation-date-from"]': "From",
    'div[data-cy="filters-creation-date-to"]': "To",
    'button[data-cy="button-filters-clear"]': "CLEAR",
    'button[data-cy="button-filters-apply"]': "APPLY",
}
LABEL_CREATED_BY = 'div[data-cy="label-Created By"]'
LABEL_DATE_CREATED = 'div[data-cy="label-Date Created"]'
LABEL_TARGET_POPULATION = 'div[data-cy="label-Target Population"]'
MESSAGE_DETAILS = 'div[data-cy="communication-message-details"]'
TABLE_ROW = 'tr[data-cy="table-row"]'
LIST_COLUMNS = {
    "thead th:nth-child(1)": "Message ID",
    "thead th:nth-child(2)": "Title",
    "thead th:nth-child(3)": "Number of Recipients",
    "thead th:nth-child(4)": "Created by",
    "thead th:nth-child(5)": "Creation Date",
}

MESSAGE_TITLE = "You got credit of USD 100"
MESSAGE_BODY = "Greetings, we have sent you USD 100 in your registered account on 2022-09-19 20:00:00 UTC"


@pytest.fixture
def message(program: Program, target_population: PaymentList, author: User) -> Message:
    return CommunicationMessageFactory(
        title=MESSAGE_TITLE,
        body=MESSAGE_BODY,
        business_area=program.business_area,
        program=program,
        payment_list=target_population,
        created_by=author,
    )


def test_communication_list_shows_message(message: Message, program: Program, login: HopeTestBrowser) -> None:
    open_accountability_page(login, program, "Communication")

    login.assert_text("NEW MESSAGE", BUTTON_NEW_MESSAGE)
    assert_texts(login, FILTERS)
    login.assert_text("Messages List", TABLE_TITLE)
    assert_single_page(login, "1–1 of 1")
    login.assert_text(message.unicef_id, ROWS)
    login.assert_text(MESSAGE_TITLE, ROWS)
    login.assert_text("Alice Author", ROWS)
    assert_texts(login, LIST_COLUMNS)
    assert len(login.find_elements(ROWS)) == 1


def test_communication_details_shows_message(message: Message, program: Program, login: HopeTestBrowser) -> None:
    open_accountability_page(login, program, "Communication")

    login.click(ROWS)

    login.assert_text(message.unicef_id, PAGE_HEADER_TITLE)
    login.assert_text("Alice Author", LABEL_CREATED_BY)
    login.assert_text(message.created_at.strftime("%-d %b %Y"), LABEL_DATE_CREATED)
    login.assert_text(TARGET_POPULATION_NAME, LABEL_TARGET_POPULATION)
    login.assert_text(MESSAGE_TITLE, MESSAGE_DETAILS)
    login.assert_text(MESSAGE_BODY, MESSAGE_DETAILS)
    login.assert_text("Recipients", TABLE_TITLE)
    assert_texts(login, RECIPIENT_COLUMNS)
    login.assert_text("No results", TABLE_ROW)
    login.assert_text("Try adjusting your search or your filters to find what you are looking for.", TABLE_ROW)
    assert_single_page(login, "0–0 of 0")
