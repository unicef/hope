from enum import auto
import logging
from typing import TYPE_CHECKING, Any, Callable

from constance import config
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from hope.apps.core.notifications.publishers import (
    BaseRenderedEmailNotificationService,
    RenderedEmailNotification,
    publish_rendered_email_notification,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.utils.mailjet import MailjetClient
from hope.models import RoleAssignment, User

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class GrievanceAssignmentChangedEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "assignment_change_notification_email.html"
    text_template = "assignment_change_notification_email.txt"


class GrievanceUniversalCategoryCreatedEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "universal_category_created_notification_email.html"
    text_template = "universal_category_created_notification_email.txt"


class GrievanceSendBackToInProgressEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "send_back_to_in_progress_notification_email.html"
    text_template = "send_back_to_in_progress_notification_email.txt"


class GrievanceSendForApprovalEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "send_for_approve_notification_email.html"
    text_template = "send_for_approve_notification_email.txt"


class GrievanceNoteAddedEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "note_added_notification_email.html"
    text_template = "note_added_notification_email.txt"


class GrievanceOverdueEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "overdue_notification_email.html"
    text_template = "overdue_notification_email.txt"


class GrievanceSensitiveReminderEmailNotificationService(BaseRenderedEmailNotificationService):
    html_template = "sensitive_reminder_notification_email.html"
    text_template = "sensitive_reminder_notification_email.txt"


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

    def __init__(self, grievance_ticket: GrievanceTicket, action: Any, **kwargs: Any) -> None:
        self.grievance_ticket = grievance_ticket
        self.action = action
        self.extra_data = kwargs
        self.user_recipients = self._prepare_user_recipients()
        self.emails, self.rendered_email_notifications = self._prepare_emails()
        self.enable_email_notification = grievance_ticket.business_area.enable_email_notification

    def _prepare_default_context(self, user_recipient: "User") -> dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        return {
            "first_name": user_recipient.first_name or getattr(user_recipient, "username", ""),
            "last_name": user_recipient.last_name,
            "ticket_url": f"{protocol}://{settings.FRONTEND_HOST}/{self.grievance_ticket.business_area.slug}/programs/all/grievance/tickets/{self.grievance_ticket.grievance_type_to_string()}-generated/{self.grievance_ticket.id}",
            "ticket_id": self.grievance_ticket.unicef_id,
            "ticket_category": self.grievance_ticket.get_category_display(),
            "title": "Grievance and feedback notification",
        }

    def _prepare_user_recipients(self) -> Any:
        func: Callable = GrievanceNotification.ACTION_PREPARE_USER_RECIPIENTS_DICT[self.action]
        return func(self)

    def _prepare_emails(self) -> tuple[list[MailjetClient], list[RenderedEmailNotification]]:
        emails = []
        rendered_email_notifications = []
        if not self.user_recipients:
            return emails, rendered_email_notifications
        for user in self.user_recipients:
            email, rendered_email_notification = self._prepare_email(user)
            emails.append(email)
            rendered_email_notifications.append(rendered_email_notification)
        return emails, rendered_email_notifications

    def _prepare_email(self, user_recipient: "User") -> tuple[MailjetClient, RenderedEmailNotification]:
        text_body, html_body, subject, context = self._prepare_rendered_email_data(user_recipient)
        email = MailjetClient(
            subject=subject,
            recipients=[user_recipient.email],
            html_body=html_body,
            text_body=text_body,
        )
        notification_service = self._prepare_rendered_email_notification_service()
        return email, RenderedEmailNotification(
            service=notification_service,
            user=user_recipient,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            context=context,
        )

    def send_email_notification(self) -> None:
        if config.SEND_GRIEVANCES_NOTIFICATION and self.enable_email_notification:
            try:
                for email, rendered_email_notification in zip(
                    self.emails, self.rendered_email_notifications, strict=True
                ):
                    email.send_email()
                    publish_rendered_email_notification(rendered_email_notification)
            except Exception as e:
                logger.exception(e)

    def _prepare_rendered_email_notification_service(self) -> BaseRenderedEmailNotificationService:
        service_cls = GrievanceNotification.ACTION_RENDERED_EMAIL_SERVICE_DICT[self.action]
        return service_cls()

    def _prepare_rendered_email_data(self, user_recipient: "User") -> tuple[str, str, str, dict[str, Any]]:
        prepare_context_method = GrievanceNotification.ACTION_PREPARE_CONTEXT_DICT[self.action]
        prepare_subject_method = GrievanceNotification.ACTION_PREPARE_SUBJECT_DICT[self.action]
        notification_service = self._prepare_rendered_email_notification_service()
        context = prepare_context_method(self, user_recipient)
        text_body = render_to_string(notification_service.text_template, context=context)
        html_body = render_to_string(notification_service.html_template, context=context)
        return text_body, html_body, prepare_subject_method(self), context

    def _prepare_universal_category_created_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_universal_category_created_recipients(self) -> "QuerySet":
        action_roles_dict = {
            GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED: "Adjudicator",
            GrievanceNotification.ACTION_DEDUPLICATION_CREATED: "Adjudicator",
            GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED: "Releaser",
            GrievanceNotification.ACTION_SENSITIVE_CREATED: "Senior Management",
        }
        user_roles = RoleAssignment.objects.filter(
            role__name=action_roles_dict[self.action],
            business_area=self.grievance_ticket.business_area,
        ).exclude(expiry_date__lt=timezone.now())
        queryset = User.objects.filter(role_assignments__in=user_roles).distinct()
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_for_approval_recipients(self) -> "QuerySet[User]":
        user_roles = RoleAssignment.objects.filter(
            role__name="Approver",
            business_area=self.grievance_ticket.business_area,
        ).exclude(expiry_date__lt=timezone.now())
        queryset = User.objects.filter(role_assignments__in=user_roles).distinct()
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_sensitive_reminder_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_overdue_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_add_note_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_send_back_to_in_progress_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_for_approval_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        notification_service = GrievanceSendForApprovalEmailNotificationService()
        text_body = render_to_string(notification_service.text_template, context=context)
        html_body = render_to_string(notification_service.html_template, context=context)
        subject = self._prepare_for_approval_subject()
        return text_body, html_body, subject

    def _prepare_assignment_changed_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        text_body, html_body, subject, _context = self._prepare_rendered_email_data(user_recipient)
        return text_body, html_body, subject

    def _prepare_default_rendered_email_context(self, user_recipient: "User") -> dict[str, Any]:
        return self._prepare_default_context(user_recipient)

    def _prepare_sensitive_reminder_context(self, user_recipient: "User") -> dict[str, Any]:
        context = self._prepare_default_context(user_recipient)
        context["hours_ago"] = (timezone.now() - self.grievance_ticket.created_at).days * 24
        return context

    def _prepare_overdue_context(self, user_recipient: "User") -> dict[str, Any]:
        context = self._prepare_default_context(user_recipient)
        context["days_ago"] = (timezone.now() - self.grievance_ticket.created_at).days
        return context

    def _prepare_add_note_context(self, user_recipient: "User") -> dict[str, Any]:
        context = self._prepare_default_context(user_recipient)
        created_by = self.extra_data.get("created_by")
        ticket_note = self.extra_data.get("ticket_note")
        context["created_by"] = f"{created_by.first_name} {created_by.last_name}"
        context["ticket_note_description"] = ticket_note.description
        return context

    def _prepare_send_back_to_in_progress_context(self, user_recipient: "User") -> dict[str, Any]:
        context = self._prepare_default_context(user_recipient)
        approver = self.extra_data.get("approver")
        context["approver"] = f"{approver.first_name} {approver.last_name}"
        return context

    def _prepare_universal_category_created_subject(self) -> str:
        return f"A Grievance & Feedback ticket for {self.grievance_ticket.get_category_display()}"

    def _prepare_sensitive_reminder_subject(self) -> str:
        return f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}"

    def _prepare_overdue_subject(self) -> str:
        return f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}"

    def _prepare_add_note_subject(self) -> str:
        return f"New note in Grievance & Feedback ticket has been left {self.grievance_ticket.unicef_id}"

    def _prepare_send_back_to_in_progress_subject(self) -> str:
        return f"Review of Grievance & Feedback ticket {self.grievance_ticket.unicef_id}"

    def _prepare_for_approval_subject(self) -> str:
        return f"Grievance ticket requiring approval {self.grievance_ticket.unicef_id}"

    def _prepare_assignment_changed_subject(self) -> str:
        return f"Grievance & Feedback ticket assigned {self.grievance_ticket.id}"

    def _prepare_assigned_to_recipient(self) -> "list[User] | None":
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

    ACTION_PREPARE_CONTEXT_DICT = {
        ACTION_ASSIGNMENT_CHANGED: _prepare_default_rendered_email_context,
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_default_rendered_email_context,
        ACTION_DEDUPLICATION_CREATED: _prepare_default_rendered_email_context,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_default_rendered_email_context,
        ACTION_SENSITIVE_CREATED: _prepare_default_rendered_email_context,
        ACTION_SEND_BACK_TO_IN_PROGRESS: _prepare_send_back_to_in_progress_context,
        ACTION_SEND_TO_APPROVAL: _prepare_default_rendered_email_context,
        ACTION_NOTES_ADDED: _prepare_add_note_context,
        ACTION_OVERDUE: _prepare_overdue_context,
        ACTION_SENSITIVE_REMINDER: _prepare_sensitive_reminder_context,
    }

    ACTION_PREPARE_SUBJECT_DICT = {
        ACTION_ASSIGNMENT_CHANGED: _prepare_assignment_changed_subject,
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_universal_category_created_subject,
        ACTION_DEDUPLICATION_CREATED: _prepare_universal_category_created_subject,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_universal_category_created_subject,
        ACTION_SENSITIVE_CREATED: _prepare_universal_category_created_subject,
        ACTION_SEND_BACK_TO_IN_PROGRESS: _prepare_send_back_to_in_progress_subject,
        ACTION_SEND_TO_APPROVAL: _prepare_for_approval_subject,
        ACTION_NOTES_ADDED: _prepare_add_note_subject,
        ACTION_OVERDUE: _prepare_overdue_subject,
        ACTION_SENSITIVE_REMINDER: _prepare_sensitive_reminder_subject,
    }

    ACTION_RENDERED_EMAIL_SERVICE_DICT = {
        ACTION_ASSIGNMENT_CHANGED: GrievanceAssignmentChangedEmailNotificationService,
        ACTION_SYSTEM_FLAGGING_CREATED: GrievanceUniversalCategoryCreatedEmailNotificationService,
        ACTION_DEDUPLICATION_CREATED: GrievanceUniversalCategoryCreatedEmailNotificationService,
        ACTION_PAYMENT_VERIFICATION_CREATED: GrievanceUniversalCategoryCreatedEmailNotificationService,
        ACTION_SENSITIVE_CREATED: GrievanceUniversalCategoryCreatedEmailNotificationService,
        ACTION_SEND_BACK_TO_IN_PROGRESS: GrievanceSendBackToInProgressEmailNotificationService,
        ACTION_SEND_TO_APPROVAL: GrievanceSendForApprovalEmailNotificationService,
        ACTION_NOTES_ADDED: GrievanceNoteAddedEmailNotificationService,
        ACTION_OVERDUE: GrievanceOverdueEmailNotificationService,
        ACTION_SENSITIVE_REMINDER: GrievanceSensitiveReminderEmailNotificationService,
    }

    ACTION_PREPARE_USER_RECIPIENTS_DICT: dict[Any, Callable[..., Any]] = {
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
    ) -> list["GrievanceNotification"]:
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
    def send_all_notifications(cls, notifications: list) -> None:
        for notification in notifications:
            notification.send_email_notification()
