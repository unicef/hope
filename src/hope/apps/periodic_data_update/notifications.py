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
from hope.models import PDUOnlineEdit, User

logger = logging.getLogger(__name__)


class PDUOnlineEditNotification:
    ACTION_SEND_FOR_APPROVAL = "SEND_FOR_APPROVAL"
    ACTION_APPROVE = "APPROVE"
    ACTION_SEND_BACK = "SEND_BACK"

    ACTION_TO_RECIPIENTS_PERMISSIONS_MAP = {
        ACTION_SEND_FOR_APPROVAL: Permissions.PDU_ONLINE_APPROVE.name,
        ACTION_APPROVE: Permissions.PDU_ONLINE_MERGE.name,
        ACTION_SEND_BACK: Permissions.PDU_ONLINE_SAVE_DATA.name,
    }

    ACTION_PREPARE_EMAIL_BODIES_MAP = {
        ACTION_SEND_FOR_APPROVAL: {
            "action_name": "sent for approval",
            "subject": "PDU Online Edit pending for Approval",
            "recipient_title": "Approver",
        },
        ACTION_APPROVE: {
            "action_name": "approved",
            "subject": "PDU Online Edit pending for Merge",
            "recipient_title": "Merger",
        },
        ACTION_SEND_BACK: {
            "action_name": "sent back",
            "subject": "PDU Online Edit sent back",
            "recipient_title": "Editor",
        },
    }

    def __init__(
        self,
        pdu_online_edit: PDUOnlineEdit,
        action: str,
        action_user: User,
        action_date: datetime,
    ) -> None:
        self.pdu_online_edit = pdu_online_edit
        self.action = action
        self.action_user = action_user
        self.action_date = action_date
        self.pdu_creator = self.pdu_online_edit.created_by
        self.pdu_creation_date = self.pdu_online_edit.created_at
        self.email_subject = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["subject"]
        self.action_name = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["action_name"]
        self.recipient_title = self.ACTION_PREPARE_EMAIL_BODIES_MAP[self.action]["recipient_title"]
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()
        self.enable_email_notification = self.pdu_online_edit.business_area.enable_email_notification

    def _prepare_user_recipients(self) -> QuerySet[User]:
        permission = self.ACTION_TO_RECIPIENTS_PERMISSIONS_MAP[self.action]

        # Get authorized users for this PDU Edit
        authorized_user_ids = list(self.pdu_online_edit.authorized_users.values_list("id", flat=True))

        if not authorized_user_ids:
            return User.objects.none()

        return (
            users_with_permissions(
                self.pdu_online_edit.business_area,
                [permission],
                [self.pdu_online_edit.program],
            )
            .filter(id__in=authorized_user_ids)  # Only authorized users
            .exclude(id=self.action_user.id)
        )

    def _prepare_emails(self) -> list[MailjetClient]:
        recipients_by_timezone: dict[str, list[str]] = defaultdict(list)
        for user_recipient in self.user_recipients:
            timezone_name = resolve_timezone_name(
                user=user_recipient,
                business_area=self.pdu_online_edit.business_area,
            )
            recipients_by_timezone[timezone_name].append(user_recipient.email)

        action_user_timezone = resolve_timezone_name(
            user=self.action_user,
            business_area=self.pdu_online_edit.business_area,
        )
        emails = [
            MailjetClient(
                mailjet_template_id=config.MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION,
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
                        mailjet_template_id=config.MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION,
                        subject=self.email_subject,
                        recipients=[self.action_user.email],
                        variables=self._prepare_body_variables(action_user_timezone),
                    )
                )
            return emails

        return [
            MailjetClient(
                mailjet_template_id=config.MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION,
                subject=self.email_subject,
                recipients=[],
                ccs=[self.action_user.email],
                variables=self._prepare_body_variables(action_user_timezone),
            )
        ]

    def send_email_notification(self) -> None:
        if config.SEND_PDU_ONLINE_EDIT_NOTIFICATION and self.enable_email_notification:
            try:
                for email in self.emails:
                    email.send_email()
            except Exception:  # pragma: no cover
                logger.exception("Failed to send PDU Online Edit notification")

    def _prepare_body_variables(self, timezone_name: str) -> dict[str, str | int]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"

        return {
            "first_name": "PDU Online Edit",
            "last_name": self.recipient_title,
            "action_name": self.action_name,
            "pdu_online_edit_url": (
                f"{protocol}://{settings.FRONTEND_HOST}/{self.pdu_online_edit.business_area.slug}/programs/"
                f"{self.pdu_online_edit.program.code}/population/individuals/online-templates/{self.pdu_online_edit.id}"
            ),
            "pdu_online_edit_id": self.pdu_online_edit.id,
            "pdu_online_edit_name": self.pdu_online_edit.name or "",
            "pdu_creator": self.pdu_creator.get_full_name() if self.pdu_creator else "Unknown",
            "pdu_creation_date": format_human_datetime(
                self.pdu_creation_date,
                timezone_name=timezone_name,
            ),
            "action_user": self.action_user.get_full_name(),
            "action_date": format_human_datetime(
                self.action_date,
                timezone_name=timezone_name,
            ),
            "program_name": self.pdu_online_edit.program.name,
        }
