import pytest
from pathlib import Path

from drf_api_checker.pytest import frozenfixture

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from unit.api_contract._helpers import HopeRecorder

pytestmark = pytest.mark.django_db

DATA_DIR = Path(__file__).parent / "_api_checker" / Path(__file__).stem


@pytest.fixture()
def superuser(db):
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture()
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture()
def api_token(db, superuser, business_area):
    from hope.models import APIToken
    from hope.models.utils import Grant

    token = APIToken.objects.create(
        user=superuser,
        grants=[Grant.API_READ_ONLY.name],
    )
    token.valid_for.add(business_area)
    return token


@frozenfixture()
def country(request, db):
    return CountryFactory()


@frozenfixture()
def area_type(request, db, country):
    return AreaTypeFactory(country=country)


@frozenfixture()
def area(request, db, area_type):
    return AreaFactory(area_type=area_type)


@frozenfixture()
def document_type(request, db):
    return DocumentTypeFactory()


def test_list_areas__returns_expected_fields(superuser, api_token, area):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/areas/")


def test_list_areatypes__returns_expected_fields(superuser, api_token, area_type):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/areatypes/")


def test_list_constance__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/constance/", allow_empty=True)


def test_list_lookups_document__returns_expected_fields(superuser, api_token, document_type):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/document/")


def test_list_lookups_country__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/country/", allow_empty=True)


def test_list_lookups_financial_institution__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/financial-institution/", allow_empty=True)


def test_list_lookups_residencestatus__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/residencestatus/", allow_empty=True)


def test_list_lookups_maritalstatus__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/maritalstatus/", allow_empty=True)


def test_list_lookups_observeddisability__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/observeddisability/", allow_empty=True)


def test_list_lookups_relationship__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/relationship/", allow_empty=True)


def test_list_lookups_role__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/role/", allow_empty=True)


def test_list_lookups_sex__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/sex/", allow_empty=True)


def test_list_lookups_program_statuses__returns_expected_fields(superuser, api_token):
    recorder = HopeRecorder(DATA_DIR, as_user=superuser, api_token=api_token)
    recorder.assertGET("/api/rest/lookups/program-statuses/", allow_empty=True)
