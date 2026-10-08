import copy
import json

from django.db import models
from strategy_field.fields import StrategyField
import swapper

from hope.apps.registration_data.utils import combine_collections
from hope.contrib.aurora.rdi import registry
from hope.models.utils import LongNameIndex, TimeStampedModel


class AuroraModel(TimeStampedModel):
    source_id = models.BigIntegerField()

    class Meta:
        abstract = True


class Organization(AuroraModel):
    name = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000)
    business_area = models.ForeignKey("core.BusinessArea", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            LongNameIndex(fields=["created_at"], name="aurora_organization_created_at_4f7b8b55"),
            LongNameIndex(fields=["updated_at"], name="aurora_organization_updated_at_b65df51b"),
        ]

    def __str__(self) -> str:
        return self.name


class Project(AuroraModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    programme = models.ForeignKey("program.Program", null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)

    class Meta:
        indexes = [
            LongNameIndex(fields=["created_at"], name="aurora_project_created_at_58878624"),
            LongNameIndex(fields=["updated_at"], name="aurora_project_updated_at_9b17f827"),
        ]

    def __str__(self) -> str:
        return self.name


def get_rdi_policy_choices() -> tuple:
    return Registration.RDI_POLICIES


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
        choices=get_rdi_policy_choices,
        default=1,
    )
    steficon_rule = models.ForeignKey("steficon.RuleCommit", blank=True, null=True, on_delete=models.SET_NULL)
    mapping = models.JSONField(blank=True, null=True)
    private_key = models.TextField(blank=True, null=True, editable=False)

    class Meta:
        indexes = [
            LongNameIndex(fields=["created_at"], name="aurora_registration_created_at_2c5ed126"),
            LongNameIndex(fields=["updated_at"], name="aurora_registration_updated_at_4dbeb556"),
        ]

    def __str__(self) -> str:
        return self.name


def get_record_status_choices() -> tuple:
    return Record.STATUSES_CHOICES


class Record(models.Model):
    STATUS_TO_IMPORT = "TO_IMPORT"
    STATUS_IMPORTED = "IMPORTED"
    STATUS_ERROR = "ERROR"
    STATUSES_CHOICES = (
        (STATUS_TO_IMPORT, "To import"),
        (STATUS_IMPORTED, "Imported"),
        (STATUS_ERROR, "Error"),
    )

    registration = models.IntegerField()
    timestamp = models.DateTimeField()
    storage = models.BinaryField(null=True, blank=True)
    ignored = models.BooleanField(default=False, blank=True, null=True)
    source_id = models.IntegerField()
    data = models.JSONField(default=dict, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=get_record_status_choices, null=True, blank=True)

    unique_field = models.CharField(blank=True, null=True, max_length=255)
    size = models.IntegerField(blank=True, null=True)
    counters = models.JSONField(blank=True, null=True)

    fields = models.JSONField(null=True, blank=True)
    files = models.BinaryField(null=True, blank=True)

    index1 = models.CharField(null=True, blank=True, max_length=255)
    index2 = models.CharField(null=True, blank=True, max_length=255)
    index3 = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        swappable = swapper.swappable_setting("aurora", "Record")
        permissions = (
            ("can_fetch_data", "Can fetch data from aurora"),
            ("can_add_records", "Can add records"),
        )
        indexes = [
            LongNameIndex(fields=["registration"], name="aurora_record_registration_18c617c1"),
            LongNameIndex(fields=["timestamp"], name="aurora_record_timestamp_d68c0d5a"),
            LongNameIndex(fields=["ignored"], name="aurora_record_ignored_1640d007"),
            LongNameIndex(fields=["source_id"], name="aurora_record_source_id_e66ff785"),
            LongNameIndex(fields=["unique_field"], name="aurora_record_unique_field_903b6acc"),
            LongNameIndex(
                fields=["unique_field"],
                opclasses=["varchar_pattern_ops"],
                name="aurora_record_unique_field_903b6acc_like",
            ),
            LongNameIndex(fields=["index1"], name="aurora_record_index1_359087d6"),
            LongNameIndex(
                fields=["index1"], opclasses=["varchar_pattern_ops"], name="aurora_record_index1_359087d6_like"
            ),
            LongNameIndex(fields=["index2"], name="aurora_record_index2_cfcbc3b9"),
            LongNameIndex(
                fields=["index2"], opclasses=["varchar_pattern_ops"], name="aurora_record_index2_cfcbc3b9_like"
            ),
            LongNameIndex(fields=["index3"], name="aurora_record_index3_21b563c6"),
            LongNameIndex(
                fields=["index3"], opclasses=["varchar_pattern_ops"], name="aurora_record_index3_21b563c6_like"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.registration} - {self.source_id}"

    def mark_as_invalid(self, msg: str) -> None:
        self.error_message = msg
        self.status = self.STATUS_ERROR
        self.save(update_fields=["status", "error_message"])

    def mark_as_imported(self) -> None:
        self.status = self.STATUS_IMPORTED
        self.save(update_fields=["status"])

    def get_data(self) -> dict:
        if self.storage:
            return json.loads(bytes(self.storage))

        fields_copy = copy.deepcopy(self.fields) if self.fields is not None else {}

        if not self.files:
            return fields_copy

        files = json.loads(bytes(self.files))
        return combine_collections(files, fields_copy)
