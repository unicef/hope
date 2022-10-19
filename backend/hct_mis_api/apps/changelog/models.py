from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Changelog(models.Model):

    # Fields
    description = models.TextField(blank=True)
    version = models.CharField(max_length=30, help_text=_("HOPE version"))
    active = models.BooleanField(default=False)
    date = models.DateField(auto_now=True)

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return f"{self.version}-{self.date}"

    def get_absolute_url(self):
        return reverse("changelog_Changelog_detail", args=(self.pk,))
