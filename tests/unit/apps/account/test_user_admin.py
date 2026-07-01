import csv
import io
from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.admin.sites import site
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, HttpResponseRedirect
from django.test import RequestFactory
import pytest
from requests import HTTPError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.admin.user import CsvImportConfig, LoadUsersForm, UserAdmin
from hope.models import BusinessArea, IncompatibleRoles, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db

GRAPH_PATH = "hope.admin.user.MicrosoftGraphAPI"
SYNC_PATH = "hope.admin.user.Synchronizer"
AZURE_ID = "11111111-1111-1111-1111-111111111111"
AZURE_ID_NEW = "22222222-2222-2222-2222-222222222222"


def _request(method: str = "get", path: str = "/", data: Any = None, user: Any = None) -> Any:
    request = getattr(RequestFactory(), method)(path, data=data)
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    request.user = user or UserFactory(is_superuser=True, is_staff=True)
    return request


@pytest.fixture
def admin() -> UserAdmin:
    return site._registry[User]


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", code="0060", name="Afghanistan")


@pytest.fixture
def role() -> Role:
    return RoleFactory(name="Some Role")


# LoadUsersForm
def test_clean_emails_accepts_space_separated_valid_addresses() -> None:
    form = LoadUsersForm(data={"emails": "one@example.com two@example.com"})

    form.is_valid()

    assert "emails" not in form.errors


def test_clean_emails_rejects_invalid_addresses() -> None:
    form = LoadUsersForm(data={"emails": "good@example.com not-an-email"})

    form.is_valid()

    assert "emails" in form.errors
    assert "not-an-email" in form.errors["emails"][0]


# ADUSerMixin
def test_get_ad_form_returns_unbound_form_on_get(admin: UserAdmin) -> None:
    form = admin._get_ad_form(_request("get"))

    assert isinstance(form, LoadUsersForm)
    assert not form.is_bound


def test_get_ad_form_returns_bound_form_on_post(admin: UserAdmin) -> None:
    form = admin._get_ad_form(_request("post", data={"emails": "a@example.com"}))

    assert form.is_bound


def test_sync_ad_data_updates_user_fields_from_graph(admin: UserAdmin) -> None:
    user = UserFactory(azure_id=AZURE_ID, email="old@example.com", first_name="Old")

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.return_value = {
            "mail": "new@example.com",
            "givenName": "New",
            "surname": "Name",
            "id": AZURE_ID_NEW,
        }
        admin._sync_ad_data(user)

    user.refresh_from_db()
    assert user.email == "new@example.com"
    assert user.first_name == "New"
    assert str(user.azure_id) == AZURE_ID_NEW


def test_sync_ad_data_raises_http404_when_user_missing_everywhere(admin: UserAdmin) -> None:
    user = UserFactory()

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.side_effect = Http404

        with pytest.raises(Http404):
            admin._sync_ad_data(user)


def test_create_user_from_ad_data_normalises_missing_names_and_sets_job_title(admin: UserAdmin) -> None:
    partner = PartnerFactory(name="ACME")
    ms_graph = MagicMock()
    ms_graph.get_user_data.return_value = {
        "mail": "person@example.com",
        "givenName": None,
        "surname": None,
        "id": AZURE_ID,
        "jobTitle": "Engineer",
    }

    user = admin._create_user_from_ad_data(ms_graph, "person@example.com", partner)

    assert not User.objects.filter(email="person@example.com").exists()
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.job_title == "Engineer"
    assert user.partner == partner
    assert not user.has_usable_password()


def test_create_user_from_ad_data_keeps_names_and_skips_absent_job_title(admin: UserAdmin) -> None:
    partner = PartnerFactory(name="ACME")
    ms_graph = MagicMock()
    ms_graph.get_user_data.return_value = {
        "mail": "person@example.com",
        "givenName": "Jane",
        "surname": "Doe",
        "id": AZURE_ID,
    }

    user = admin._create_user_from_ad_data(ms_graph, "person@example.com", partner)

    assert user.first_name == "Jane"
    assert user.last_name == "Doe"
    assert user.job_title == ""


def test_sync_multi_reports_success_when_all_users_found(admin: UserAdmin) -> None:
    request = _request(user=UserFactory(is_superuser=True, is_staff=True, azure_id=AZURE_ID))

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.return_value = {
            "mail": "synced@example.com",
            "givenName": "Synced",
            "surname": "User",
            "id": AZURE_ID,
        }
        admin.sync_multi.func(admin, request)

    assert any("successfully fetched" in str(m) for m in get_messages(request))


def test_sync_multi_reports_users_that_were_not_found(admin: UserAdmin) -> None:
    request = _request(user=UserFactory(is_superuser=True, is_staff=True, azure_id=None))

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.side_effect = Http404
        admin.sync_multi.func(admin, request)

    assert any("were not found" in str(m) for m in get_messages(request))


