from typing import Any

from constance.test import override_config
from django.conf import settings
from django.test import override_settings
from django.utils import timezone
import pytest

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.payment.notifications import PaymentNotification
from hope.models import PaymentPlan, Role, RoleAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def action_permissions_list():
    return [
        Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
        Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
        Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
        Permissions.PM_DOWNLOAD_XLSX_FOR_FSP,
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
    user_payment_plan_creator = UserFactory(partner=partner_empty)
    user_action_user = UserFactory()

    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        created_by=user_payment_plan_creator,
        program_cycle=ProgramCycleFactory(program=program),
    )

    action_permission_values = [perm.value for perm in action_permissions_list]

    role_for_unicef_partners, _ = Role.objects.update_or_create(
        name="Role for UNICEF Partners",
        subsystem=Role.HOPE,
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
            subsystem=Role.HOPE,
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

    users["user_with_partner_unicef_hq"] = UserFactory(partner=unicef_hq_partner)
    users["user_with_partner_unicef_in_ba"] = UserFactory(partner=partner_unicef_in_ba)

    users["user_with_no_permissions"] = UserFactory(partner=partner_empty)
    users["user_with_no_permissions_partner_with_different_role_in_program"] = UserFactory(
        partner=partner_with_different_role_in_program
    )
    users["user_with_no_permissions_partner_with_approval_permission_in_different_program"] = UserFactory(
        partner=partner_with_approval_permission_in_different_program
    )
    users["user_with_no_permissions_partner_with_action_permissions"] = UserFactory(
        partner=partner_with_action_permissions
    )
    users["user_with_no_permissions_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        partner=partner_with_action_permissions_in_whole_ba
    )

    users["user_with_approval_permission_partner_unicef_in_ba"] = UserFactory(partner=partner_unicef_in_ba)
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_different_role_in_program"] = UserFactory(
        partner=partner_with_different_role_in_program
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_approval_permission_in_different_program"] = UserFactory(
        partner=partner_with_approval_permission_in_different_program
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_action_permissions"] = UserFactory(
        partner=partner_with_action_permissions
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        partner=partner_with_action_permissions_in_whole_ba
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_partner_empty"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_approval_permission_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_unicef_in_ba"] = UserFactory(partner=partner_unicef_in_ba)
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_different_role_in_program"] = UserFactory(
        partner=partner_with_different_role_in_program
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program"] = UserFactory(
        partner=partner_with_approval_permission_in_different_program
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_action_permissions"] = UserFactory(
        partner=partner_with_action_permissions
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        partner=partner_with_action_permissions_in_whole_ba
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_in_ba_partner_empty"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_approval_permission_in_ba_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        whole_business_area_access=True,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_unicef_in_ba"] = UserFactory(
        partner=partner_unicef_in_ba
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_unicef_in_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_different_role_in_program"] = UserFactory(
        partner=partner_with_different_role_in_program
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_different_role_in_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program"] = (
        UserFactory(partner=partner_with_approval_permission_in_different_program)
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_action_permissions"] = UserFactory(
        partner=partner_with_action_permissions
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_action_permissions"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba"] = UserFactory(
        partner=partner_with_action_permissions_in_whole_ba
    )
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_approval_permission_wrong_program_partner_empty"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_approval_permission_wrong_program_partner_empty"],
        [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
        business_area,
        program=program2,
        name="Role with approval permission",
    )

    users["user_with_authorize_permission"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_authorize_permission"],
        [Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE],
        business_area,
        whole_business_area_access=True,
        name="Role with authorize permission",
    )

    users["user_with_review_permission"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_review_permission"],
        [Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW],
        business_area,
        whole_business_area_access=True,
        name="Role with review permission",
    )

    users["user_with_download_xlsx_permission"] = UserFactory(partner=partner_empty)
    create_user_role_with_permissions(
        users["user_with_download_xlsx_permission"],
        [Permissions.PM_DOWNLOAD_XLSX_FOR_FSP],
        business_area,
        whole_business_area_access=True,
        name="Role with download xlsx permission",
    )

    users["user_with_action_permissions"] = UserFactory(partner=partner_empty)
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


def test_prepare_user_recipients_for_send_for_approval(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )

    users = notification_setup["users"]
    assert payment_notification.user_recipients.count() == 20

    for key in [
        "user_with_partner_unicef_hq",
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key] in payment_notification.user_recipients.all()

    assert notification_setup["user_action_user"] not in payment_notification.user_recipients.all()

    for key in [
        "user_with_no_permissions",
        "user_with_no_permissions_partner_with_different_role_in_program",
        "user_with_no_permissions_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_with_different_role_in_program",
        "user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_empty",
        "user_with_authorize_permission",
        "user_with_review_permission",
        "user_with_download_xlsx_permission",
    ]:
        assert users[key] not in payment_notification.user_recipients.all()


def test_prepare_user_recipients_for_approve(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.APPROVE.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )

    users = notification_setup["users"]
    assert payment_notification.user_recipients.count() == 11
    for key in [
        "user_with_authorize_permission",
        "user_with_partner_unicef_hq",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key] in payment_notification.user_recipients.all()

    assert notification_setup["user_action_user"] not in payment_notification.user_recipients.all()

    for key in [
        "user_with_no_permissions",
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_no_permissions_partner_with_different_role_in_program",
        "user_with_no_permissions_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_with_different_role_in_program",
        "user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_empty",
        "user_with_review_permission",
        "user_with_download_xlsx_permission",
    ]:
        assert users[key] not in payment_notification.user_recipients.all()


