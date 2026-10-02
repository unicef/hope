from django.contrib.admin.helpers import AdminReadonlyField
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
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
    with django_assert_num_queries(4):
        ba.save()

    ba.refresh_from_db()
    assert ba.ingest_source == BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY


def test_business_area_save_does_not_run_full_field_validation():
    ba = BusinessAreaFactory()
    # bypass save() — it is the code under test
    BusinessArea.objects.filter(pk=ba.pk).update(deduplication_duplicate_score=-1.0)
    ba.refresh_from_db()

    ba.name = "Renamed BA"
    ba.save()

    ba.refresh_from_db()
    assert ba.name == "Renamed BA"


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


@pytest.fixture
def business_area_editor():
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(content_type__app_label="core", codename="change_businessarea"))
    return user


@pytest.mark.parametrize(
    ("ingest_source", "expected_readonly_thresholds"),
    [
        (BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, set()),
        (
            BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY,
            {
                "deduplication_batch_duplicates_percentage",
                "deduplication_batch_duplicates_allowed",
                "deduplication_golden_record_duplicates_percentage",
                "deduplication_golden_record_duplicates_allowed",
            },
        ),
    ],
)
def test_business_area_admin_deduplication_thresholds_readonly_state(
    ingest_source, expected_readonly_thresholds, business_area_editor, django_assert_num_queries
):
    ba = BusinessAreaFactory(ingest_source=ingest_source)
    admin = BusinessAreaAdmin(model=BusinessArea, admin_site=AdminSite())
    request = RequestFactory().get("/")
    request.user = business_area_editor

    with django_assert_num_queries(0):
        readonly = admin.get_readonly_fields(request, ba)

    assert (
        set(readonly)
        & {
            "deduplication_batch_duplicates_percentage",
            "deduplication_batch_duplicates_allowed",
            "deduplication_golden_record_duplicates_percentage",
            "deduplication_golden_record_duplicates_allowed",
        }
        == expected_readonly_thresholds
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "deduplication_batch_duplicates_percentage",
        "deduplication_batch_duplicates_allowed",
        "deduplication_golden_record_duplicates_percentage",
        "deduplication_golden_record_duplicates_allowed",
    ],
)
def test_business_area_admin_deduplication_threshold_help_text_for_country_workspace_only(
    field_name, business_area_editor, django_assert_num_queries
):
    ba = BusinessAreaFactory(ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY)
    admin = BusinessAreaAdmin(model=BusinessArea, admin_site=AdminSite())
    request = RequestFactory().get("/")
    request.user = business_area_editor

    with django_assert_num_queries(4):
        form_class = admin.get_form(request, ba, change=True)

    form = form_class(instance=ba)
    readonly_field = AdminReadonlyField(form, field_name, is_first=False, model_admin=admin)

    assert readonly_field.field["help_text"] == (
        "Not supported for Country Workspace only business areas - biographic duplicate thresholds "
        "are not evaluated in this flow."
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "deduplication_batch_duplicates_percentage",
        "deduplication_batch_duplicates_allowed",
        "deduplication_golden_record_duplicates_percentage",
        "deduplication_golden_record_duplicates_allowed",
    ],
)
def test_business_area_admin_deduplication_threshold_help_text_for_legacy_ingest_source(
    field_name, business_area_editor, django_assert_num_queries
):
    ba = BusinessAreaFactory(ingest_source=BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE)
    admin = BusinessAreaAdmin(model=BusinessArea, admin_site=AdminSite())
    request = RequestFactory().get("/")
    request.user = business_area_editor

    with django_assert_num_queries(4):
        form = admin.get_form(request, ba, change=True)

    assert form.base_fields[field_name].help_text == BusinessArea._meta.get_field(field_name).help_text
