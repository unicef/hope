import logging
from typing import Any, Dict

from django.conf import settings
from django.db.models import Q, QuerySet
from django.utils import timezone

from constance import config

from hct_mis_api.apps.account.models import RoleAssignment, User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.utils.mailjet import MailjetClient

logger = logging.getLogger(__name__)


class PaymentNotification:
    ACTION_SEND_FOR_APPROVAL = PaymentPlan.Action.SEND_FOR_APPROVAL.name
    ACTION_APPROVE = PaymentPlan.Action.APPROVE.name
    ACTION_AUTHORIZE = PaymentPlan.Action.AUTHORIZE.name
    ACTION_REVIEW = PaymentPlan.Action.REVIEW.name  # payment plan release

    ACTION_TO_RECIPIENTS_PERMISSIONS_MAP = {
        ACTION_SEND_FOR_APPROVAL: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
        ACTION_APPROVE: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
        ACTION_AUTHORIZE: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        ACTION_REVIEW: Permissions.PM_DOWNLOAD_XLSX_FOR_FSP.name,
    }

    ACTION_PREPARE_EMAIL_BODIES_MAP = {
        ACTION_SEND_FOR_APPROVAL: {
            "action_name": "sent for approval",
            "subject": "Payment pending for Approval",
            "recipient_title": "Approver",
        },
        ACTION_APPROVE: {
            "action_name": "approved",
            "subject": "Payment pending for Authorization",
            "recipient_title": "Authorizer",
        },
        ACTION_AUTHORIZE: {
            "action_name": "authorized",
            "subject": "Payment pending for Release",
            "recipient_title": "Reviewer",
        },
        ACTION_REVIEW: {
            "action_name": "released",
            "subject": "Payment is Released",
            "recipient_title": "Reviewer",
        },
    }

    def __init__(self, payment_plan: PaymentPlan, action: str, action_user: User, action_date: str) -> None:
        self.payment_plan = payment_plan
        self.action = action
        self.action_user = action_user
        self.action_date = action_date
        self.payment_plan_creator = self.payment_plan.created_by
        self.payment_plan_creation_date = self.payment_plan.created_at
        self.email_subject = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["subject"]
        self.action_name = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["action_name"]
        self.recipient_title = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["recipient_title"]
        self.user_recipients = self._prepare_user_recipients()
        self.email = self._prepare_email()
        self.enable_email_notification = self.payment_plan.business_area.enable_email_notification

    def _prepare_user_recipients(self) -> QuerySet[User]:
        permission = PaymentNotification.ACTION_TO_RECIPIENTS_PERMISSIONS_MAP[self.action]
        business_area = self.payment_plan.business_area
        program = self.payment_plan.program

        role_assignments = (
            RoleAssignment.objects.filter(
                Q(role__permissions__contains=[permission])
                & Q(business_area=business_area)
                & (Q(program=None) | Q(program=program))
            )
            .exclude(expiry_date__lt=timezone.now())
            .distinct()
        )
        users = (
            User.objects.filter(
                Q(role_assignments__in=role_assignments) | Q(partner__role_assignments__in=role_assignments)
            )
            .exclude(id=self.action_user.id)
            .distinct()
        )

        if settings.ENV == "prod":
            users = users.exclude(is_superuser=True)
        return users

    def _prepare_email(self) -> MailjetClient:
        body_variables = self._prepare_body_variables()
        email = MailjetClient(
            mailjet_template_id=config.MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION,
            subject=self.email_subject,
            recipients=[user_recipient.email for user_recipient in self.user_recipients],
            ccs=[self.action_user.email],
            variables=body_variables,
        )
        return email

    def send_email_notification(self) -> None:
        if config.SEND_PAYMENT_PLANS_NOTIFICATION and self.enable_email_notification:
            try:
                self.email.send_email()
            except Exception as e:  # pragma: no cover
                logger.exception(e)

    def _prepare_body_variables(self) -> Dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        variables = {
            "first_name": "Payment Plan",
            "last_name": self.recipient_title,
            "action_name": self.action_name,
            "payment_plan_url": (
                f"{protocol}://{settings.FRONTEND_HOST}/{self.payment_plan.business_area.slug}/programs/"
                f'{encode_id_base64(self.payment_plan.program.id, "Program")}/payment-module/payment-plans/'
                f'{encode_id_base64(self.payment_plan.id, "PaymentPlan")}'
            ),
            "payment_plan_id": self.payment_plan.unicef_id,
            "payment_plan_creator": self.payment_plan_creator.get_full_name(),
            "payment_plan_creation_date": f"{self.payment_plan_creation_date:%-d %B %Y}",
            "action_user": self.action_user.get_full_name(),
            "action_date": self.action_date,
            "program_name": self.payment_plan.program.name,
        }
        return variables
