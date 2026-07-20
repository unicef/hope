from enum import auto
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any, Callable

from constance import config
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.utils.mailjet import MailjetClient
from hope.models import RoleAssignment, User

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


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
    ACTION_TICKET_UPDATED = auto()

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

    def __init__(self, grievance_ticket: GrievanceTicket, action: Any, **kwargs: Any) -> None:
        self.grievance_ticket = grievance_ticket
        self.action = action
        self.extra_data = kwargs
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()
        self.enable_email_notification = grievance_ticket.business_area.enable_email_notification

    def _prepare_default_context(self, user_recipient: "User") -> dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
        # sensitive grievance shouldn't contain any urls
        is_sensitive = self.grievance_ticket.category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE
        ticket_url = (
            None
            if is_sensitive
            else f"{protocol}://{settings.FRONTEND_HOST}/{self.grievance_ticket.business_area.slug}/programs/all/grievance/tickets/{self.grievance_ticket.grievance_type_to_string()}-generated/{self.grievance_ticket.id}"
        )
        return {
            "first_name": user_recipient.first_name or getattr(user_recipient, "username", ""),
            "last_name": user_recipient.last_name,
            "ticket_url": ticket_url,
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

    def _prepare_universal_category_created_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("universal_category_created_notification_email.txt", context=context)
        html_body = render_to_string("universal_category_created_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"A Grievance & Feedback ticket for {self.grievance_ticket.get_category_display()}",
        )

    @staticmethod
    def _exclude_unmailable(queryset: "QuerySet[User]") -> "QuerySet[User]":
        return queryset.filter(is_active=True).exclude(email="")

    @cached_property
    def _program_scope(self) -> Q:
        program_ids = list(self.grievance_ticket.programs.values_list("pk", flat=True))
        return Q() if not program_ids else Q(program__isnull=True) | Q(program__in=program_ids)

    def _users_with_permissions(self, permissions: list[Permissions]) -> "QuerySet[User]":
        perm_values = [permission.value for permission in permissions]
        role_assignments = (
            RoleAssignment.objects.filter(
                self._program_scope,
                role__permissions__overlap=perm_values,
                business_area=self.grievance_ticket.business_area,
            )
            .exclude(expiry_date__lt=timezone.now())
            .distinct()
        )
        return self._exclude_unmailable(
            User.objects.filter(
                Q(role_assignments__in=role_assignments) | Q(partner__role_assignments__in=role_assignments)
            )
        ).distinct()

    def _prepare_permission_based_recipients(self) -> "QuerySet[User]":
        queryset = self._users_with_permissions(GrievanceNotification.ACTION_VIEW_PERMISSIONS[self.action])
        if self.action == GrievanceNotification.ACTION_PAYMENT_VERIFICATION_CREATED:
            # A recipient must additionally hold a payment-verification view permission.
            payment_users = self._users_with_permissions(
                [Permissions.PAYMENT_VERIFICATION_VIEW_LIST, Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS]
            )
            queryset = queryset.filter(pk__in=payment_users.values("pk"))
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_creator_and_assignee_recipients(self) -> "list[User]":
        editor = self.extra_data.get("editor")
        recipients = {}
        for user in (self.grievance_ticket.created_by, self.grievance_ticket.assigned_to):
            if user is None:
                continue
            if not user.is_active or not user.email:
                continue
            if editor is not None and user.id == editor.id:
                continue
            recipients[user.id] = user
        return list(recipients.values())

    def _prepare_for_approval_recipients(self) -> "QuerySet[User]":
        # Approval permission depends on the ticket type, mirroring the approve_* actions on the viewset.
        approve_permissions_by_category = {
            GrievanceTicket.CATEGORY_DATA_CHANGE: (
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            ),
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: (
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            ),
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: (
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            ),
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: (
                Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
                Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
            ),
        }
        permissions = approve_permissions_by_category.get(self.grievance_ticket.category)
        if permissions is None:
            return User.objects.none()
        base_permission, creator_permission = permissions
        # Base-permission holders, plus the creator when they hold the creator-scoped approve permission.
        creator_id = self.grievance_ticket.created_by_id
        queryset = User.objects.filter(
            Q(pk__in=self._users_with_permissions([base_permission]).values("pk"))
            | (Q(pk=creator_id) & Q(pk__in=self._users_with_permissions([creator_permission]).values("pk")))
        )
        # Never notify the user who sent the ticket for approval about their own action.
        editor = self.extra_data.get("editor")
        if editor is not None:
            queryset = queryset.exclude(id=editor.id)
        if self.grievance_ticket.assigned_to:
            queryset = queryset.exclude(id=self.grievance_ticket.assigned_to.id)
        return queryset.all()

    def _prepare_sensitive_reminder_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["hours_ago"] = (timezone.now() - self.grievance_ticket.created_at).days * 24
        text_body = render_to_string("sensitive_reminder_notification_email.txt", context=context)
        html_body = render_to_string("sensitive_reminder_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"Overdue Grievance ticket requiring attention {self.grievance_ticket.unicef_id}",
        )

    def _prepare_overdue_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        context["days_ago"] = (timezone.now() - self.grievance_ticket.created_at).days
        text_body = render_to_string("overdue_notification_email.txt", context=context)
        html_body = render_to_string("overdue_notification_email.html", context=context)
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
        text_body = render_to_string("note_added_notification_email.txt", context=context)
        html_body = render_to_string("note_added_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"New note in Grievance & Feedback ticket has been left {self.grievance_ticket.unicef_id}",
        )

    def _prepare_send_back_to_in_progress_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        approver = self.extra_data.get("approver")
        context["approver"] = f"{approver.first_name} {approver.last_name}"
        text_body = render_to_string("send_back_to_in_progress_notification_email.txt", context=context)
        html_body = render_to_string("send_back_to_in_progress_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"Review of Grievance & Feedback ticket {self.grievance_ticket.unicef_id}",
        )

    def _prepare_for_approval_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("send_for_approve_notification_email.txt", context=context)
        html_body = render_to_string("send_for_approve_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"Grievance ticket requiring approval {self.grievance_ticket.unicef_id}",
        )

    def _prepare_assignment_changed_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("assignment_change_notification_email.txt", context=context)
        html_body = render_to_string("assignment_change_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"Grievance & Feedback ticket assigned {self.grievance_ticket.id}",
        )

    def _prepare_ticket_updated_bodies(self, user_recipient: "User") -> tuple[str, str, str]:
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("ticket_updated_notification_email.txt", context=context)
        html_body = render_to_string("ticket_updated_notification_email.html", context=context)
        return (
            text_body,
            html_body,
            f"Changes made on Grievance & Feedback ticket {self.grievance_ticket.unicef_id}",
        )

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
        ACTION_TICKET_UPDATED: _prepare_ticket_updated_bodies,
    }

    ACTION_PREPARE_USER_RECIPIENTS_DICT: dict[Any, Callable[..., Any]] = {
        ACTION_ASSIGNMENT_CHANGED: _prepare_assigned_to_recipient,
        ACTION_SYSTEM_FLAGGING_CREATED: _prepare_permission_based_recipients,
        ACTION_DEDUPLICATION_CREATED: _prepare_permission_based_recipients,
        ACTION_PAYMENT_VERIFICATION_CREATED: _prepare_permission_based_recipients,
        ACTION_SENSITIVE_CREATED: _prepare_permission_based_recipients,
        ACTION_SEND_BACK_TO_IN_PROGRESS: _prepare_assigned_to_recipient,
        ACTION_OVERDUE: _prepare_assigned_to_recipient,
        ACTION_SEND_TO_APPROVAL: _prepare_for_approval_recipients,
        ACTION_NOTES_ADDED: _prepare_assigned_to_recipient,
        ACTION_SENSITIVE_REMINDER: _prepare_assigned_to_recipient,
        ACTION_TICKET_UPDATED: _prepare_creator_and_assignee_recipients,
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
