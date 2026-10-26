from collections.abc import Generator
from typing import Any
from urllib.parse import unquote

import pytest
import responses

from extras.test_utils.factories import ApprovalFactory, UserFactory
from hope.apps.account.actor_snapshot import ActorSnapshot, actor_display, build_actor_snapshot
from hope.models import Approval, User

pytestmark = pytest.mark.django_db

USERS_URL = "https://graph.microsoft.com/v1.0/users/"
USER_BY_ID_URL = "https://graph.microsoft.com/v1.0/users/11111111-2222-3333-4444-555555555555"


@pytest.fixture
def user() -> User:
    return UserFactory(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com", job_title="Stored Title"
    )


@pytest.fixture
def user_with_azure_id(user: User) -> User:
    user.azure_id = "11111111-2222-3333-4444-555555555555"
    user.save(update_fields=["azure_id"])
    return user


@pytest.fixture
def nameless_user() -> User:
    return UserFactory(first_name="", last_name="", email="nameless@example.com", job_title="Stored Title")


@pytest.fixture
def ad(settings: Any) -> Generator[responses.RequestsMock, None, None]:
    settings.AZURE_CLIENT_ID = "client-id"
    settings.AZURE_CLIENT_SECRET = "client-secret"
    with responses.RequestsMock() as graph:
        graph.add(responses.POST, settings.AZURE_TOKEN_URL, json={"access_token": "token"})
        yield graph


@pytest.fixture
def ad_without_credentials(settings: Any) -> None:
    settings.AZURE_CLIENT_ID = ""
    settings.AZURE_CLIENT_SECRET = ""


@pytest.fixture
def ad_token_failure(settings: Any) -> Generator[responses.RequestsMock, None, None]:
    settings.AZURE_CLIENT_ID = "client-id"
    settings.AZURE_CLIENT_SECRET = "client-secret"
    with responses.RequestsMock() as graph:
        graph.add(responses.POST, settings.AZURE_TOKEN_URL, body="fail", status=500)
        yield graph


@pytest.fixture
def snapshot_approval(user: User) -> Approval:
    return ApprovalFactory(
        created_by=user, created_by_name="Old Name", created_by_job_title="Old Title", created_by_job_title_source="AD"
    )


@pytest.fixture
def snapshot_approval_without_title(user: User) -> Approval:
    return ApprovalFactory(
        created_by=user, created_by_name="Old Name", created_by_job_title="", created_by_job_title_source="AD"
    )


@pytest.fixture
def legacy_approval(user: User) -> Approval:
    return ApprovalFactory(created_by=user)


@pytest.fixture
def legacy_approval_without_user() -> Approval:
    return ApprovalFactory(created_by=None)


def test_build_actor_snapshot_arrange_ad_title_act_build_assert_name_and_ad_title(
    user: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USERS_URL, json={"value": [{"jobTitle": "Programme Officer"}]})

    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Programme Officer", job_title_source="AD")
    assert "mail eq 'jan.kowalski@example.com'" in unquote(ad.calls[1].request.url)


def test_build_actor_snapshot_arrange_ad_without_title_act_build_assert_empty_ad_title(
    user: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USERS_URL, json={"value": [{"jobTitle": None}]})

    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="", job_title_source="AD")


def test_build_actor_snapshot_arrange_azure_id_act_build_assert_lookup_by_id(
    user_with_azure_id: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USER_BY_ID_URL, json={"jobTitle": "Programme Officer"})

    snapshot = build_actor_snapshot(user_with_azure_id)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Programme Officer", job_title_source="AD")


def test_build_actor_snapshot_arrange_azure_id_unknown_to_ad_act_build_assert_lookup_by_email(
    user_with_azure_id: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USER_BY_ID_URL, json={"error": "not found"}, status=404)
    ad.add(responses.GET, USERS_URL, json={"value": [{"jobTitle": "Programme Officer"}]})

    snapshot = build_actor_snapshot(user_with_azure_id)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Programme Officer", job_title_source="AD")


def test_build_actor_snapshot_arrange_no_ad_credentials_act_build_assert_stored_title(
    user: User, ad_without_credentials: None
) -> None:
    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Stored Title", job_title_source="USER_RECORD")


def test_build_actor_snapshot_arrange_token_request_fails_act_build_assert_stored_title(
    user: User, ad_token_failure: responses.RequestsMock
) -> None:
    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Stored Title", job_title_source="USER_RECORD")


def test_build_actor_snapshot_arrange_user_query_fails_act_build_assert_stored_title(
    user: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USERS_URL, body="fail", status=500)

    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Stored Title", job_title_source="USER_RECORD")


def test_build_actor_snapshot_arrange_user_unknown_to_ad_act_build_assert_stored_title(
    user: User, ad: responses.RequestsMock
) -> None:
    ad.add(responses.GET, USERS_URL, json={"value": []})

    snapshot = build_actor_snapshot(user)

    assert snapshot == ActorSnapshot(name="Jan Kowalski", job_title="Stored Title", job_title_source="USER_RECORD")


def test_build_actor_snapshot_arrange_user_without_names_act_build_assert_empty_name(
    nameless_user: User, ad_without_credentials: None
) -> None:
    snapshot = build_actor_snapshot(nameless_user)

    assert snapshot == ActorSnapshot(name="", job_title="Stored Title", job_title_source="USER_RECORD")


def test_build_actor_snapshot_arrange_no_user_act_build_assert_empty_snapshot() -> None:
    snapshot = build_actor_snapshot(None)

    assert snapshot == ActorSnapshot(name="", job_title="", job_title_source="")


def test_as_model_fields_arrange_snapshot_act_map_assert_prefixed_keys() -> None:
    snapshot = ActorSnapshot(name="Jan Kowalski", job_title="Programme Officer", job_title_source="AD")

    assert snapshot.as_model_fields("created_by") == {
        "created_by_name": "Jan Kowalski",
        "created_by_job_title": "Programme Officer",
        "created_by_job_title_source": "AD",
    }


def test_apply_to_arrange_snapshot_act_apply_assert_prefixed_attributes_set(legacy_approval: Approval) -> None:
    snapshot = ActorSnapshot(name="Jan Kowalski", job_title="Programme Officer", job_title_source="AD")

    snapshot.apply_to(legacy_approval, "created_by")

    assert legacy_approval.created_by_name == "Jan Kowalski"
    assert legacy_approval.created_by_job_title == "Programme Officer"
    assert legacy_approval.created_by_job_title_source == "AD"


def test_actor_display_arrange_snapshot_act_display_assert_snapshot_name_and_title(
    snapshot_approval: Approval,
) -> None:
    assert actor_display(snapshot_approval, "created_by") == "Old Name (Old Title)"


def test_actor_display_arrange_snapshot_without_title_act_display_assert_name_only(
    snapshot_approval_without_title: Approval,
) -> None:
    assert actor_display(snapshot_approval_without_title, "created_by") == "Old Name"


def test_actor_display_arrange_legacy_row_act_display_assert_live_user_values(legacy_approval: Approval) -> None:
    assert actor_display(legacy_approval, "created_by") == "Jan Kowalski (Stored Title)"


def test_actor_display_arrange_legacy_row_without_user_act_display_assert_empty(
    legacy_approval_without_user: Approval,
) -> None:
    assert actor_display(legacy_approval_without_user, "created_by") == ""
