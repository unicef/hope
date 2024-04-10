from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from hct_mis_api.apps.core.models import BusinessArea


class LimitBusinessAreaModelQuerySet(QuerySet):
    def allowed_to(self, business_area_slug: str) -> QuerySet:
        return self.filter(allowed_business_areas__slug=business_area_slug)


class LimitBusinessAreaModelManager(models.Manager):
    _queryset_class = LimitBusinessAreaModelQuerySet


class LimitBusinessAreaModelMixin(models.Model):
    allowed_business_areas = models.ManyToManyField(to=BusinessArea)

    objects = LimitBusinessAreaModelManager()

    class Meta:
        abstract = True


class RdiMergedModelManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(rdi_merge_status=RdiMergeStatusMixin.MERGED)


class RdiImportedModelManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(rdi_merge_status=RdiMergeStatusMixin.PENDING)


class RdiMergeStatusMixin(models.Model):
    PENDING = "PENDING"
    MERGED = "MERGED"
    STATUS_CHOICE = (
        (PENDING, _("Pending")),
        (MERGED, _("Merged")),
    )

    rdi_merge_status = models.CharField(max_length=10, choices=STATUS_CHOICE, null=True)

    objects = RdiMergedModelManager()
    imported = RdiImportedModelManager()

    class Meta:
        abstract = True
