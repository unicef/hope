from enum import auto
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any, Callable

from constance import config
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.utils import grievance_ticket_url
from hope.apps.utils.mailjet import MailjetClient
from hope.apps.utils.recipients import is_mailable, users_with_permissions
from hope.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class GrievanceNotification:
    ACTION_SYSTEM_FLAGGING_CREATED = auto()
    ACTION_DEDUPLICATION_CREATED = auto()
    ACTION_PAYMENT_VERIFICATION_CREATED = auto()
    ACTION_NOTES_ADDED = auto()
    ACTION_SEND_BACK_TO_IN_PROGRESS = auto()
    ACTION_SENSITIVE_CREATED = auto()
    ACTION_SENSITIVE_REMINDER = auto()
    ACTION_OVERDUE = auto()
    ACTION_SEND_TO_APPROVAL = auto()

    ACTION_VIEW_PERMISSIONS = {
        ACTION_SENSITIVE_CREATED: [
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
        ],
        ACTION_SYSTEM_FLAGGING_CREATED: [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
        ],
        ACTION_DEDUPLICATION_CREATED: [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
        ],
        ACTION_PAYMENT_VERIFICATION_CREATED: [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
        ],
    }

    # Which permission lets a user act on a ticket waiting for approval, per category.
    CATEGORY_APPROVE_PERMISSIONS = {
        GrievanceTicket.CATEGORY_DATA_CHANGE: (
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: (
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: (
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: (
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: (
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: (
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        ),
        GrievanceTicket.CATEGORY_BENEFICIARY: (
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        ),
        # Referral is a feedback-type ticket, so closing/approving is gated by the feedback permission.
        GrievanceTicket.CATEGORY_REFERRAL: (
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
        ),
    }

    def __init__(self, grievance_ticket: GrievanceTicket, action: Any, **kwargs: Any) -> None:
        self.grievance_ticket = grievance_ticket
        self.action = action
        self.extra_data = kwargs
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()
        self.enable_email_notification = grievance_ticket.business_area.enable_email_notification

    def _prepare_default_context(self, user_recipient: "User") -> dict[str, Any]:
        return {
            "first_name": user_recipient.first_name or getattr(user_recipient, "username", ""),
            "last_name": user_recipient.last_name,
            "ticket_url": grievance_ticket_url(self.grievance_ticket),
            "ticket_id": self.grievance_ticket.unicef_id,
            "ticket_category": self.grievance_ticket.get_category_display(),
            "title": "Grievance and feedback notification",
        }

    def _prepare_user_recipients(self) -> Any:
        func: Callable = GrievanceNotification.ACTION_PREPARE_USER_RECIPIENTS_DICT[self.action]
        return func(self)

    def _prepare_emails(self) -> list[MailjetClient]:
        return [self._prepare_email(user) for user in self.user_recipients]

    def _prepare_email(self, user_recipient: "User") -> MailjetClient:
        prepare_bodies_method = GrievanceNotification.ACTION_PREPARE_BODIES_DICT[self.action]
        text_body, html_body, subject = prepare_bodies_method(self, user_recipient)
        return MailjetClient(
            subject=subject,
            recipients=[user_recipient.email],
            html_body=html_body,
            text_body=text_body,
        )

    def send_email_notification(self) -> None:
        if config.SEND_GRIEVANCES_NOTIFICATION and self.enable_email_notification:
            try:
                for email in self.emails:
                    email.send_email()
            except Exception as e:  # pragma: no cover
                logger.exception(e)

    @staticmethod
    def _render_bodies(template_base: str, context: dict[str, Any]) -> tuple[str, str]:
        return (
            render_to_string(f"{template_base}_notification_email.txt", context=context),
            render_to_string(f"{template_base}_notification_email.html", context=context),
        )

    def _prepare_universal_category_created_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body, html_body = self._render_bodies("universal_category_created", context)
        return (
            text_body,
            html_body,
            f"A Grievance & Feedback ticket for {self.grievance_ticket.get_category_display()}",
        )

    @staticmethod
    def _exclude_users(queryset: "QuerySet[User]", *users: "User | None") -> "QuerySet[User]":
        ids = [user.id for user in users if user is not None]
        return queryset.exclude(id__in=ids) if ids else queryset

    @property
    def _editor(self) -> "User | None":
        # The user who performed the action; never notified about their own action.
        return self.extra_data.get("editor")

    @cached_property
    def _program_ids(self) -> list:
        return list(self.grievance_ticket.programs.values_list("pk", flat=True))

    def _users_with_permissions(self, permissions: list[Permissions]) -> "QuerySet[User]":
        return users_with_permissions(
            self.grievance_ticket.business_area,
            permissions,
            self._program_ids,
            exclude_staff=True,
        )

    def _prepare_permission_based_recipients(self) -> "QuerySet[User]":
        queryset = self._users_with_permissions(GrievanceNotification.ACTION_VIEW_PERMISSIONS[self.action])
        if self.action == GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED:
            # A recipient must additionally hold a payment-verification view permission.
            payment_users = self._users_with_permissions(
                [Permissions.PAYMENT_VERIFICATION_VIEW_LIST, Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS]
            )
            queryset = queryset.filter(pk__in=payment_users.values("pk"))
        # Assignee is notified about the ticket in the daily digest; the editor is the user performing
        # the creation.
        return self._exclude_users(queryset, self.grievance_ticket.assigned_to, self._editor).all()

    def _prepare_for_approval_recipients(self) -> "QuerySet[User]":
        permissions = GrievanceNotification.CATEGORY_APPROVE_PERMISSIONS.get(self.grievance_ticket.category)
        if permissions is None:
            return User.objects.none()
        base_permission, creator_permission, owner_permission = permissions
        # General-permission holders, plus the creator/owner when they hold their scoped approve permission.
        queryset = User.objects.filter(
            Q(pk__in=self._users_with_permissions([base_permission]).values("pk"))
            | (
                Q(pk=self.grievance_ticket.created_by_id)
                & Q(pk__in=self._users_with_permissions([creator_permission]).values("pk"))
            )
            | (
                Q(pk=self.grievance_ticket.assigned_to_id)
                & Q(pk__in=self._users_with_permissions([owner_permission]).values("pk"))
            )
        )
        # Never notify the user who sent the ticket for approval about their own action.
        return self._exclude_users(queryset, self._editor).all()

    def _prepare_sensitive_reminder_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["hours_ago"] = (timezone.now() - self.grievance_ticket.created_at).days * 24
        text_body, html_body = self._render_bodies("sensitive_reminder", context)
        return (
            text_body,
            html_body,
            f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}",
        )

    def _prepare_overdue_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["days_ago"] = (timezone.now() - self.grievance_ticket.created_at).days
        text_body, html_body = self._render_bodies("overdue", context)
        return (
            text_body,
            html_body,
            f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}",
        )

    def _prepare_add_note_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        created_by = self.extra_data.get("created_by")
        context["created_by"] = f"{created_by.first_name} {created_by.last_name}"
        context["ticket_note"] = self.extra_data.get("ticket_note")
        text_body, html_body = self._render_bodies("note_added", context)
        return (
            text_body,
            html_body,
            f"New note in Grievance & Feedback ticket has been left {self.grievance_ticket.unicef_id}",
        )

    def _prepare_send_back_to_in_progress_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        approver = self.extra_data.get("approver")
        context["approver"] = f"{approver.first_name} {approver.last_name}"
        text_body, html_body = self._render_bodies("send_back_to_in_progress", context)
        return (
            text_body,
            html_body,
            f"Review of Grievance & Feedback ticket {self.grievance_ticket.unicef_id}",
        )

    def _prepare_for_approval_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body, html_body = self._render_bodies("send_for_approve", context)
        return (
            text_body,
            html_body,
            f"Grievance ticket requiring approval {self.grievance_ticket.unicef_id}",
        )

    def _prepare_assigned_to_recipient(self) -> "list[User] | None":
        assigned_to = self.grievance_ticket.assigned_to
        if assigned_to is None or not is_mailable(assigned_to):
            return []
        # Never notify the user who performed the action about their own action.
        editor = self._editor
        if editor is not None and assigned_to.id == editor.id:
            return []
        return [assigned_to]

    ACTION_PREPARE_BODIES_DICT = {
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

    ACTION_PREPARE_USER_RECIPIENTS_DICT: dict[Any, Callable[..., Any]] = {
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_permission_based_recipients,
        ACTION_DEDUPLICATION_CREATED: _prepare_permission_based_recipients,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_permission_based_recipients,
        ACTION_SENSITIVE_CREATED: _prepare_permission_based_recipients,
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
        category_action_dict = {
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: GrievanceNotification.ACTION_SYSTEM_FLAGGING_CREATED,
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: GrievanceNotification.ACTION_DEDUPLICATION_CREATED,
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: GrievanceNotification.ACTION_SENSITIVE_CREATED,
        }
        action = category_action_dict.get(grievance_ticket.category)
        if action:
            notifications.append(GrievanceNotification(grievance_ticket, action, editor=grievance_ticket.created_by))

        return notifications

    @classmethod
    def send_all_notifications(cls, notifications: list) -> None:
        for notification in notifications:
            notification.send_email_notification()
