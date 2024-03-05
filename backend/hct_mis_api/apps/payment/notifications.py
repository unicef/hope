import logging
from typing import Any, Dict, List, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from constance import config

from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.permissions import (
    DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER,
    Permissions,
)
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import Approval, PaymentPlan

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

    def __init__(self, payment_plan: PaymentPlan, action: str) -> None:
        self.payment_plan = payment_plan
        self.action = action
        self.approval_process = self.payment_plan.approval_process.first()
        self.payment_plan_creator = self.payment_plan.created_by
        self.payment_plan_creation_date = self.payment_plan.created_at
        self.email_subject = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["subject"]
        self.action_name = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["action_name"]
        self.user_recipients = self._prepare_user_recipients()
        self._prepare_action_user_and_date()
        self.emails = self._prepare_emails()
        self.enable_email_notification = self.payment_plan.business_area.enable_email_notification

    def _prepare_default_context(self, user_recipient: User) -> Dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        context = {
            "first_name": user_recipient.first_name,
            "last_name": user_recipient.last_name,
            "action_name": self.action_name,
            "payment_plan_url": (
                f"{protocol}://{settings.FRONTEND_HOST}/{self.payment_plan.business_area.slug}/programs/"
                f'{encode_id_base64(self.payment_plan.program.id, "Program")}/payment-module/payment-plans/'
                f'{encode_id_base64(self.payment_plan.id, "PaymentPlan")}'
            ),
            "payment_plan_id": self.payment_plan.unicef_id,
            "payment_plan": self.payment_plan,
            "payment_plan_creator": self.payment_plan_creator,
            "payment_plan_creation_date": self.payment_plan_creation_date,
            "action_user": self.action_user,
            "action_date": self.action_date,
            "program": self.payment_plan.program,
        }
        return context

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

        partners_recipients = []
        partners_with_program_access = []
        for partner in Partner.objects.all():
            program_ids = partner.get_program_ids_for_business_area(str(business_area.id))
            if str(program.id) in program_ids:
                partners_with_program_access.append(partner)
                partner_roles_ids = partner.get_permissions().roles_for(str(business_area.id))
                if Role.objects.filter(id__in=partner_roles_ids, permissions__contains=[permission]).exists():
                    partners_recipients.append(partner)

        program_access_q = Q(partner__in=partners_with_program_access)
        unicef_q = (
            Q(user_roles__business_area=business_area, partner__name="UNICEF")
            if permission in DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER
            else Q()
        )
        return User.objects.filter(
            (Q(user_roles__in=user_roles) & program_access_q) | Q(partner__in=partners_recipients) | unicef_q
        ).distinct()

    def _prepare_action_user_and_date(self) -> None:
        PaymentNotification.ACTION_GET_DATA_MAP[self.action](self)

    def _prepare_emails(self) -> List[EmailMultiAlternatives]:
        return [self._prepare_email(user) for user in self.user_recipients.exclude(id=self.action_user.id)]

    def _prepare_email(self, user_recipient: User) -> EmailMultiAlternatives:
        text_body, html_body = self._prepare_bodies(user_recipient)
        email = EmailMultiAlternatives(
            subject=self.email_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[user_recipient.email],
            body=text_body,
            cc=[self.action_user.email],
        )
        email.attach_alternative(html_body, "text/html")
        return email

    def send_email_notification(self) -> None:
        if not config.SEND_PAYMENT_PLANS_NOTIFICATION or not self.enable_email_notification:
            return
        try:
            for email in self.emails:
                email.send()
        except Exception as e:
            logger.exception(e)

    def _prepare_bodies(self, user_recipient: User) -> Tuple[str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("payment/payment_plan_action.html", context)
        html_body = render_to_string("payment/payment_plan_action.txt", context)
        return text_body, html_body

    def _get_sent_for_approval_action_data(self) -> None:
        self.action_user = self.approval_process.sent_for_approval_by
        self.action_date = self.approval_process.sent_for_approval_date

    def _get_approved_action_data(self) -> None:
        approval = self.approval_process.approvals.filter(type=Approval.APPROVAL).order_by("created_at").last()
        self.action_user = approval.created_by
        self.action_date = approval.created_at

    def _get_authorized_action_data(self) -> None:
        authorization = (
            self.approval_process.approvals.filter(type=Approval.AUTHORIZATION).order_by("created_at").last()
        )
        self.action_user = authorization.created_by
        self.action_date = authorization.created_at

    def _get_released_action_data(self) -> None:
        release = self.approval_process.approvals.filter(type=Approval.FINANCE_RELEASE).order_by("created_at").last()
        self.action_user = release.created_by
        self.action_date = release.created_at

    ACTION_GET_DATA_MAP = {
        ACTION_SEND_FOR_APPROVAL: _get_sent_for_approval_action_data,
        ACTION_APPROVE: _get_approved_action_data,
        ACTION_AUTHORIZE: _get_authorized_action_data,
        ACTION_REVIEW: _get_released_action_data,
    }
