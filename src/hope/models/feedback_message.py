from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.feedback import Feedback
from hope.models.utils import TimeStampedUUIDModel


class FeedbackMessage(TimeStampedUUIDModel):
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("The content of the feedback message."),
    )
    feedback = models.ForeignKey(
        Feedback,
        related_name="feedback_messages",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedback_messages",
        blank=True,
        null=True,
        verbose_name=_("Created by"),
    )

    class Meta:
        app_label = "accountability"
        ordering = ("created_at",)
        verbose_name = _("Feedback message")
