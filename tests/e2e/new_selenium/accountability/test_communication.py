import pytest

from e2e.new_selenium.accountability.conftest import TARGET_POPULATION_NAME, open_accountability_page
from extras.test_utils.factories import CommunicationMessageFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Message, PaymentPlan, Program, User

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_TITLE = 'h6[data-cy="table-title"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
ROWS = 'tr[role="checkbox"]'
BUTTON_NEW_MESSAGE = 'a[data-cy="button-communication-create-new"]'
FILTERS = (
    'div[data-cy="filters-target-population-autocomplete"]',
    'div[data-cy="filters-created-by-autocomplete"]',
    'div[data-cy="filters-creation-date-from"]',
    'div[data-cy="filters-creation-date-to"]',
    'button[data-cy="button-filters-clear"]',
    'button[data-cy="button-filters-apply"]',
)
LABEL_CREATED_BY = 'div[data-cy="label-Created By"]'
LABEL_DATE_CREATED = 'div[data-cy="label-Date Created"]'
LABEL_TARGET_POPULATION = 'div[data-cy="label-Target Population"]'
MESSAGE_DETAILS = 'div[data-cy="communication-message-details"]'
RECIPIENT_COLUMNS = (
    'th[data-cy="household-id"]',
    'th[data-cy="status"]',
    'th[data-cy="household-head-name"]',
    'th[data-cy="household-size"]',
    'th[data-cy="household-location"]',
    'th[data-cy="household-residence-status"]',
    'th[data-cy="household-registration-date"]',
)
TABLE_ROW = 'tr[data-cy="table-row"]'

MESSAGE_TITLE = "You got credit of USD 100"
MESSAGE_BODY = "Greetings, we have sent you USD 100 in your registered account on 2022-09-19 20:00:00 UTC"


@pytest.fixture
def message(program: Program, target_population: PaymentPlan, author: User) -> Message:
    return CommunicationMessageFactory(
        title=MESSAGE_TITLE,
        body=MESSAGE_BODY,
        business_area=program.business_area,
        program=program,
        payment_plan=target_population,
        created_by=author,
    )


def test_communication_list_shows_message(message: Message, program: Program, login: HopeTestBrowser) -> None:
    open_accountability_page(login, program, "Communication")

    login.assert_elements_visible(BUTTON_NEW_MESSAGE, *FILTERS)
    login.assert_text("Messages List", TABLE_TITLE)
    login.assert_text("1–1 of 1", TABLE_PAGINATION)
    login.assert_text(message.unicef_id, ROWS)
    login.assert_text(MESSAGE_TITLE, ROWS)
    login.assert_text("Alice Author", ROWS)


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
    login.assert_elements_visible(*RECIPIENT_COLUMNS)
    login.assert_text("No results", TABLE_ROW)
    login.assert_text("0–0 of 0", TABLE_PAGINATION)
