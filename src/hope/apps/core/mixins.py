from django.db import models


class LimitBusinessAreaModelMixin(models.Model):
    allowed_business_areas = models.ManyToManyField(to="core.BusinessArea", blank=True)

    # Partner lists this mixin before MPTTModel, so this keeps Partner.objects a plain manager, not MPTT's TreeManager.
    objects = models.Manager()

    class Meta:
        abstract = True
