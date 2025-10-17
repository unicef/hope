from django.db import models
from django.utils.translation import gettext_lazy as _


class FlexFieldClassification(models.TextChoices):
    NOT_FLEX_FIELD = "NOT_FLEX_FIELD", _("Not Flex Field")
    FLEX_FIELD_BASIC = "FLEX_FIELD_BASIC", _("Flex Field Basic")
    FLEX_FIELD_PDU = "FLEX_FIELD_PDU", _("Flex Field PDU")
