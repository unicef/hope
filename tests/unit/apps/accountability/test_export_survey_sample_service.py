from django.conf import settings
from django.test import override_settings
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    HouseholdFactory,
    SurveyFactory,
    UserFactory,
)
from hope.apps.accountability.services.export_survey_sample_service import ExportSurveySampleService
from hope.apps.household import const
from hope.models import Household, Survey, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="Jane", last_name="Doe", email="jane@example.com")


@pytest.fixture
def survey(user: User) -> Survey:
    return SurveyFactory(created_by=user)


@pytest.fixture
def recipient_household(survey: Survey) -> Household:
    household = HouseholdFactory(
        business_area=survey.business_area,
        size=5,
        residence_status=const.HOST,
        admin2=AreaFactory(name="Admin Two"),
    )
    survey.recipients.set([household])
    return household


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=True)
def test_get_email_context_uses_https_link(survey: Survey, user: User) -> None:
    service = ExportSurveySampleService(survey, user)

    context = service.get_email_context()

    expected_link = f"https://{settings.FRONTEND_HOST}{reverse('download-survey-sample', args=[str(survey.id)])}"
    assert context["link"] == expected_link
    assert context["first_name"] == "Jane"
    assert context["last_name"] == "Doe"
    assert context["email"] == "jane@example.com"
    assert context["title"] == "Survey sample XLSX file generated"


@override_settings(SOCIAL_AUTH_REDIRECT_IS_HTTPS=False)
def test_get_email_context_uses_http_link(survey: Survey, user: User) -> None:
    service = ExportSurveySampleService(survey, user)

    context = service.get_email_context()

    assert context["link"].startswith(f"http://{settings.FRONTEND_HOST}")


def test_generate_file_writes_headers(survey: Survey, user: User) -> None:
    service = ExportSurveySampleService(survey, user)

    workbook = service._generate_file()
    sheet = workbook[ExportSurveySampleService.WORKBOOK_TITLE]
    header_count = len(ExportSurveySampleService.HEADERS)

    assert [cell.value for cell in sheet[1]][:header_count] == list(ExportSurveySampleService.HEADERS)


def test_generate_file_writes_recipient_row(survey: Survey, user: User, recipient_household: Household) -> None:
    service = ExportSurveySampleService(survey, user)

    workbook = service._generate_file()
    sheet = workbook[ExportSurveySampleService.WORKBOOK_TITLE]
    header_count = len(ExportSurveySampleService.HEADERS)
    row = [cell.value for cell in sheet[2]][:header_count]

    assert row == [
        str(recipient_household.unicef_id),
        str(recipient_household.head_of_household.full_name),
        5,
        "Admin Two",
        const.HOST,
        str(recipient_household.last_registration_date),
    ]


def test_generate_file_renders_empty_admin2_when_missing(survey: Survey, user: User) -> None:
    household = HouseholdFactory(business_area=survey.business_area, size=2, admin2=None)
    survey.recipients.set([household])
    service = ExportSurveySampleService(survey, user)

    workbook = service._generate_file()
    sheet = workbook[ExportSurveySampleService.WORKBOOK_TITLE]
    row = [cell.value for cell in sheet[2]]

    assert row[3] == ""


def test_export_sample_stores_xlsx_file(survey: Survey, user: User, recipient_household: Household) -> None:
    service = ExportSurveySampleService(survey, user)

    service.export_sample()

    survey.refresh_from_db()
    assert survey.sample_file
    assert survey.sample_file_generated_at is not None
    assert survey.sample_file.name.startswith(f"survey_sample_{survey.unicef_id}")
    assert survey.sample_file.name.endswith(".xlsx")
