import logging
from typing import Any

from constance import config
from django.conf import settings
from django.db.models import Q, QuerySet
from django.utils import timezone

from hope.apps.account.models import RoleAssignment, User
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.utils.mailjet import MailjetClient

logger = logging.getLogger(__name__)


class PDUOnlineEditNotification:
    ACTION_SEND_FOR_APPROVAL = "SEND_FOR_APPROVAL"
    ACTION_APPROVE = "APPROVE"
    ACTION_SEND_BACK = "SEND_BACK"

    ACTION_TO_RECIPIENTS_PERMISSIONS_MAP = {
        ACTION_SEND_FOR_APPROVAL: Permissions.PDU_ONLINE_APPROVE.name,
        ACTION_APPROVE: Permissions.PDU_ONLINE_MERGE.name,
        ACTION_SEND_BACK: None,  # Special case - notify the creator
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
            "recipient_title": "Creator",
        },
    }

    def __init__(
        self,
        pdu_online_edit: PDUOnlineEdit,
        action: str,
        action_user: User,
        action_date: str,
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
        self.email = self._prepare_email()
        self.enable_email_notification = self.pdu_online_edit.business_area.enable_email_notification

    def _prepare_user_recipients(self) -> QuerySet[User]:
        if self.action == self.ACTION_SEND_BACK:
            # For send back action, notify the creator
            return User.objects.filter(id=self.pdu_creator.id).exclude(id=self.action_user.id)

        else:
            permission = self.ACTION_TO_RECIPIENTS_PERMISSIONS_MAP[self.action]
            business_area = self.pdu_online_edit.business_area
            program = self.pdu_online_edit.program

            # Get authorized users for this PDU Edit
            authorized_user_ids = list(self.pdu_online_edit.authorized_users.values_list('id', flat=True))

            if not authorized_user_ids:
                return User.objects.none()

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
                .filter(id__in=authorized_user_ids)  # Only authorized users
                .exclude(id=self.action_user.id)
                .distinct()
            )

            if settings.ENV == "prod":
                users = users.exclude(is_superuser=True)
            return users

    def _prepare_email(self) -> MailjetClient:
        body_variables = self._prepare_body_variables()
        return MailjetClient(
            mailjet_template_id=config.MAILJET_TEMPLATE_PDU_ONLINE_EDIT_NOTIFICATION,
            subject=self.email_subject,
            recipients=[user_recipient.email for user_recipient in self.user_recipients],
            ccs=[self.action_user.email],
            variables=body_variables,
        )

    def send_email_notification(self) -> None:
        if config.SEND_PDU_ONLINE_EDIT_NOTIFICATION and self.enable_email_notification:
            try:
                self.email.send_email()
            except Exception as e:  # pragma: no cover
                logger.exception(e)

    def _prepare_body_variables(self) -> dict[str, Any]:
        protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"

        body_vars = {
            "first_name": "PDU Online Edit",
            "last_name": self.recipient_title,
            "action_name": self.action_name,
            "pdu_online_edit_url": (
                f"{protocol}://{settings.FRONTEND_HOST}/{self.pdu_online_edit.business_area.slug}/programs/"
                f"{self.pdu_online_edit.program.id}/population/individuals/online-templates/"
                f"online-edit/{self.pdu_online_edit.id}"
            ),
            "pdu_online_edit_id": self.pdu_online_edit.id,
            "pdu_creator": self.pdu_creator.get_full_name() if self.pdu_creator else "Unknown",
            "pdu_creation_date": f"{self.pdu_creation_date:%-d %B %Y}",
            "action_user": self.action_user.get_full_name(),
            "action_date": self.action_date,
            "program_name": self.pdu_online_edit.program.name,
        }

        # Only add the name variable if the PDU Online Edit has a name
        if self.pdu_online_edit.name:
            body_vars["pdu_online_edit_name"] = self.pdu_online_edit.name

        return body_vars