def test_sync_multi_reports_error_on_http_error(admin: UserAdmin) -> None:
    request = _request(user=UserFactory(is_superuser=True, is_staff=True, azure_id=AZURE_ID))

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.side_effect = HTTPError("boom")
        admin.sync_multi.func(admin, request)

    assert any("boom" in str(m) for m in get_messages(request))


def test_sync_single_reports_success(admin: UserAdmin) -> None:
    user = UserFactory(azure_id=AZURE_ID)
    request = _request()

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.return_value = {
            "mail": "synced@example.com",
            "givenName": "Synced",
            "surname": "User",
            "id": AZURE_ID,
        }
        admin.sync_single.func(admin, request, user.pk)

    assert any("successfully fetched" in str(m) for m in get_messages(request))


def test_sync_single_reports_error(admin: UserAdmin) -> None:
    user = UserFactory(azure_id=AZURE_ID)
    request = _request()

    with patch(GRAPH_PATH) as graph:
        graph.return_value.get_user_data.side_effect = HTTPError("nope")
        admin.sync_single.func(admin, request, user.pk)

    assert any("nope" in str(m) for m in get_messages(request))


# UserAdmin
def test_ad_button_renders_synchronizer_context(admin: UserAdmin) -> None:
    user = UserFactory(username="ad-user")
    request = _request()

    with patch(SYNC_PATH) as synchronizer:
        synchronizer.return_value.get_user.return_value = {"displayName": "AD User"}
        response = admin.ad.func(admin, request, user.pk)

    assert response.context_data["ctx"] == {"displayName": "AD User"}


def test_get_readonly_fields_locks_all_fields_without_restrict_perm(admin: UserAdmin) -> None:
    request = _request(user=UserFactory(is_staff=True))
    all_fields = ["username", "email", "partner"]

    with patch.object(UserAdmin, "get_fields", return_value=all_fields):
        readonly_fields = admin.get_readonly_fields(request, None)

    assert readonly_fields == all_fields


def test_get_readonly_fields_delegates_to_super_with_restrict_perm(admin: UserAdmin) -> None:
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="restrict_help_desk"))
    request = _request(user=User.objects.get(pk=user.pk))

    readonly_fields = admin.get_readonly_fields(request, None)

    assert set(readonly_fields) != set(admin.get_fields(request, None))


def test_get_deleted_objects_appends_kobo_entry(admin: UserAdmin) -> None:
    user = UserFactory(custom_fields={"kobo_pk": 7, "kobo_username": "kobo-bob"})
    request = _request()

    to_delete, _model_count, _perms, _protected = admin.get_deleted_objects([user], request)

    assert "Kobo: kobo-bob" in to_delete


def test_get_deleted_objects_without_kobo_pk_adds_nothing(admin: UserAdmin) -> None:
    user = UserFactory(custom_fields={})
    request = _request()

    to_delete, _model_count, _perms, _protected = admin.get_deleted_objects([user], request)

    assert not any(str(entry).startswith("Kobo:") for entry in to_delete)


def test_get_actions_keeps_business_area_role_for_privileged_user(admin: UserAdmin) -> None:
    request = _request()

    assert "add_business_area_role" in admin.get_actions(request)


def test_get_actions_removes_business_area_role_without_perm(admin: UserAdmin) -> None:
    request = _request(user=UserFactory(is_staff=True))

    assert "add_business_area_role" not in admin.get_actions(request)


@pytest.mark.parametrize(
    ("added", "removed", "users", "expected"),
    [
        (0, 2, 3, "2 roles removed from 3 users"),
        (2, 0, 3, "2 roles granted to 3 users"),
        (0, 0, 3, "3 users processed no actions have been required"),
    ],
)
def test_get_msg_formats_summary(admin: UserAdmin, added: int, removed: int, users: int, expected: str) -> None:
    assert admin._get_msg(added, removed, users) == expected


def test_add_business_area_role_adds_role_to_users(admin: UserAdmin, afghanistan: BusinessArea, role: Role) -> None:
    target = UserFactory()
    request = _request(
        "post",
        path="/api/unicorn/account/user/",
        data={
            "apply": "1",
            "operation": "ADD",
            "business_area": afghanistan.pk,
            "roles": [role.pk],
        },
    )

    response = admin.add_business_area_role(request, User.objects.filter(pk=target.pk))

    assert isinstance(response, HttpResponseRedirect)
    assert RoleAssignment.objects.filter(user=target, business_area=afghanistan, role=role).exists()
    assert any("1 roles granted to 1 users" in str(m) for m in get_messages(request))


def test_add_business_area_role_removes_role_from_users(
    admin: UserAdmin, afghanistan: BusinessArea, role: Role
) -> None:
    target = UserFactory()
    RoleAssignmentFactory(user=target, partner=None, role=role, business_area=afghanistan)
    request = _request(
        "post",
        path="/api/unicorn/account/user/",
        data={
            "apply": "1",
            "operation": "REMOVE",
            "business_area": afghanistan.pk,
            "roles": [role.pk],
        },
    )

    admin.add_business_area_role(request, User.objects.filter(pk=target.pk))

    assert not RoleAssignment.objects.filter(user=target, business_area=afghanistan, role=role).exists()
    assert any("1 roles removed from 1 users" in str(m) for m in get_messages(request))


