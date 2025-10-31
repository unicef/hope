from django.conf import settings
from django.db import models

from hope.models.pdu_online_edit import PDUOnlineEdit
from hope.models.utils import TimeStampedModel


class PDUOnlineEditSentBackComment(TimeStampedModel):
    pdu_online_edit = models.OneToOneField(
        PDUOnlineEdit,
        on_delete=models.CASCADE,
        related_name="sent_back_comment",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="sent_back_comments",
        null=True,
    )
    comment = models.TextField()

    class Meta:
        app_label = "periodic_data_update"
        ordering = ["-created_at"]
