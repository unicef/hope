import importlib
from typing import Any

from django.apps import apps
import pytest

from extras.test_utils.factories import ApprovalFactory, ApprovalProcessFactory, UserFactory
from hope.models import Approval, ApprovalProcess, User

pytestmark = pytest.mark.django_db

migration_module = importlib.import_module("hope.apps.payment.migrations.0085_migration")


@pytest.fixture
def user() -> User:
    return UserFactory(
        first_name="Jan", last_name="Kowalski", email="jan.kowalski@example.com", job_title="Programme Officer"
    )


@pytest.fixture
def nameless_user() -> User:
    return UserFactory(first_name="", last_name="", email="nameless@example.com", job_title="Finance Officer")


@pytest.fixture
def approval_without_snapshot(user: User) -> Approval:
    return ApprovalFactory(created_by=user)


@pytest.fixture
def approval_of_nameless_user(nameless_user: User) -> Approval:
    return ApprovalFactory(created_by=nameless_user)


@pytest.fixture
def approval_with_ad_snapshot(user: User) -> Approval:
    return ApprovalFactory(
        created_by=user,
        created_by_name="Old Name",
        created_by_job_title="Old Title",
        created_by_job_title_source="AD",
    )


@pytest.fixture
def approval_without_user() -> Approval:
    return ApprovalFactory(created_by=None)


@pytest.fixture
def approval_process_sent_for_authorization(user: User) -> ApprovalProcess:
    return ApprovalProcessFactory(sent_for_authorization_by=user)


def test_copy_actor_arrange_approval_without_snapshot_act_migrate_assert_user_record_copied(
    approval_without_snapshot: Approval,
) -> None:
    migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_without_snapshot.refresh_from_db()
    assert approval_without_snapshot.created_by_name == "Jan Kowalski"
    assert approval_without_snapshot.created_by_job_title == "Programme Officer"
    assert approval_without_snapshot.created_by_job_title_source == "USER_RECORD"


def test_copy_actor_arrange_user_without_names_act_migrate_assert_email_as_name(
    approval_of_nameless_user: Approval,
) -> None:
    migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_of_nameless_user.refresh_from_db()
    assert approval_of_nameless_user.created_by_name == "nameless@example.com"
    assert approval_of_nameless_user.created_by_job_title == "Finance Officer"
    assert approval_of_nameless_user.created_by_job_title_source == "USER_RECORD"


def test_copy_actor_arrange_approval_with_ad_snapshot_act_migrate_assert_snapshot_kept(
    approval_with_ad_snapshot: Approval,
) -> None:
    migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_with_ad_snapshot.refresh_from_db()
    assert approval_with_ad_snapshot.created_by_name == "Old Name"
    assert approval_with_ad_snapshot.created_by_job_title == "Old Title"
    assert approval_with_ad_snapshot.created_by_job_title_source == "AD"


def test_copy_actor_arrange_approval_without_user_act_migrate_assert_left_empty(
    approval_without_user: Approval,
) -> None:
    migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_without_user.refresh_from_db()
    assert approval_without_user.created_by_name == ""
    assert approval_without_user.created_by_job_title == ""
    assert approval_without_user.created_by_job_title_source == ""


def test_copy_actor_arrange_approval_process_sent_for_authorization_act_migrate_assert_user_record_copied(
    approval_process_sent_for_authorization: ApprovalProcess,
) -> None:
    migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_process_sent_for_authorization.refresh_from_db()
    assert approval_process_sent_for_authorization.sent_for_authorization_by_name == "Jan Kowalski"
    assert approval_process_sent_for_authorization.sent_for_authorization_by_job_title == "Programme Officer"
    assert approval_process_sent_for_authorization.sent_for_authorization_by_job_title_source == "USER_RECORD"
    assert approval_process_sent_for_authorization.sent_for_approval_by_job_title_source == ""


def test_copy_actor_arrange_approvals_of_two_users_act_migrate_assert_one_user_select_and_update_per_user(
    approval_without_snapshot: Approval, approval_of_nameless_user: Approval, django_assert_num_queries: Any
) -> None:
    with django_assert_num_queries(6):
        migration_module.copy_actor_from_user_record(apps, schema_editor=None)

    approval_without_snapshot.refresh_from_db()
    approval_of_nameless_user.refresh_from_db()
    assert approval_without_snapshot.created_by_job_title_source == "USER_RECORD"
    assert approval_of_nameless_user.created_by_job_title_source == "USER_RECORD"
