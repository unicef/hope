from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from hope.admin.business_area import BusinessAreaAdmin
from hope.models import BusinessArea

pytestmark = pytest.mark.django_db


def test_business_area_ingest_source_reverse_transition_rejected():
    # reverse is changing from COUNTRY_WORKSPACE_ONLY to ALL_EXCEPT_COUNTRY_WORKSPACE
    ba = BusinessAreaFactory(ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)

    ba.ingest_source = BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE
    with pytest.raises(ValidationError) as exc_info:
        ba.save()

    assert exc_info.value.message_dict == {
        "ingest_source": ["Cannot go back to legacy ingest sources when CW source was chosen."]
    }


def test_business_area_ingest_source_clean_skips_when_unsaved(django_assert_num_queries):
    ba = BusinessArea(name="Fresh BA", ingest_source=BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)

    with django_assert_num_queries(1):
        ba.clean()


def test_business_area_ingest_source_forward_transition_allowed(django_assert_num_queries):
    ba = BusinessAreaFactory()

    ba.ingest_source = BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    with django_assert_num_queries(6):
        ba.save()

    ba.refresh_from_db()
    assert ba.ingest_source == BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY


@pytest.mark.parametrize(
    ("ingest_source", "expected_readonly"),
    [
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, False),
        (BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, True),
    ],
)
def test_business_area_admin_ingest_source_readonly_state(ingest_source, expected_readonly, django_assert_num_queries):
    ba = BusinessAreaFactory(ingest_source=ingest_source)
    admin = BusinessAreaAdmin(model=BusinessArea, admin_site=AdminSite())
    request = RequestFactory().get("/")
    request.user = UserFactory(is_superuser=True, is_staff=True)

    with django_assert_num_queries(0):
        readonly = admin.get_readonly_fields(request, ba)

    assert ("ingest_source" in readonly) is expected_readonly
