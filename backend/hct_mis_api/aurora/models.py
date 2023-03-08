from django.db import models

from strategy_field.fields import StrategyField

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_datahub.models import Record as Record_
from hct_mis_api.apps.steficon.models import RuleCommit

from .rdi import registry


class AuroraModel(models.Model):
    source_id = models.BigIntegerField()

    class Meta:
        abstract = True


class Organization(AuroraModel):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000)
    business_area = models.ForeignKey(BusinessArea, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Project(AuroraModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    programme = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Registration(AuroraModel):
    RDI_MANUAL = 1
    RDI_DAILY = 2
    RDI_AS_DATA = 3
    RDI_POLICIES = (
        (RDI_MANUAL, "Manual"),
        (RDI_DAILY, "Daily"),
        (RDI_AS_DATA, "As data arrives"),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    slug = models.SlugField()
    extra = models.JSONField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    rdi_policy = models.IntegerField(
        choices=RDI_POLICIES,
        default=1,
    )
    rdi_parser = StrategyField(registry=registry, blank=True, null=True)
    steficon_rule = models.ForeignKey(RuleCommit, blank=True, null=True, on_delete=models.SET_NULL)
    mapping = models.JSONField(blank=True, null=True)
    private_key = models.TextField(blank=True, null=True, editable=False)

    def __str__(self):
        return self.name


class Record(Record_):
    class Meta:
        proxy = True
