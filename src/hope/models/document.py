import re

from django.db import models
from django.db.models import UniqueConstraint, Q, Func, F, Value, BooleanField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hope.models.household import logger
from hope.models.utils import TimeStampedUUIDModel, AbstractSyncable, SoftDeletableMergeStatusModel, MergeStatusModel, \
    PendingManager


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey("household.DocumentType", related_name="validators", on_delete=models.CASCADE)
    regex = models.CharField(max_length=100, default=".*")

    class Meta:
        app_label = "household"


class Document(AbstractSyncable, SoftDeletableMergeStatusModel, TimeStampedUUIDModel):
    STATUS_PENDING = "PENDING"
    STATUS_VALID = "VALID"
    STATUS_NEED_INVESTIGATION = "NEED_INVESTIGATION"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_VALID, _("Valid")),
        (STATUS_NEED_INVESTIGATION, _("Need Investigation")),
        (STATUS_INVALID, _("Invalid")),
    )

    individual = models.ForeignKey("household.Individual", related_name="documents", on_delete=models.CASCADE)
    program = models.ForeignKey("program.Program", null=True, related_name="+", on_delete=models.CASCADE)
    document_number = models.CharField(max_length=255, blank=True, db_index=True)
    type = models.ForeignKey("household.DocumentType", related_name="documents", on_delete=models.CASCADE)
    country = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    photo = models.ImageField(blank=True)
    cleared = models.BooleanField(default=False)
    cleared_date = models.DateTimeField(default=timezone.now)
    cleared_by = models.ForeignKey("account.User", null=True, on_delete=models.SET_NULL)
    issuance_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.warning("Document number is not validating")
                raise ValidationError("Document number is not validating")

    class Meta:
        app_label = "household"
        constraints = [
            # if document_type.unique_for_individual=True then document of this type must be unique for an individual
            UniqueConstraint(
                fields=["individual", "type", "country", "program"],
                condition=Q(
                    Q(is_removed=False)
                    & Q(status="VALID")
                    & Func(
                        F("type_id"),
                        Value(True),
                        function="check_unique_document_for_individual",
                        output_field=BooleanField(),
                    )
                ),
                name="unique_for_individual_if_not_removed_and_valid",
            ),
            # document_number must be unique across all documents of the same type
            UniqueConstraint(
                fields=["document_number", "type", "country", "program"],
                condition=Q(Q(is_removed=False) & Q(status="VALID") & Q(rdi_merge_status=MergeStatusModel.MERGED)),
                name="unique_if_not_removed_and_valid_for_representations",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type} - {self.document_number}"

    def mark_as_need_investigation(self) -> None:
        self.status = self.STATUS_NEED_INVESTIGATION

    def mark_as_valid(self) -> None:
        self.status = self.STATUS_VALID

    def erase(self) -> None:
        self.is_removed = True
        self.photo = ""
        self.document_number = "GDPR REMOVED"
        self.save()


class PendingDocument(Document):
    objects = PendingManager()

    class Meta:
        app_label = "household"
        proxy = True
        verbose_name = "Imported Document"
        verbose_name_plural = "Imported Documents"
