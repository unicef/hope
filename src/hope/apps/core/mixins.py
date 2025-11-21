from django.db import models
from django.db.models.query import QuerySet

from hope.models.business_area import BusinessArea


class LimitBusinessAreaModelQuerySet(QuerySet):
    def allowed_to(self, business_area_slug: str) -> QuerySet:
        return self.filter(allowed_business_areas__slug=business_area_slug)


class LimitBusinessAreaModelManager(models.Manager):
    _queryset_class = LimitBusinessAreaModelQuerySet


class LimitBusinessAreaModelMixin(models.Model):
    allowed_business_areas = models.ManyToManyField(to=BusinessArea, blank=True)

    objects = LimitBusinessAreaModelManager()

    class Meta:
        abstract = True
