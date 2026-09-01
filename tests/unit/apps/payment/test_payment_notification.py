from datetime import UTC, datetime
from typing import Any

from constance.test import override_config
from django.conf import settings
from django.test import override_settings
import pytest

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.timezones import format_human_datetime
from hope.apps.payment.notifications import PaymentNotification
from hope.models import PaymentPlan, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db

ACTION_DATETIME = datetime(2026, 8, 21, 12, 30, tzinfo=UTC)


@pytest.fixture
def action_permissions_list():
    return [
        Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
        Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
        Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
        Permissions.PM_DOWNLOAD_XLSX_FOR_FSP,
        Permissions.PM_CLOSE_FINISHED,
        Permissions.PM_MARK_READY_FOR_CLOSURE,
    ]


@pytest.fixture
def unicef_partner():
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq_partner(unicef_partner):
    return PartnerFactory(name=settings.UNICEF_HQ_PARTNER, parent=unicef_partner)


@pytest.fixture
def business_area(unicef_partner, unicef_hq_partner):
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def partner_unicef_in_ba(unicef_partner, business_area):
    return PartnerFactory(name=f"UNICEF Partner for {business_area.slug}", parent=unicef_partner)


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program2(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def notification_setup(
    business_area,
    program,
    program2,
    action_permissions_list,
    unicef_hq_partner,
    partner_unicef_in_ba,
    create_user_role_with_permissions,
    create_partner_role_with_permissions,
):
    partner_empty = PartnerFactory(name="Empty Partner")
    user_payment_plan_creator = UserFactory(
        username="user_payment_plan_creator", email="user_payment_plan_creator@example.com", partner=partner_empty
    )
    user_action_user = UserFactory(username="user_action_user", email="user_action_user@example.com")

    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        created_by=user_payment_plan_creator,
        program_cycle=program.cycles.first(),
    )

    action_permission_values = [perm.value for perm in action_permissions_list]

    role_for_unicef_partners, _ = Role.objects.update_or_create(
        name="Role for UNICEF Partners",
        defaults={"permissions": [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.value]},
    )
    RoleAssignment.objects.get_or_create(
        partner=partner_unicef_in_ba,
        role=role_for_unicef_partners,
        business_area=business_area,
        program=None,
    )

    partner_unicef_in_ba.allowed_business_areas.add(business_area)
    unicef_hq_partner.allowed_business_areas.add(business_area)

    role_assignment = unicef_hq_partner.role_assignments.filter(business_area=business_area).first()
    if role_assignment and role_assignment.role:
        role_assignment.role.permissions = action_permission_values
        role_assignment.role.save()
    else:
        role_all, _ = Role.objects.update_or_create(
            name="Role with all permissions",
            defaults={"permissions": action_permission_values},
        )
        RoleAssignment.objects.update_or_create(
            partner=unicef_hq_partner,
            business_area=business_area,
            program=None,
            defaults={"role": role_all},
        )

    create_user_role_with_permissions(
        user_action_user,
        action_permissions_list,
        business_area,
        program=program,
        name="Role with action permissions",
    )

    partner_with_different_role_in_program = PartnerFactory(name="Partner with different role in program")
    create_partner_role_with_permissions(
        partner_with_different_role_in_program,
        [Permissions.PROGRAMME_CREATE],
        business_area,
        program=program,
        name="Role with different permissions",
    )

    partner_with_approval_permission_in_different_program = PartnerFactory(
        name="Partner with approval permission in different program"
    )
    create_partner_role_with_permissions(
        partner_with_approval_permission_in_different_program,
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    partner_with_action_permissions = PartnerFactory(name="Partner with action permissions")
    create_partner_role_with_permissions(
        partner_with_action_permissions,
        action_permissions_list,
        business_area,
        program=program,
        name="Role with action permissions",
    )

    partner_with_action_permissions_in_whole_ba = PartnerFactory(
        name="Partner with action permissions in whole business area"
    )
    create_partner_role_with_permissions(
        partner_with_action_permissions_in_whole_ba,
        action_permissions_list,
        business_area,
        whole_business_area_access=True,
        name="Role with action permissions",
    )

    users = {}

    users["user_with_partner_unicef_hq"] = UserFactory(
        username="user_with_partner_unicef_hq",
        email="user_with_partner_unicef_hq@example.com",
        partner=unicef_hq_partner,
    )
    users["user_with_partner_unicef_in_ba"] = UserFactory(
        username="user_with_partner_unicef_in_ba",
        email="user_with_partner_unicef_in_ba@example.com",
        partner=partner_unicef_in_ba,
    )

    users["user_with_no_permissions"] = UserFactory(
        username="user_with_no_permissions", email="user_with_no_permissions@example.com", partner=partner_empty
    )
    users["user_with_no_permissions_partner_with_different_role_in_program"] = UserFactory(
        username="user_with_no_permissions_partner_with_different_role_in_program",
        email="user_with_no_permissions_partner_with_different_role_in_program@example.com",
        partner=partner_with_different_role_in_program,
    )
    users["user_with_no_permissions_partner_with_approval_permission_in_different_program"] = UserFactory(
        username="user_with_no_permissions_partner_with_approval_permission_in_different_program",
        email="user_with_no_permissions_partner_with_approval_permission_in_different_program@example.com",
        partner=partner_with_approval_permission_in_different_program,
    )
    users["user_with_no_permissions_partner_with_action_permissions"] = UserFactory(
        username="user_with_no_permissions_partner_with_action_permissions",
        email="user_with_no_permissions_partner_with_action_permissions@example.com",
        partner=partner_with_action_permissions,
    )
    users["user_with_no_permissions_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        username="user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        email="user_with_no_permissions_partner_with_action_permissions_in_whole_ba@example.com",
        partner=partner_with_action_permissions_in_whole_ba,
    )

    users["user_with_approval_permission_partner_unicef_in_ba"] = UserFactory(
        username="user_with_approval_permission_partner_unicef_in_ba",
        email="user_with_approval_permission_partner_unicef_in_ba@example.com",
        partner=partner_unicef_in_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_different_role_in_program"] = UserFactory(
        username="user_with_approval_permission_partner_with_different_role_in_program",
        email="user_with_approval_permission_partner_with_different_role_in_program@example.com",
        partner=partner_with_different_role_in_program,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_approval_permission_in_different_program"] = UserFactory(
        username="user_with_approval_permission_partner_with_approval_permission_in_different_program",
        email="user_with_approval_permission_partner_with_approval_permission_in_different_program@example.com",
        partner=partner_with_approval_permission_in_different_program,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_action_permissions"] = UserFactory(
        username="user_with_approval_permission_partner_with_action_permissions",
        email="user_with_approval_permission_partner_with_action_permissions@example.com",
        partner=partner_with_action_permissions,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        username="user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        email="user_with_approval_permission_partner_with_action_permissions_in_whole_ba@example.com",
        partner=partner_with_action_permissions_in_whole_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_empty"] = UserFactory(
        username="user_with_approval_permission_partner_empty",
        email="user_with_approval_permission_partner_empty@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_unicef_in_ba"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_unicef_in_ba",
        email="user_with_approval_permission_in_ba_partner_unicef_in_ba@example.com",
        partner=partner_unicef_in_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_different_role_in_program"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        email="user_with_approval_permission_in_ba_partner_with_different_role_in_program@example.com",
        partner=partner_with_different_role_in_program,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        email="user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program@example.com",
        partner=partner_with_approval_permission_in_different_program,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_action_permissions"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_with_action_permissions",
        email="user_with_approval_permission_in_ba_partner_with_action_permissions@example.com",
        partner=partner_with_action_permissions,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        email="user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba@example.com",
        partner=partner_with_action_permissions_in_whole_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_empty"] = UserFactory(
        username="user_with_approval_permission_in_ba_partner_empty",
        email="user_with_approval_permission_in_ba_partner_empty@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_unicef_in_ba"] = UserFactory(
        username="user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        email="user_with_approval_permission_wrong_program_partner_unicef_in_ba@example.com",
        partner=partner_unicef_in_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_different_role_in_program"] = UserFactory(
        username="user_with_approval_permission_wrong_program_partner_with_different_role_in_program",
        email="user_with_approval_permission_wrong_program_partner_with_different_role_in_program@example.com",
        partner=partner_with_different_role_in_program,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program"] = (
        UserFactory(
            username="user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program",
            email="user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program@example.com",
            partner=partner_with_approval_permission_in_different_program,
        )
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_action_permissions"] = UserFactory(
        username="user_with_approval_permission_wrong_program_partner_with_action_permissions",
        email="user_with_approval_permission_wrong_program_partner_with_action_permissions@example.com",
        partner=partner_with_action_permissions,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        username="user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        email="user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba@example.com",
        partner=partner_with_action_permissions_in_whole_ba,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_empty"] = UserFactory(
        username="user_with_approval_permission_wrong_program_partner_empty",
        email="user_with_approval_permission_wrong_program_partner_empty@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_authorize_permission"] = UserFactory(
        username="user_with_authorize_permission",
        email="user_with_authorize_permission@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_authorize_permission"],
        [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
        business_area,
        whole_business_area_access=True,
        name="Role with authorize permission",
    )

    users["user_with_review_permission"] = UserFactory(
        username="user_with_review_permission", email="user_with_review_permission@example.com", partner=partner_empty
    )
    create_user_role_with_permissions(
        users["user_with_review_permission"],
        [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
        business_area,
        whole_business_area_access=True,
        name="Role with review permission",
    )

    users["user_with_download_xlsx_permission"] = UserFactory(
        username="user_with_download_xlsx_permission",
        email="user_with_download_xlsx_permission@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_download_xlsx_permission"],
        [Permissions.PM_DOWNLOAD_XLSX_FOR_FSP],
        business_area,
        whole_business_area_access=True,
        name="Role with download xlsx permission",
    )

    users["user_with_close_permission"] = UserFactory(
        username="user_with_close_permission", email="user_with_close_permission@example.com", partner=partner_empty
    )
    create_user_role_with_permissions(
        users["user_with_close_permission"],
        [Permissions.PM_CLOSE_FINISHED],
        business_area,
        whole_business_area_access=True,
        name="Role with close permission",
    )

    users["user_with_mark_ready_permission"] = UserFactory(
        username="user_with_mark_ready_permission",
        email="user_with_mark_ready_permission@example.com",
        partner=partner_empty,
    )
    create_user_role_with_permissions(
        users["user_with_mark_ready_permission"],
        [Permissions.PM_MARK_READY_FOR_CLOSURE],
        business_area,
        whole_business_area_access=True,
        name="Role with mark ready for closure permission",
    )

    users["user_with_action_permissions"] = UserFactory(
        username="user_with_action_permissions", email="user_with_action_permissions@example.com", partner=partner_empty
    )
    create_user_role_with_permissions(
        users["user_with_action_permissions"],
        action_permissions_list,
        business_area,
        whole_business_area_access=True,
        name="Role with action permissions",
    )

    return {
        "payment_plan": payment_plan,
        "user_action_user": user_action_user,
        "users": users,
    }


@pytest.fixture
def distinct_timezone_notification_data(notification_setup: dict) -> tuple[PaymentPlan, User]:
    action_user = notification_setup["user_action_user"]
    action_user.timezone = "America/New_York"
    action_user.save(update_fields=("timezone",))
    recipient = notification_setup["users"]["user_with_action_permissions"]
    recipient.timezone = "Europe/Warsaw"
    recipient.save(update_fields=("timezone",))
    return notification_setup["payment_plan"], action_user


@pytest.fixture
def notification_data_without_recipients(notification_setup: dict) -> tuple[PaymentPlan, User]:
    RoleAssignment.objects.all().delete()
    return notification_setup["payment_plan"], notification_setup["user_action_user"]


def test_prepare_user_recipients_for_send_for_approval(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
        "user_with_partner_unicef_in_ba",
    ]


def test_prepare_user_recipients_for_approve(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.APPROVE.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_authorize_permission",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
    ]


def test_prepare_user_recipients_for_authorize(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.AUTHORIZE.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
        "user_with_review_permission",
    ]


def test_prepare_user_recipients_for_release(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.REVIEW.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_download_xlsx_permission",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
    ]


def test_prepare_user_recipients_for_mark_ready_for_closure(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_close_permission",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
    ]


def test_prepare_user_recipients_for_send_back_to_finished(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_BACK_TO_FINISHED.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    assert sorted(payment_notification.user_recipients.values_list("username", flat=True)) == [
        "user_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_mark_ready_permission",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
        "user_with_partner_unicef_hq",
    ]


def test_prepare_notification_from_refetched_payment_plan_stays_within_query_budget(
    notification_setup: dict, django_assert_num_queries: Any
) -> None:
    payment_plan = PaymentPlan.objects.get(pk=notification_setup["payment_plan"].pk)

    with django_assert_num_queries(5):
        PaymentNotification(
            payment_plan,
            PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name,
            notification_setup["user_action_user"],
            ACTION_DATETIME,
        )


def test_action_user_is_ccd_and_excluded_from_recipients_for_mark_ready_for_closure(
    notification_setup: dict,
) -> None:
    action_user = notification_setup["user_action_user"]
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name,
        action_user,
        ACTION_DATETIME,
    )

    assert len(payment_notification.emails) == 1
    assert action_user not in payment_notification.user_recipients.all()
    assert action_user.email not in payment_notification.emails[0].recipients
    assert action_user.email in payment_notification.emails[0].ccs


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification_subject_mark_ready_for_closure(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    assert len(payment_notification.emails) == 1
    assert payment_notification.emails[0].subject == "Payment pending for Closure"


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification_mark_ready_for_closure(notification_setup: dict, mocker: Any) -> None:
    mock_send = mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert mock_send.call_count == 1


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification_subject_send_back_to_finished(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_BACK_TO_FINISHED.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    assert len(payment_notification.emails) == 1
    assert payment_notification.emails[0].subject == "Payment sent back to Finished"


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification_send_back_to_finished(notification_setup: dict, mocker: Any) -> None:
    mock_send = mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_BACK_TO_FINISHED.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert mock_send.call_count == 1


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification(notification_setup: dict, mocker: Any) -> None:
    mock_send = mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert mock_send.call_count == 1


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification_subject_send_for_approval(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    assert len(payment_notification.emails) == 1
    assert payment_notification.emails[0].subject == "Payment pending for Approval"


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
)
@override_settings(CATCH_ALL_EMAIL=["catchallemail@email.com", "catchallemail2@email.com"])
def test_send_email_notification_catch_all_email(notification_setup: dict, mocker: Any) -> None:
    mock_post = mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert len(payment_notification.emails) == 1
    assert len(payment_notification.emails[0].recipients) == 2
    assert "catchallemail@email.com" in payment_notification.emails[0].recipients
    assert "catchallemail2@email.com" in payment_notification.emails[0].recipients
    assert mock_post.call_count == 1


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
)
def test_send_email_notification_without_catch_all_email(notification_setup: dict, mocker: Any) -> None:
    mock_post = mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert sorted(payment_notification.emails[0].recipients) == [
        "user_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_empty@example.com",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_partner_empty@example.com",
        "user_with_approval_permission_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_partner_with_action_permissions@example.com",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_no_permissions_partner_with_action_permissions@example.com",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_partner_unicef_hq@example.com",
        "user_with_partner_unicef_in_ba@example.com",
    ]

    assert mock_post.call_count == 1


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
)
def test_send_email_notification_exclude_superuser(notification_setup: dict, mocker: Any) -> None:
    mock_post = mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    users = notification_setup["users"]
    users["user_with_partner_unicef_hq"].is_superuser = True
    users["user_with_partner_unicef_hq"].save()

    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert sorted(payment_notification.emails[0].recipients) == [
        "user_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_empty@example.com",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_partner_empty@example.com",
        "user_with_approval_permission_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_partner_with_action_permissions@example.com",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_no_permissions_partner_with_action_permissions@example.com",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_partner_unicef_in_ba@example.com",
    ]

    assert mock_post.call_count == 1


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
)
def test_send_email_notification_exclude_staff_user(notification_setup: dict, mocker: Any) -> None:
    mock_post = mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    users = notification_setup["users"]
    users["user_with_partner_unicef_hq"].is_staff = True
    users["user_with_partner_unicef_hq"].save()

    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()
    assert sorted(payment_notification.emails[0].recipients) == [
        "user_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_empty@example.com",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions@example.com",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_partner_empty@example.com",
        "user_with_approval_permission_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_partner_with_action_permissions@example.com",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program@example.com",
        "user_with_approval_permission_partner_with_different_role_in_program@example.com",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions@example.com",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_no_permissions_partner_with_action_permissions@example.com",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba@example.com",
        "user_with_partner_unicef_in_ba@example.com",
    ]

    assert mock_post.call_count == 1


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
    NOTIFY_INTERNAL_USERS=True,
)
def test_send_email_notification_include_internal_users(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    users = notification_setup["users"]
    users["user_with_partner_unicef_hq"].is_superuser = True
    users["user_with_partner_unicef_hq"].is_staff = True
    users["user_with_partner_unicef_hq"].save()

    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )
    payment_notification.send_email_notification()

    assert len(payment_notification.emails) == 1
    assert users["user_with_partner_unicef_hq"].email in payment_notification.emails[0].recipients


