import logging
from enum import auto
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from constance import config

from hct_mis_api.apps.account.models import User, UserRole
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.utils.mailjet import MailjetClient

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from django.db.models import QuerySet


class GrievanceNotification:
    ACTION_ASSIGNMENT_CHANGED = auto()
    ACTION_SYSTEM_FLAGGING_CREATED = auto()
    ACTION_DEDUPLICATION_CREATED = auto()
    ACTION_PAYMENT_VERIFICATION_CREATED = auto()
    ACTION_NOTES_ADDED = auto()
    ACTION_SEND_BACK_TO_IN_PROGRESS = auto()
    ACTION_SENSITIVE_CREATED = auto()
    ACTION_SENSITIVE_REMINDER = auto()
    ACTION_OVERDUE = auto()
    ACTION_SEND_TO_APPROVAL = auto()

    def __init__(self, grievance_ticket: GrievanceTicket, action: auto, **kwargs: Any) -> None:
        self.grievance_ticket = grievance_ticket
        self.action = action
        self.extra_data = kwargs
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()
        self.enable_email_notification = grievance_ticket.business_area.enable_email_notification

    def _prepare_default_context(self, user_recipient: "User") -> Dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        context = {
            "first_name": user_recipient.first_name,
            "last_name": user_recipient.last_name,
            "ticket_url": f'{protocol}://{settings.FRONTEND_HOST}/{self.grievance_ticket.business_area.slug}/programs/all/grievance/tickets/{self.grievance_ticket.grievance_type_to_string()}-generated/{encode_id_base64(self.grievance_ticket.id, "GrievanceTicket")}',
            "ticket_id": self.grievance_ticket.unicef_id,
            "ticket_category": self.grievance_ticket.get_category_display(),
            "title": "Grievance and feedback notification",
        }
        return context

    def _prepare_user_recipients(self) -> Any:
        func: Callable = GrievanceNotification.ACTION_PREPARE_USER_RECIPIENTS_DICT[self.action]
        return func(self)

    def _prepare_emails(self) -> List[MailjetClient]:
        return [self._prepare_email(user) for user in self.user_recipients]

    def _prepare_email(self, user_recipient: "User") -> MailjetClient:
        prepare_bodies_method = GrievanceNotification.ACTION_PREPARE_BODIES_DICT[self.action]
        text_body, html_body, subject = prepare_bodies_method(self, user_recipient)
        email = MailjetClient(
            subject=subject,
            recipients=[user_recipient.email],
            html_body=html_body,
            text_body=text_body,
        )
        return email

    def send_email_notification(self) -> None:
        if config.SEND_GRIEVANCES_NOTIFICATION and self.enable_email_notification:
            try:
                for email in self.emails:
                    email.send_email()
            except Exception as e:  # pragma: no cover
                logger.exception(e)

    def _prepare_universal_category_created_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("universal_category_created_notification_email.txt", context=context)
        html_body = render_to_string("universal_category_created_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"A Grievance & Feedback ticket for {self.grievance_ticket.get_category_display()}",
        )

    def _prepare_universal_category_created_recipients(self) -> "QuerySet":
        action_roles_dict = {
            GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED: "Adjudicator",
            GrievanceNotification.ACTION_DEDUPLICATION_CREATED: "Adjudicator",
            GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED: "Releaser",
            GrievanceNotification.ACTION_SENSITIVE_CREATED: "Senior Management",
        }
        user_roles = UserRole.objects.filter(
            role__name=action_roles_dict[self.action],
            business_area=self.grievance_ticket.business_area,
        ).exclude(expiry_date__lt=timezone.now())
        queryset = User.objects.filter(user_roles__in=user_roles).distinct()
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_for_approval_recipients(self) -> "QuerySet[User]":
        user_roles = UserRole.objects.filter(
            role__name="Approver",
            business_area=self.grievance_ticket.business_area,
        ).exclude(expiry_date__lt=timezone.now())
        queryset = User.objects.filter(user_roles__in=user_roles).distinct()
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_sensitive_reminder_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["hours_ago"] = (timezone.now() - self.grievance_ticket.created_at).days * 24
        text_body = render_to_string("sensitive_reminder_notification_email.txt", context=context)
        html_body = render_to_string("sensitive_reminder_notification_email.html", context=context)
        return text_body, html_body, f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}"

    def _prepare_overdue_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["days_ago"] = (timezone.now() - self.grievance_ticket.created_at).days
        text_body = render_to_string("overdue_notification_email.txt", context=context)
        html_body = render_to_string("overdue_notification_email.html", context=context)
        return text_body, html_body, f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}"

    def _prepare_add_note_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        created_by = self.extra_data.get("created_by")
        context["created_by"] = f"{created_by.first_name} {created_by.last_name}"
        context["ticket_note"] = self.extra_data.get("ticket_note")
        text_body = render_to_string("note_added_notification_email.txt", context=context)
        html_body = render_to_string("note_added_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"New note in Grievance & Feedback ticket has been left {self.grievance_ticket.unicef_id}",
        )

    def _prepare_send_back_to_in_progress_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        approver = self.extra_data.get("approver")
        context["approver"] = f"{approver.first_name} {approver.last_name}"
        text_body = render_to_string("send_back_to_in_progress_notification_email.txt", context=context)
        html_body = render_to_string("send_back_to_in_progress_notification_email.html", context=context)
        return text_body, html_body, f"Review of Grievance & Feedback ticket {self.grievance_ticket.unicef_id}"

    def _prepare_for_approval_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("send_for_approve_notification_email.txt", context=context)
        html_body = render_to_string("send_for_approve_notification_email.html", context=context)
        return text_body, html_body, f"Grievance ticket requiring approval {self.grievance_ticket.unicef_id}"

    def _prepare_assignment_changed_bodies(self, user_recipient: "User") -> Tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("assignment_change_notification_email.txt", context=context)
        html_body = render_to_string("assignment_change_notification_email.html", context=context)
        return text_body, html_body, f"Grievance & Feedback ticket assigned {self.grievance_ticket.id}"

    def _prepare_assigned_to_recipient(self) -> "Optional[List[User]]":
        if self.grievance_ticket.assigned_to is None:
            return []
        return [self.grievance_ticket.assigned_to]

    ACTION_PREPARE_BODIES_DICT = {
        ACTION_ASSIGNMENT_CHANGED: _prepare_assignment_changed_bodies,
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_universal_category_created_bodies,
        ACTION_DEDUPLICATION_CREATED: _prepare_universal_category_created_bodies,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_universal_category_created_bodies,
        ACTION_SENSITIVE_CREATED: _prepare_universal_category_created_bodies,
        ACTION_SEND_BACK_TO_IN_PROGRESS: _prepare_send_back_to_in_progress_bodies,
        ACTION_SEND_TO_APPROVAL: _prepare_for_approval_bodies,
        ACTION_NOTES_ADDED: _prepare_add_note_bodies,
        ACTION_OVERDUE: _prepare_overdue_bodies,
        ACTION_SENSITIVE_REMINDER: _prepare_sensitive_reminder_bodies,
    }

    ACTION_PREPARE_USER_RECIPIENTS_DICT: Dict[int, Callable] = {
        ACTION_ASSIGNMENT_CHANGED: _prepare_assigned_to_recipient,
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_universal_category_created_recipients,
        ACTION_DEDUPLICATION_CREATED: _prepare_universal_category_created_recipients,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_universal_category_created_recipients,
        ACTION_SENSITIVE_CREATED: _prepare_universal_category_created_recipients,
        ACTION_SEND_BACK_TO_IN_PROGRESS: _prepare_assigned_to_recipient,
        ACTION_OVERDUE: _prepare_assigned_to_recipient,
        ACTION_SEND_TO_APPROVAL: _prepare_for_approval_recipients,
        ACTION_NOTES_ADDED: _prepare_assigned_to_recipient,
        ACTION_SENSITIVE_REMINDER: _prepare_assigned_to_recipient,
    }

    @classmethod
    def prepare_notification_for_ticket_creation(
        cls: "GrievanceNotification", grievance_ticket: GrievanceTicket
    ) -> List["GrievanceNotification"]:
        notifications = []
        if grievance_ticket.assigned_to:
            notifications.append(
                GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)
            )
        category_action_dict = {
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED,
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: GrievanceNotification.ACTION_DEDUPLICATION_CREATED,
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: GrievanceNotification.ACTION_SENSITIVE_CREATED,
        }
        action = category_action_dict.get(grievance_ticket.category)
        if action:
            notifications.append(GrievanceNotification(grievance_ticket, action))

        return notifications

    @classmethod
    def send_all_notifications(cls, notifications: List) -> None:
        for notification in notifications:
            notification.send_email_notification()
