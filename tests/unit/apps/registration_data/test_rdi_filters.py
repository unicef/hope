import pytest

from extras.test_utils.factories import RegistrationDataImportFactory
from hope.apps.registration_data.filters import RegistrationDataImportFilter
from hope.models import RegistrationDataImport

pytestmark = pytest.mark.django_db


def _filtered_qs(data):
    """Apply RegistrationDataImportFilter to the full RDI queryset."""
    return RegistrationDataImportFilter(data=data, queryset=RegistrationDataImport.objects.all()).qs


def test_rdi_search_matches_middle_of_title(rdi_syria_import, rdi_afghanistan_import, django_assert_num_queries):
    with django_assert_num_queries(1):
        result = list(_filtered_qs({"search": "Syria"}))
    assert result == [rdi_syria_import]


def test_rdi_search_is_case_insensitive(rdi_syria_import, rdi_afghanistan_import, rdi_syria_lowercase):
    result = set(_filtered_qs({"search": "syria"}))
    assert result == {rdi_syria_import, rdi_syria_lowercase}


def test_rdi_search_returns_empty_for_no_match(rdi_syria_import, rdi_afghanistan_import):
    result = list(_filtered_qs({"search": "xyz"}))
    assert result == []


def test_rdi_name_startswith_meta_lookup_still_exposed(rdi_syria_import):
    qs = RegistrationDataImportFilter(
        data={"name__startswith": "June"},
        queryset=RegistrationDataImport.objects.all(),
    ).qs
    assert rdi_syria_import in qs


def test_rdi_name_exact_meta_lookup_removed():
    f = RegistrationDataImportFilter()
    assert "name__exact" not in f.form.fields


def test_rdi_search_excludes_soft_deleted(rdi_syria_import):
    excluded_rdi = RegistrationDataImportFactory(name="Syria excluded", excluded=True)
    result = list(_filtered_qs({"search": "Syria"}))
    assert rdi_syria_import in result
    assert excluded_rdi not in result
