from collections import defaultdict
from datetime import datetime
import logging

from constance import config
from django.conf import settings
from django.db.models import QuerySet

from hope.apps.account.permissions import Permissions
from hope.apps.core.timezones import format_human_datetime, resolve_timezone_name
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import users_with_permissions
from hope.models import PaymentPlan, User

logger = logging.getLogger(__name__)


class PaymentNotification:
    ACTION_SEND_FOR_APPROVAL = PaymentPlan.Action.SEND_FOR_APPROVAL.name
    ACTION_APPROVE = PaymentPlan.Action.APPROVE.name
    ACTION_AUTHORIZE = PaymentPlan.Action.AUTHORIZE.name
    ACTION_REVIEW = PaymentPlan.Action.REVIEW.name  # payment plan release
    ACTION_MARK_READY_FOR_CLOSURE = PaymentPlan.Action.MARK_READY_FOR_CLOSURE.name
    ACTION_SEND_BACK_TO_FINISHED = PaymentPlan.Action.SEND_BACK_TO_FINISHED.name

    ACTION_TO_RECIPIENTS_PERMISSIONS_MAP = {
        ACTION_SEND_FOR_APPROVAL: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
        ACTION_APPROVE: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
        ACTION_AUTHORIZE: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        ACTION_REVIEW: Permissions.PM_DOWNLOAD_XLSX_FOR_FSP.name,
        ACTION_MARK_READY_FOR_CLOSURE: Permissions.PM_CLOSE_FINISHED.name,
        ACTION_SEND_BACK_TO_FINISHED: Permissions.PM_MARK_READY_FOR_CLOSURE.name,
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
        ACTION_MARK_READY_FOR_CLOSURE: {
            "action_name": "marked as ready for closure",
            "subject": "Payment pending for Closure",
            "recipient_title": "Reviewer",
        },
        ACTION_SEND_BACK_TO_FINISHED: {
            "action_name": "sent back to finished",
            "subject": "Payment sent back to Finished",
            "recipient_title": "Reviewer",
        },
    }

    def __init__(
        self,
        payment_plan: PaymentPlan,
        action: str,
        action_user: User,
        action_date: datetime,
    ) -> None:
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
        self.emails = self._prepare_emails()
        self.enable_email_notification = self.payment_plan.business_area.enable_email_notification

    def _prepare_user_recipients(self) -> QuerySet[User]:
        permission = PaymentNotification.ACTION_TO_RECIPIENTS_PERMISSIONS_MAP[self.action]
        return users_with_permissions(
            self.payment_plan.business_area,
            [permission],
            [self.payment_plan.program],
            exclude_staff=True,
        ).exclude(id=self.action_user.id)

    def _prepare_emails(self) -> list[MailjetClient]:
        recipients_by_timezone: dict[str, list[str]] = defaultdict(list)
        for user_recipient in self.user_recipients:
            timezone_name = resolve_timezone_name(
                user=user_recipient,
                business_area=self.payment_plan.business_area,
            )
            recipients_by_timezone[timezone_name].append(user_recipient.email)

        action_user_timezone = resolve_timezone_name(
            user=self.action_user,
            business_area=self.payment_plan.business_area,
        )
        emails = [
            MailjetClient(
                mailjet_template_id=config.MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION,
                subject=self.email_subject,
                recipients=recipients,
                ccs=[self.action_user.email] if timezone_name == action_user_timezone else [],
                variables=self._prepare_body_variables(timezone_name),
            )
            for timezone_name, recipients in recipients_by_timezone.items()
        ]
        if emails:
            if action_user_timezone not in recipients_by_timezone:
                emails.append(
                    MailjetClient(
                        mailjet_template_id=config.MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION,
                        subject=self.email_subject,
                        recipients=[self.action_user.email],
                        variables=self._prepare_body_variables(action_user_timezone),
                    )
                )
            return emails

        return [
            MailjetClient(
                mailjet_template_id=config.MAILJET_TEMPLATE_PAYMENT_PLAN_NOTIFICATION,
                subject=self.email_subject,
                recipients=[self.action_user.email],
                variables=self._prepare_body_variables(action_user_timezone),
            )
        ]

    def send_email_notification(self) -> None:
        if config.SEND_PAYMENT_PLANS_NOTIFICATION and self.enable_email_notification:
            try:
                for email in self.emails:
                    email.send_email()
            except Exception:  # pragma: no cover
                logger.exception("Failed to send payment plan notification")

    def _prepare_body_variables(self, timezone_name: str) -> dict[str, str | None]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        return {
            "first_name": "Payment Plan",
            "last_name": self.recipient_title,
            "action_name": self.action_name,
            "payment_plan_url": (
                f"{protocol}://{settings.FRONTEND_HOST}/{self.payment_plan.business_area.slug}/programs/"
                f"{self.payment_plan.program.code}/payment-module/payment-plans/"
                f"{self.payment_plan.id}"
            ),
            "payment_plan_id": self.payment_plan.unicef_id,
            "payment_plan_creator": self.payment_plan_creator.get_full_name()
            if self.payment_plan_creator
            else "Unknown",
            "payment_plan_creation_date": format_human_datetime(
                self.payment_plan_creation_date,
                timezone_name=timezone_name,
            ),
            "action_user": self.action_user.get_full_name(),
            "action_date": format_human_datetime(
                self.action_date,
                timezone_name=timezone_name,
            ),
            "program_name": self.payment_plan.program.name,
        }
