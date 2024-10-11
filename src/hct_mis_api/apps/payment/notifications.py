import logging
from typing import Any, Dict, List

from django.conf import settings
from django.db.models import Q, QuerySet
from django.utils import timezone

from constance import config

from hct_mis_api.apps.account.models import Partner, User, UserRole
from hct_mis_api.apps.account.permissions import (
    DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER,
    Permissions,
)
from hct_mis_api.apps.core.models import BusinessAreaPartnerThrough
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
        },
        ACTION_APPROVE: {
            "action_name": "approved",
            "subject": "Payment pending for Authorization",
        },
        ACTION_AUTHORIZE: {
            "action_name": "authorized",
            "subject": "Payment pending for Release",
        },
        ACTION_REVIEW: {
            "action_name": "released",
            "subject": "Payment is Released",
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
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()
        self.enable_email_notification = self.payment_plan.business_area.enable_email_notification

    def _prepare_user_recipients(self) -> QuerySet[User]:
        permission = PaymentNotification.ACTION_TO_RECIPIENTS_PERMISSIONS_MAP[self.action]
        business_area = self.payment_plan.business_area
        program = self.payment_plan.program

        user_roles = (
            UserRole.objects.filter(
                role__permissions__contains=[permission],
                business_area=business_area,
            )
            .exclude(expiry_date__lt=timezone.now())
            .distinct()
        )

        ba_partner_with_permission = BusinessAreaPartnerThrough.objects.filter(
            business_area=business_area,
            roles__permissions__contains=[permission],
        ).distinct()
        partners_with_permission = Partner.objects.filter(business_area_partner_through__in=ba_partner_with_permission)
        partner_role_q = Q(partner__in=partners_with_permission)

        program_access_q = Q(partner__in=program.partners.all())

        unicef_q = (
            Q(user_roles__business_area=business_area, partner__name="UNICEF")
            if permission in DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
            else Q()
        )
        return User.objects.filter(
            (Q(user_roles__in=user_roles) & program_access_q) | Q(partner_role_q & program_access_q) | unicef_q
        ).distinct()

    def _prepare_emails(self) -> List[MailjetClient]:
        return [self._prepare_email(user) for user in self.user_recipients.exclude(id=self.action_user.id)]

    def _prepare_email(self, user_recipient: User) -> MailjetClient:
        body_variables = self._prepare_body_variables(user_recipient)
        email = MailjetClient(
            mailjet_template_id=config.MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION,
            subject=self.email_subject,
            recipients=[user_recipient.email],
            ccs=[self.action_user.email],
            variables=body_variables,
        )
        return email

    def send_email_notification(self) -> None:
        if config.SEND_PAYMENT_PLANS_NOTIFICATION and self.enable_email_notification:
            try:
                for email in self.emails:
                    email.send_email()
            except Exception as e:  # pragma: no cover
                logger.exception(e)

    def _prepare_body_variables(self, user_recipient: User) -> Dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        variables = {
            "first_name": user_recipient.first_name,
            "last_name": user_recipient.last_name,
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
