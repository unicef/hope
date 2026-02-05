from django.core.exceptions import PermissionDenied
from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, SurveyFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.accountability.views import download_cash_plan_payment_verification
from hope.models import Survey
from hope.models.survey import SampleFileExpiredError

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def survey(business_area):
    return SurveyFactory(business_area=business_area)


def test_download_survey_sample_returns_403_when_user_has_no_permission(rf, survey, user):
    request = rf.get(reverse("download-survey-sample", args=[survey.id]))
    request.user = user

    with pytest.raises(PermissionDenied) as excinfo:
        download_cash_plan_payment_verification(request, str(survey.id))

    assert excinfo.value.args[0]["required_permissions"] == [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS.name]


def test_download_survey_sample_redirects_to_file_url_when_user_has_permission(
    rf, monkeypatch, survey, user, business_area, create_user_role_with_permissions
):
    create_user_role_with_permissions(user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], business_area)
    monkeypatch.setattr(Survey, "sample_file_path", lambda self: "http://example.com/file.xlsx")

    request = rf.get(reverse("download-survey-sample", args=[survey.id]))
    request.user = user

    response = download_cash_plan_payment_verification(request, str(survey.id))

    assert response.status_code == 302
    assert response.url == "http://example.com/file.xlsx"


def test_download_survey_sample_returns_400_when_file_expired(
    rf, monkeypatch, survey, user, business_area, create_user_role_with_permissions
):
    create_user_role_with_permissions(user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], business_area)

    def raise_expired(self):
        raise SampleFileExpiredError()

    monkeypatch.setattr(Survey, "sample_file_path", raise_expired)

    request = rf.get(reverse("download-survey-sample", args=[survey.id]))
    request.user = user

    response = download_cash_plan_payment_verification(request, str(survey.id))

    assert response.status_code == 400
    assert "expired" in response.content.decode().lower()
