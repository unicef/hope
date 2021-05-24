from enum import auto

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from hct_mis_api.apps.core.utils import encode_id_base64


class GrievanceNotification:
    ACTION_ASSIGNMENT_CHANGED = auto()
    ACTION_STATUS_CHANGED = auto()

    def __init__(self, grievance_ticket, action):
        self.grievance_ticket = grievance_ticket
        self.action = action
        self.user_recipients = self._prepare_user_recipients()
        self.emails = self._prepare_emails()

    def _prepare_default_context(self, user_recipient):
        protocol = "http" if settings.IS_DEV else "https"
        context = {
            "first_name": user_recipient.first_name,
            "last_name": user_recipient.last_name,
            "report_url": f'{protocol}://{settings.FRONTEND_HOST}/{self.grievance_ticket.business_area.slug}/grievance-and-feedback/{encode_id_base64(self.grievance_ticket.id, "GrievanceTicketNode")}',
        }
        return context

    def _prepare_assignment_changed_bodies(self, user_recipient):
        context = self._prepare_default_context(user_recipient)
        text_body = render_to_string("assignment_change_notification_email.txt", context=context)
        html_body = render_to_string("assignment_change_notification_email.html", context=context)
        return text_body, html_body

    def _prepare_assignment_changed_user_recipients(self):
        return [self.grievance_ticket.assigned_to]

    def _prepare_user_recipients(self):
        return GrievanceNotification.ACTION_PREPARE_USER_RECIPIENTS_DICT[self.action](self)

    def _prepare_emails(self):
        return [self._prepare_email(user) for user in self.user_recipients]

    def _prepare_email(self, user_recipient):
        prepare_bodies_method = GrievanceNotification.ACTION_PREPARE_BODIES_DICT[self.action]
        text_body, html_body = prepare_bodies_method(self, user_recipient)
        email = EmailMultiAlternatives(
            subject="HOPE report generated",
            from_email=settings.EMAIL_HOST_USER,
            to=[self.grievance_ticket.assigned_to.email],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        return email

    def send_email_notification(self):
        for email in self.emails:
            email.send()

    ACTION_PREPARE_BODIES_DICT = {ACTION_ASSIGNMENT_CHANGED: _prepare_assignment_changed_bodies}

    ACTION_PREPARE_USER_RECIPIENTS_DICT = {ACTION_ASSIGNMENT_CHANGED: _prepare_assignment_changed_user_recipients}
