from django.db import models

from hct_mis_api.apps.core.models import BusinessArea


class LimitBusinessAreaModelManager(models.Manager):
    def allowed_to(self, business_area: BusinessArea):
        return super().get_queryset().filter(allowed_business_areas__in=[business_area])


class LimitBusinessAreaModelMixin(models.Model):
    allowed_business_areas = models.ManyToManyField(to=BusinessArea, related_name="+")

    objects = LimitBusinessAreaModelManager()

    class Meta:
        abstract = True
