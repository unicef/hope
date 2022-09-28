from django.db import models
from django.utils.translation import gettext_lazy as _


class RejectPolicy(models.TextChoices):
    STRICT = "STRICT", _("STRICT")
    LAX = "LAX", _("Lax")
