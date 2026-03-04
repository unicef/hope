from pathlib import Path

from drf_api_checker.pytest import frozenfixture
import pytest
from unit.api_contract._helpers import HopeRecorder

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, CountryFactory
from extras.test_utils.factories.payment import DeliveryMechanismFactory, FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.steficon import RuleFactory

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------


@frozenfixture()
def superuser(request, db):
    return UserFactory(is_staff=True, is_superuser=True)


@frozenfixture()
def program(request, db):
    return ProgramFactory()


@frozenfixture()
def api_token(request, db, superuser, program):
    from hope.models import APIToken
    from hope.models.utils import Grant

    token = APIToken.objects.create(
        user=superuser,
        grants=[Grant.API_READ_ONLY.name],
    )
    token.valid_for.add(program.business_area)
    return token


# ---------------------------------------------------------------------------
# Model fixtures
# ---------------------------------------------------------------------------


@frozenfixture()
def country(request, db):
    return CountryFactory()


@frozenfixture()
def area(request, db):
    return AreaFactory()


@frozenfixture()
def financial_institution(request, db):
    return FinancialInstitutionFactory()


@frozenfixture()
def rule(request, db):
    return RuleFactory()


@frozenfixture()
def delivery_mechanism(request, db):
    return DeliveryMechanismFactory()


# ---------------------------------------------------------------------------
# HOPEAuthentication endpoints (need api_token)
# ---------------------------------------------------------------------------


def test_constance(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/constance/")


def test_lookups_document(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/document/")


def test_lookups_country(superuser, api_token, country):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/country/")


def test_lookups_financial_institution(superuser, api_token, financial_institution):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/financial-institution/")


def test_lookups_residencestatus(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/residencestatus/")


def test_lookups_maritalstatus(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/maritalstatus/")


def test_lookups_observeddisability(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/observeddisability/")


def test_lookups_relationship(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/relationship/")


def test_lookups_role(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/role/")


def test_lookups_sex(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/sex/")


def test_lookups_program_statuses(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/program-statuses/")


# ---------------------------------------------------------------------------
# Default DRF auth (AllowAny, no token needed)
# ---------------------------------------------------------------------------


def test_areas(superuser, area):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/areas/")


def test_areatypes(superuser, area):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/areatypes/")


def test_engine_rules(superuser, rule):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/engine-rules/", data={"type": "TARGETING"})


# ---------------------------------------------------------------------------
# Choices endpoints (DRF default AllowAny, ChoicesViewSet)
# ---------------------------------------------------------------------------


def test_choices_currencies(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/currencies/")


def test_choices_payment_plan_status(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-plan-status/")


def test_choices_payment_plan_bg_action_status(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-plan-background-action-status/")


def test_choices_payment_verification_plan_status(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-verification-plan-status/")


def test_choices_payment_verification_status(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-verification-status/")


def test_choices_payment_verification_summary_status(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-verification-summary-status/")


def test_choices_payment_verification_plan_sampling(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-verification-plan-sampling/")


def test_choices_payment_record_delivery_type(superuser, delivery_mechanism):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/payment-record-delivery-type/")


def test_choices_feedback_issue_type(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/feedback-issue-type/")


def test_choices_languages(superuser):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/languages/")


def test_choices_countries(superuser, country):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser)
    recorder.assertGET("/api/rest/choices/countries/")