def test_notification_formats_action_datetime_in_requested_timezone(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        ACTION_DATETIME,
    )

    body_variables = payment_notification._prepare_body_variables("Europe/Warsaw")

    assert body_variables["action_date"] == format_human_datetime(
        ACTION_DATETIME,
        timezone_name="Europe/Warsaw",
    )


def test_notification_groups_recipients_and_action_user_by_timezone(
    distinct_timezone_notification_data: tuple[PaymentPlan, User],
) -> None:
    payment_plan, action_user = distinct_timezone_notification_data

    payment_notification = PaymentNotification(
        payment_plan,
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        action_user,
        ACTION_DATETIME,
    )

    assert len(payment_notification.emails) == 3
    assert payment_notification.emails[0].ccs == []
    assert payment_notification.emails[-1].recipients == [action_user.email]
    assert payment_notification.emails[-1].variables["action_date"] == format_human_datetime(
        ACTION_DATETIME,
        timezone_name="America/New_York",
    )


def test_notification_without_recipients_creates_cc_only_email(
    notification_data_without_recipients: tuple[PaymentPlan, User],
) -> None:
    payment_plan, action_user = notification_data_without_recipients

    payment_notification = PaymentNotification(
        payment_plan,
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        action_user,
        ACTION_DATETIME,
    )

    assert len(payment_notification.emails) == 1
    assert payment_notification.emails[0].recipients == []
    assert payment_notification.emails[0].ccs == [action_user.email]