def test_prepare_user_recipients_for_authorize(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.AUTHORIZE.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )

    users = notification_setup["users"]
    assert payment_notification.user_recipients.count() == 11
    for key in [
        "user_with_review_permission",
        "user_with_partner_unicef_hq",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key] in payment_notification.user_recipients.all()

    assert notification_setup["user_action_user"] not in payment_notification.user_recipients.all()

    for key in [
        "user_with_no_permissions",
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_no_permissions_partner_with_different_role_in_program",
        "user_with_no_permissions_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_with_different_role_in_program",
        "user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_empty",
        "user_with_authorize_permission",
        "user_with_download_xlsx_permission",
    ]:
        assert users[key] not in payment_notification.user_recipients.all()


def test_prepare_user_recipients_for_release(notification_setup: dict) -> None:
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.REVIEW.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )

    users = notification_setup["users"]
    assert payment_notification.user_recipients.count() == 11
    for key in [
        "user_with_download_xlsx_permission",
        "user_with_partner_unicef_hq",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key] in payment_notification.user_recipients.all()

    assert notification_setup["user_action_user"] not in payment_notification.user_recipients.all()

    for key in [
        "user_with_no_permissions",
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_no_permissions_partner_with_different_role_in_program",
        "user_with_no_permissions_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_with_different_role_in_program",
        "user_with_approval_permission_wrong_program_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_wrong_program_partner_empty",
        "user_with_authorize_permission",
        "user_with_review_permission",
    ]:
        assert users[key] not in payment_notification.user_recipients.all()


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
def test_send_email_notification(notification_setup: dict, mocker: Any) -> None:
    mock_send = mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )
    payment_notification.send_email_notification()
    assert mock_send.call_count == 1


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
@override_settings(EMAIL_SUBJECT_PREFIX="test")
def test_send_email_notification_subject_test_env(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )
    assert payment_notification.email.subject == "[test] Payment pending for Approval"


@override_config(SEND_PAYMENT_PLANS_NOTIFICATION=True)
@override_settings(EMAIL_SUBJECT_PREFIX="")
def test_send_email_notification_subject_prod_env(notification_setup: dict, mocker: Any) -> None:
    mocker.patch("hope.apps.payment.notifications.MailjetClient.send_email")
    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )
    assert payment_notification.email.subject == "Payment pending for Approval"


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
        f"{timezone.now():%-d %B %Y}",
    )
    payment_notification.send_email_notification()
    assert len(payment_notification.email.recipients) == 2
    assert "catchallemail@email.com" in payment_notification.email.recipients
    assert "catchallemail2@email.com" in payment_notification.email.recipients
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
        f"{timezone.now():%-d %B %Y}",
    )
    payment_notification.send_email_notification()
    assert len(payment_notification.email.recipients) == 20

    users = notification_setup["users"]
    for key in [
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key].email in payment_notification.email.recipients

    assert mock_post.call_count == 1


@override_config(
    SEND_PAYMENT_PLANS_NOTIFICATION=True,
    ENABLE_MAILJET=True,
    MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION=1,
)
@override_settings(ENV="prod")
def test_send_email_notification_exclude_superuser(notification_setup: dict, mocker: Any) -> None:
    mock_post = mocker.patch("hope.apps.utils.celery_tasks.requests.post")
    users = notification_setup["users"]
    users["user_with_partner_unicef_hq"].is_superuser = True
    users["user_with_partner_unicef_hq"].save()

    payment_notification = PaymentNotification(
        notification_setup["payment_plan"],
        PaymentPlan.Action.SEND_FOR_APPROVAL.name,
        notification_setup["user_action_user"],
        f"{timezone.now():%-d %B %Y}",
    )
    payment_notification.send_email_notification()
    assert len(payment_notification.email.recipients) == 19
    assert users["user_with_partner_unicef_hq"].email not in payment_notification.email.recipients

    for key in [
        "user_with_partner_unicef_in_ba",
        "user_with_approval_permission_partner_unicef_in_ba",
        "user_with_approval_permission_partner_with_different_role_in_program",
        "user_with_approval_permission_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_partner_with_action_permissions",
        "user_with_approval_permission_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_partner_empty",
        "user_with_approval_permission_in_ba_partner_unicef_in_ba",
        "user_with_approval_permission_in_ba_partner_with_different_role_in_program",
        "user_with_approval_permission_in_ba_partner_with_approval_permission_in_different_program",
        "user_with_approval_permission_in_ba_partner_with_action_permissions",
        "user_with_approval_permission_in_ba_partner_with_action_permissions_in_whole_ba",
        "user_with_approval_permission_in_ba_partner_empty",
        "user_with_approval_permission_wrong_program_partner_unicef_in_ba",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions",
        "user_with_approval_permission_wrong_program_partner_with_action_permissions_in_whole_ba",
        "user_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions",
        "user_with_no_permissions_partner_with_action_permissions_in_whole_ba",
    ]:
        assert users[key].email in payment_notification.email.recipients

    assert mock_post.call_count == 1
