import pytest

from e2e.new_selenium.accountability.conftest import (
    PROGRAM_NAME,
    RECIPIENT_COLUMNS,
    assert_single_page,
    assert_texts,
    open_accountability_page,
)
from extras.test_utils.factories import SurveyFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Household, PaymentList, Program, Survey, User

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TABLE_TITLE = 'h6[data-cy="table-title"]'
ROWS = 'tr[role="checkbox"]'
BUTTON_NEW_SURVEY = 'button[data-cy="button-new-survey"]'
FILTERS = {
    'div[data-cy="filters-search"]': "Search",
    'div[data-cy="filters-target-population-autocomplete"]': "Target Population",
    'div[data-cy="Target Population-input"]': "Target Population",
    'div[data-cy="filters-created-by-autocomplete"]': "Created by",
    'div[data-cy="Created by-input"]': "Created by",
    'div[data-cy="filters-creation-date-from"]': "From",
    'div[data-cy="filters-creation-date-to"]': "To",
    'button[data-cy="button-filters-clear"]': "CLEAR",
    'button[data-cy="button-filters-apply"]': "APPLY",
}
LABEL_CATEGORY = 'div[data-cy="label-Category"]'
LABEL_SURVEY_TITLE = 'div[data-cy="label-Survey Title"]'
LABEL_CREATED_BY = 'div[data-cy="label-Created By"]'
LABEL_DATE_CREATED = 'div[data-cy="label-Date Created"]'
LABEL_PROGRAMME = 'div[data-cy="label-Programme"]'
LIST_COLUMNS = {
    "thead th:nth-child(1)": "Survey ID",
    "thead th:nth-child(2)": "Survey Title",
    "thead th:nth-child(3)": "Category",
    "thead th:nth-child(4)": "Number of Recipients",
    "thead th:nth-child(5)": "Created by",
    "thead th:nth-child(6)": "Creation Date",
}

SURVEY_TITLE = "Test survey"


@pytest.fixture
def survey(program: Program, target_population: PaymentList, author: User, household: Household) -> Survey:
    survey = SurveyFactory(
        title=SURVEY_TITLE,
        category=Survey.CATEGORY_MANUAL,
        business_area=program.business_area,
        program=program,
        payment_list=target_population,
        created_by=author,
        number_of_recipients=1,
    )
    survey.recipients.add(household)
    return survey


def test_surveys_list_shows_survey(survey: Survey, program: Program, login: HopeTestBrowser) -> None:
    open_accountability_page(login, program, "Surveys")

    login.assert_text("NEW SURVEY", BUTTON_NEW_SURVEY)
    assert_texts(login, FILTERS)
    login.assert_text("Surveys List", TABLE_TITLE)
    assert_single_page(login, "1–1 of 1")
    login.assert_text(survey.unicef_id, ROWS)
    login.assert_text(SURVEY_TITLE, ROWS)
    login.assert_text("Alice Author", ROWS)
    assert_texts(login, LIST_COLUMNS)
    assert len(login.find_elements(ROWS)) == 1


def test_survey_details_shows_survey_and_recipient(
    survey: Survey, household: Household, program: Program, login: HopeTestBrowser
) -> None:
    open_accountability_page(login, program, "Surveys")

    login.click(ROWS)

    login.assert_text(survey.unicef_id, PAGE_HEADER_TITLE)
    login.assert_text("Survey with manual process", LABEL_CATEGORY)
    login.assert_text(SURVEY_TITLE, LABEL_SURVEY_TITLE)
    login.assert_text("Alice Author", LABEL_CREATED_BY)
    login.assert_text(survey.created_at.strftime("%-d %b %Y"), LABEL_DATE_CREATED)
    login.assert_text(PROGRAM_NAME, LABEL_PROGRAMME)
    assert_texts(login, RECIPIENT_COLUMNS)
    assert_single_page(login, "1–1 of 1")
    login.assert_text(household.unicef_id, ROWS)
    assert len(login.find_elements(ROWS)) == 1
