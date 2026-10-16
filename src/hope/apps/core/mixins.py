from django.db import models


class LimitBusinessAreaModelMixin(models.Model):
    allowed_business_areas = models.ManyToManyField(to="core.BusinessArea", blank=True)

    class Meta:
        abstract = True