def test_get_user_uses_username_from_row_when_present(admin: UserAdmin) -> None:
    partner = PartnerFactory(name="Importer")

    is_new, user = admin._get_user(
        "imported@example.com", partner, {"email": "imported@example.com", "username": "custom_name"}
    )

    assert is_new is True
    assert user.username == "custom_name"


def test_get_user_derives_username_from_email_when_missing(admin: UserAdmin) -> None:
    partner = PartnerFactory(name="Importer")

    is_new, user = admin._get_user("Imported.User@example.com", partner, {"email": "Imported.User@example.com"})

    assert is_new is True
    assert user.username == "imported_user_example_com"


def test_import_csv_get_renders_form(admin: UserAdmin) -> None:
    response = admin.import_csv.func(admin, _request("get"))

    assert "form" in response.context_data
    assert response.context_data["processed"] is False


def test_import_csv_post_imports_user_from_csv(admin: UserAdmin, afghanistan: BusinessArea, role: Role) -> None:
    partner = PartnerFactory(name="Importer")
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["email", "username"])
    writer.writerow(["fresh@example.com", "fresh_user"])
    upload = SimpleUploadedFile("users.csv", buffer.getvalue().encode("utf-8-sig"), content_type="text/csv")

    request = _request("post")
    request.FILES["file"] = upload
    request.POST = request.POST.copy()
    request.POST.update(
        {
            "file": upload,
            "delimiter": ",",
            "quotechar": '"',
            "quoting": str(csv.QUOTE_MINIMAL),
            "escapechar": "",
            "partner": str(partner.pk),
            "business_area": str(afghanistan.pk),
            "role": str(role.pk),
        }
    )

    response = admin.import_csv.func(admin, request)

    assert response.context_data["processed"] is True
    created = User.objects.get(email="fresh@example.com")
    assert created.role_assignments.filter(business_area=afghanistan, role=role).exists()


def test_add_business_area_role_get_renders_selection_form(admin: UserAdmin, role: Role) -> None:
    target = UserFactory()
    request = _request("get", path="/api/unicorn/account/user/")

    response = admin.add_business_area_role(request, User.objects.filter(pk=target.pk))

    assert response.status_code == 200


def test_process_csv_row_adds_role_to_existing_user(admin: UserAdmin, afghanistan: BusinessArea, role: Role) -> None:
    partner = PartnerFactory(name="Importer")
    existing = UserFactory(email="existing@example.com", partner=partner)
    config = CsvImportConfig(partner=partner, business_area=afghanistan, role=role)
    request = _request("post")

    user_info = admin._process_csv_row(request, {"email": "existing@example.com"}, config)

    assert user_info["is_new"] is False
    assert existing.role_assignments.filter(business_area=afghanistan, role=role).exists()


def test_process_csv_row_reports_incompatible_role_for_existing_user(
    admin: UserAdmin, afghanistan: BusinessArea, role: Role
) -> None:
    partner = PartnerFactory(name="Importer")
    other_role = RoleFactory(name="Conflicting Role")
    IncompatibleRoles.objects.create(role_one=role, role_two=other_role)
    existing = UserFactory(email="existing@example.com", partner=partner)
    RoleAssignmentFactory(user=existing, partner=None, role=other_role, business_area=afghanistan)
    config = CsvImportConfig(partner=partner, business_area=afghanistan, role=role)
    request = _request("post")

    admin._process_csv_row(request, {"email": "existing@example.com"}, config)

    assert any("incompatible" in str(m) for m in get_messages(request))


def test_process_csv_row_raises_when_email_column_missing(
    admin: UserAdmin, afghanistan: BusinessArea, role: Role
) -> None:
    partner = PartnerFactory(name="Importer")
    config = CsvImportConfig(partner=partner, business_area=afghanistan, role=role)
    request = _request("post")

    with pytest.raises(Exception, match="KeyError"):
        admin._process_csv_row(request, {"not_email": "x"}, config)


def test_import_csv_post_with_invalid_form_reports_errors(admin: UserAdmin) -> None:
    request = _request("post")
    request.POST = request.POST.copy()
    request.POST.update({"delimiter": ",", "quotechar": '"', "quoting": str(csv.QUOTE_MINIMAL)})

    response = admin.import_csv.func(admin, request)

    assert response.context_data["processed"] is False
    assert any("correct errors" in str(m) for m in get_messages(request))


def test_formfield_for_foreignkey_partner_excludes_parent_partners(admin: UserAdmin) -> None:
    parent = PartnerFactory(name="Parent")
    child = PartnerFactory(name="Child", parent=parent)
    standalone = PartnerFactory(name="Standalone")
    request = _request()

    field = admin.formfield_for_foreignkey(User._meta.get_field("partner"), request)

    assert parent not in field.queryset
    assert child in field.queryset
    assert standalone in field.queryset
