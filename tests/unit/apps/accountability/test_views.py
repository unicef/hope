from django.core.exceptions import PermissionDenied
from django.urls import reverse
import pytest

from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.accountability import SurveyFactory
from hope.apps.account.permissions import Permissions
from hope.apps.accountability.views import download_cash_plan_payment_verification
from hope.models import Survey
from hope.models.survey import SampleFileExpiredError

pytestmark = pytest.mark.django_db


class TestDownloadCashPlanPaymentVerification:
    def test_requires_permission(self, rf):
        business_area = BusinessAreaFactory()
        survey = SurveyFactory(business_area=business_area)
        user = UserFactory()

        request = rf.get(reverse("download-survey-sample", args=[survey.id]))
        request.user = user

        with pytest.raises(PermissionDenied) as excinfo:
            download_cash_plan_payment_verification(request, str(survey.id))

        assert excinfo.value.args[0]["required_permissions"] == [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS.name]

    def test_redirects_with_permission(self, rf, monkeypatch, create_user_role_with_permissions):
        business_area = BusinessAreaFactory()
        survey = SurveyFactory(business_area=business_area)
        user = UserFactory()
        create_user_role_with_permissions(user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], business_area)
        monkeypatch.setattr(Survey, "sample_file_path", lambda self: "http://example.com/file.xlsx")

        request = rf.get(reverse("download-survey-sample", args=[survey.id]))
        request.user = user

        response = download_cash_plan_payment_verification(request, str(survey.id))

        assert response.status_code == 302
        assert response.url == "http://example.com/file.xlsx"

    def test_handles_expired_file(self, rf, monkeypatch, create_user_role_with_permissions):
        business_area = BusinessAreaFactory()
        survey = SurveyFactory(business_area=business_area)
        user = UserFactory()
        create_user_role_with_permissions(user, [Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS], business_area)

        def raise_expired(self):
            raise SampleFileExpiredError()

        monkeypatch.setattr(Survey, "sample_file_path", raise_expired)

        request = rf.get(reverse("download-survey-sample", args=[survey.id]))
        request.user = user

        response = download_cash_plan_payment_verification(request, str(survey.id))

        assert response.status_code == 400
        assert "expired" in response.content.decode().lower()
