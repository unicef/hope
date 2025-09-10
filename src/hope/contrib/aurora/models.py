import json

from django.db import models
from strategy_field.fields import StrategyField
import swapper

from hope.apps.registration_datahub.utils import combine_collections
from hope.apps.utils.models import TimeStampedModel
from hope.contrib.aurora.rdi import registry


class AuroraModel(TimeStampedModel):
    source_id = models.BigIntegerField()

    class Meta:
        abstract = True


class Organization(AuroraModel):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000)
    business_area = models.ForeignKey("core.BusinessArea", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Project(AuroraModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    programme = models.ForeignKey("program.Program", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
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
    rdi_parser = StrategyField(registry=registry, blank=True, null=True)
    rdi_policy = models.IntegerField(
        choices=RDI_POLICIES,
        default=1,
    )
    steficon_rule = models.ForeignKey("steficon.RuleCommit", blank=True, null=True, on_delete=models.SET_NULL)
    mapping = models.JSONField(blank=True, null=True)
    private_key = models.TextField(blank=True, null=True, editable=False)

    def __str__(self) -> str:
        return self.name


class Record(models.Model):
    STATUS_TO_IMPORT = "TO_IMPORT"
    STATUS_IMPORTED = "IMPORTED"
    STATUS_ERROR = "ERROR"
    STATUSES_CHOICES = (
        (STATUS_TO_IMPORT, "To import"),
        (STATUS_IMPORTED, "Imported"),
        (STATUS_ERROR, "Error"),
    )

    registration = models.IntegerField(db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    storage = models.BinaryField(null=True, blank=True)
    ignored = models.BooleanField(default=False, blank=True, null=True, db_index=True)
    source_id = models.IntegerField(db_index=True)
    data = models.JSONField(default=dict, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUSES_CHOICES, null=True, blank=True)

    unique_field = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    size = models.IntegerField(blank=True, null=True)
    counters = models.JSONField(blank=True, null=True)

    fields = models.JSONField(null=True, blank=True)
    files = models.BinaryField(null=True, blank=True)

    index1 = models.CharField(null=True, blank=True, max_length=255, db_index=True)
    index2 = models.CharField(null=True, blank=True, max_length=255, db_index=True)
    index3 = models.CharField(null=True, blank=True, max_length=255, db_index=True)

    class Meta:
        swappable = swapper.swappable_setting("aurora", "Record")
        permissions = (
            ("can_fetch_data", "Can fetch data from aurora"),
            ("can_add_records", "Can add records"),
        )

    def __str__(self):
        return f"{self.registration} - {self.source_id}"

    def mark_as_invalid(self, msg: str) -> None:
        self.error_message = msg
        self.status = self.STATUS_ERROR
        self.save()

    def mark_as_imported(self) -> None:
        self.status = self.STATUS_IMPORTED
        self.save()

    def get_data(self) -> dict:
        if self.storage:
            return json.loads(self.storage.tobytes().decode())
        if not self.files:
            return self.fields
        files = json.loads(self.files.tobytes().decode())
        return combine_collections(files, self.fields)
