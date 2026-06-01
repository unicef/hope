from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class SurprisePageConfig(models.Model):
    image = models.ImageField(upload_to="surprise/", blank=True, help_text=_("Photo displayed on the surprise page"))
    heading = models.CharField(
        max_length=255,
        blank=True,
        default="🎉 You found a secret!",
        help_text=_("Main heading shown on the surprise page"),
    )
    subheading = models.CharField(
        max_length=255,
        blank=True,
        default="Congratulations, explorer.",
        help_text=_("Subtitle shown below the heading"),
    )

    class Meta:
        app_label = "core"
        verbose_name = "Special Page Configuration"
        verbose_name_plural = "Special Page Configuration"

    def __str__(self) -> str:
        return "Special Page Configuration"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> None:
        pass
