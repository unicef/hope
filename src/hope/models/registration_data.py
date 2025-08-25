import logging
from typing import Any

from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models, transaction
from django.db.models import Count, OuterRef, Q, QuerySet, Subquery
from django.utils.translation import gettext_lazy as _

from hope.apps.activity_log.utils import create_mapping_dict
from models.core import BusinessArea
from models.household import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    Household,
    Individual,
    PendingHousehold,
    PendingIndividual,
)
from hope.apps.registration_datahub.apis.deduplication_engine import SimilarityPair
from models.utils import AdminUrlMixin, ConcurrencyModel, TimeStampedUUIDModel
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator

logger = logging.getLogger(__name__)

SIMILAR_IN_BATCH = "SIMILAR_IN_BATCH"
DUPLICATE_IN_BATCH = "DUPLICATE_IN_BATCH"
UNIQUE_IN_BATCH = "UNIQUE_IN_BATCH"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_BATCH_STATUS_CHOICE = (
    (SIMILAR_IN_BATCH, "Similar in batch"),
    (DUPLICATE_IN_BATCH, "Duplicate in batch"),
    (UNIQUE_IN_BATCH, "Unique in batch"),
    (NOT_PROCESSED, "Not Processed"),
)

COLLECT_TYPE_UNKNOWN = ""
COLLECT_TYPE_NONE = "0"
COLLECT_TYPE_FULL = "1"
COLLECT_TYPE_PARTIAL = "2"

COLLECT_TYPES = (
    (COLLECT_TYPE_UNKNOWN, _("Unknown")),
    (COLLECT_TYPE_PARTIAL, _("Partial individuals collected")),
    (COLLECT_TYPE_FULL, _("Full individual collected")),
    (COLLECT_TYPE_NONE, _("No individual data")),
)


class RegistrationDataImport(TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "import_date",
            "imported_by",
            "data_source",
            "number_of_individuals",
            "number_of_households",
            "error_message",
        ]
    )
    LOADING = "LOADING"
    IMPORT_SCHEDULED = "IMPORT_SCHEDULED"
    IMPORTING = "IMPORTING"
    IN_REVIEW = "IN_REVIEW"
    MERGE_SCHEDULED = "MERGE_SCHEDULED"
    MERGING = "MERGING"
    MERGED = "MERGED"
    DEDUPLICATION_FAILED = "DEDUPLICATION_FAILED"
    DEDUPLICATION = "DEDUPLICATION"
    REFUSED_IMPORT = "REFUSED"
    IMPORT_ERROR = "IMPORT_ERROR"
    MERGE_ERROR = "MERGE_ERROR"
    STATUS_CHOICE = (
        (LOADING, _("Loading")),
        (DEDUPLICATION, _("Deduplication")),
        (DEDUPLICATION_FAILED, _("Deduplication Failed")),
        (IMPORT_SCHEDULED, _("Import Scheduled")),
        (IMPORTING, _("Importing")),
        (IMPORT_ERROR, _("Import Error")),
        (IN_REVIEW, _("In Review")),
        (MERGE_SCHEDULED, _("Merge Scheduled")),
        (MERGED, _("Merged")),
        (MERGING, _("Merging")),
        (MERGE_ERROR, _("Merge Error")),
        (REFUSED_IMPORT, _("Refused import")),
    )
    XLS = "XLS"
    KOBO = "KOBO"
    API = "API"
    FLEX_REGISTRATION = "FLEX_REGISTRATION"
    EDOPOMOGA = "EDOPOMOGA"
    PROGRAM_POPULATION = "PROGRAM_POPULATION"
    ENROLL_FROM_PROGRAM = "ENROLL_FROM_PROGRAM"
    DATA_SOURCE_CHOICE = (
        (XLS, "Excel"),
        (KOBO, "KoBo"),
        (FLEX_REGISTRATION, "Flex Registration"),
        (API, "Flex API"),
        (EDOPOMOGA, "eDopomoga"),
        (PROGRAM_POPULATION, "Programme Population"),
        (ENROLL_FROM_PROGRAM, "Enroll From Programme"),
    )

    DEDUP_ENGINE_PENDING = "PENDING"
    DEDUP_ENGINE_UPLOADED = "UPLOADED"
    DEDUP_ENGINE_IN_PROGRESS = "IN_PROGRESS"
    DEDUP_ENGINE_PROCESSING = "PROCESSING"
    DEDUP_ENGINE_FINISHED = "FINISHED"
    DEDUP_ENGINE_UPLOAD_ERROR = "UPLOAD_ERROR"
    DEDUP_ENGINE_ERROR = "ERROR"

    DEDUP_ENGINE_STATUS_CHOICE = (
        (DEDUP_ENGINE_PENDING, _("Pending")),
        (DEDUP_ENGINE_UPLOADED, _("Uploaded")),
        (DEDUP_ENGINE_IN_PROGRESS, _("Started")),
        (DEDUP_ENGINE_PROCESSING, _("Processing")),
        (DEDUP_ENGINE_FINISHED, _("Finished")),
        (DEDUP_ENGINE_ERROR, _("Error")),
        (DEDUP_ENGINE_UPLOAD_ERROR, _("Upload Error")),
    )
    name = CICharField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default=IN_REVIEW, db_index=True)
    deduplication_engine_status = models.CharField(
        max_length=255,
        choices=DEDUP_ENGINE_STATUS_CHOICE,
        blank=True,
        null=True,
        default=None,
    )
    business_area = models.ForeignKey(BusinessArea, null=True, on_delete=models.CASCADE)
    # TODO: set to not nullable Program and on_delete=models.PROTECT
    program = models.ForeignKey(
        "program.Program",
        null=True,
        blank=True,
        db_index=True,
        related_name="registration_imports",
        on_delete=models.SET_NULL,
    )
    import_date = models.DateTimeField(auto_now_add=True, db_index=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="registration_data_imports",
        on_delete=models.CASCADE,
        null=True,
    )
    data_source = models.CharField(
        max_length=255,
        choices=DATA_SOURCE_CHOICE,
    )
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import_hope",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    import_from_ids = models.TextField(blank=True, null=True)
    exclude_external_collectors = models.BooleanField(
        default=False,
        help_text="Exclude external alternate collectors from the RDI. "
        "This is used for the RDI created from the program population.",
    )
    pull_pictures = models.BooleanField(default=True)
    screen_beneficiary = models.BooleanField(default=False)
    excluded = models.BooleanField(default=False, help_text="Exclude RDI in UI")
    erased = models.BooleanField(default=False, help_text="Abort RDI")
    refuse_reason = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True)
    sentry_id = models.CharField(max_length=100, default="", blank=True, null=True)

    number_of_individuals = models.PositiveIntegerField(db_index=True)
    number_of_households = models.PositiveIntegerField(db_index=True)

    batch_duplicates = models.PositiveIntegerField(default=0)
    batch_possible_duplicates = models.PositiveIntegerField(default=0)
    batch_unique = models.PositiveIntegerField(default=0)
    golden_record_duplicates = models.PositiveIntegerField(default=0)
    golden_record_possible_duplicates = models.PositiveIntegerField(default=0)
    golden_record_unique = models.PositiveIntegerField(default=0)

    dedup_engine_batch_duplicates = models.PositiveIntegerField(default=0)
    dedup_engine_golden_record_duplicates = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return self.name

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Registration data import"
        permissions = (("rerun_rdi", "Can Rerun RDI"),)

    def should_check_against_sanction_list(self) -> bool:
        return self.screen_beneficiary

    @classmethod
    def get_choices(cls, business_area_slug: str | None = None, program_id: str | None = None) -> list[dict[str, Any]]:
        query = Q(status=cls.MERGED)
        if business_area_slug:
            query &= Q(business_area__slug=business_area_slug)
        if program_id:
            query &= Q(program_id=program_id)
        queryset = cls.objects.filter(query)
        return [
            {
                "label": {"English(EN)": f"{rdi.name}"},
                "value": rdi.id,
            }
            for rdi in queryset
        ]

    def can_be_merged(self) -> bool:
        return self.status in (self.IN_REVIEW, self.MERGE_ERROR)

    def refresh_population_statistics(self) -> None:
        self.number_of_individuals = Individual.objects.filter(registration_data_import=self).count()
        self.number_of_households = Household.objects.filter(registration_data_import=self).count()
        self.save(update_fields=("number_of_individuals", "number_of_households"))

    @property
    def biometric_deduplication_enabled(self) -> bool:
        return self.program.biometric_deduplication_enabled

    @property
    def biometric_deduplicated(self) -> str:
        if self.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_FINISHED:
            return "YES"
        return "NO"

    @property
    def can_merge(self) -> bool:
        if not self.program.is_active():
            return False

        is_still_processing = RegistrationDataImport.objects.filter(
            program=self.program,
            deduplication_engine_status__in=[
                RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
            ],
        ).exists()
        return not is_still_processing

    def update_duplicates_against_population_statistics(self) -> None:
        self.golden_record_duplicates = Individual.objects.filter(
            registration_data_import_id=self.id,
            deduplication_golden_record_status=DUPLICATE,
        ).count()
        self.golden_record_possible_duplicates = Individual.objects.filter(
            registration_data_import_id=self.id,
            deduplication_golden_record_status=NEEDS_ADJUDICATION,
        ).count()
        self.save(
            update_fields=[
                "golden_record_duplicates",
                "golden_record_possible_duplicates",
            ]
        )

    def bulk_update_household_size(self) -> None:
        # AB#208387
        if self.program and self.program.data_collecting_type.recalculate_composition:
            households = PendingHousehold.all_objects.filter(registration_data_import=self)
            size_subquery = Subquery(
                PendingIndividual.all_objects.filter(household=OuterRef("pk"))
                .values("household")
                .annotate(count=Count("pk"))
                .values("count")
            )
            households.update(size=size_subquery)


class ImportData(TimeStampedUUIDModel):
    XLSX = "XLSX"
    JSON = "JSON"
    FLEX_REGISTRATION = "FLEX"
    DATA_TYPE_CHOICES = (
        (XLSX, _("XLSX File")),
        (JSON, _("JSON File")),
        (FLEX_REGISTRATION, _("Flex Registration")),
    )
    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_FINISHED = "FINISHED"
    STATUS_ERROR = "ERROR"
    STATUS_VALIDATION_ERROR = "VALIDATION_ERROR"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_RUNNING, _("Running")),
        (STATUS_FINISHED, _("Finished")),
        (STATUS_ERROR, _("Error")),
        (STATUS_VALIDATION_ERROR, _("Validation Error")),
    )
    status = models.CharField(max_length=40, default=STATUS_FINISHED, choices=STATUS_CHOICES)
    business_area_slug = models.CharField(max_length=200, blank=True)
    data_type = models.CharField(max_length=4, choices=DATA_TYPE_CHOICES, default=XLSX)
    file = models.FileField(null=True)
    number_of_households = models.PositiveIntegerField(null=True)
    number_of_individuals = models.PositiveIntegerField(null=True)
    error = models.TextField(blank=True)
    validation_errors = models.TextField(blank=True)
    delivery_mechanisms_validation_errors = models.TextField(blank=True)
    created_by_id = models.UUIDField(null=True)


class KoboImportData(ImportData):
    kobo_asset_id = models.CharField(max_length=100)
    only_active_submissions = models.BooleanField(default=True)
    pull_pictures = models.BooleanField(default=True)


class RegistrationDataImportDatahub(TimeStampedUUIDModel):
    LOADING = "LOADING"
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    DONE = "DONE"
    IMPORT_DONE_CHOICES = (
        (LOADING, _("Loading")),
        (NOT_STARTED, _("Not Started")),
        (STARTED, _("Started")),
        (DONE, _("Done")),
    )

    name = models.CharField(max_length=255, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    hct_id = models.UUIDField(null=True, db_index=True)
    import_data = models.OneToOneField(
        ImportData,
        related_name="registration_data_import",
        on_delete=models.CASCADE,
        null=True,
    )
    import_done = models.CharField(max_length=15, choices=IMPORT_DONE_CHOICES, default=NOT_STARTED)
    business_area_slug = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ("name",)
        permissions = (["api_upload", "Can upload"],)

    def __str__(self) -> str:
        return self.name

    @property
    def business_area(self) -> str:
        return self.business_area_slug


class KoboImportedSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    kobo_submission_uuid = models.UUIDField()  # ImportedHousehold.kobo_submission_uuid
    kobo_asset_id = models.CharField(max_length=150)  # ImportedHousehold.detail_id
    kobo_submission_time = models.DateTimeField()  # ImportedHousehold.kobo_submission_time
    imported_household = models.ForeignKey("household.Household", blank=True, null=True, on_delete=models.SET_NULL)
    amended = models.BooleanField(default=False, blank=True)

    registration_data_import = models.ForeignKey(
        RegistrationDataImport,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.kobo_submission_uuid} ({self.kobo_asset_id})"


class DeduplicationEngineSimilarityPair(models.Model):
    class StatusCode(models.TextChoices):
        STATUS_200 = "200", "Deduplication success"
        STATUS_404 = "404", "No file found"
        STATUS_412 = "412", "No face detected"
        STATUS_429 = "429", "Multiple faces detected"
        STATUS_500 = "500", "Generic error"

    program = models.ForeignKey(
        "program.Program",
        related_name="deduplication_engine_similarity_pairs",
        on_delete=models.CASCADE,
    )
    individual1 = models.ForeignKey(
        "household.Individual",
        related_name="biometric_duplicates_1",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    individual2 = models.ForeignKey(
        "household.Individual",
        related_name="biometric_duplicates_2",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )  # 0 represents invalid pair (ex. multiple faces detected)
    status_code = models.CharField(max_length=20, choices=StatusCode.choices)

    class Meta:
        unique_together = ("individual1", "individual2")
        constraints = [
            # Prevent an Individual from being marked as a duplicate of itself
            # Enforce a consistent ordering to avoid duplicate entries in reverse
            models.CheckConstraint(
                check=models.Q(individual1__lt=models.F("individual2")),
                name="individual1_lt_individual2",
            ),
        ]

    def __str__(self):
        return f"{self.program} - {self.individual1} / {self.individual2}"

    @classmethod
    def remove_pairs(cls, deduplication_set_id: str) -> None:
        from models.program import Program

        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        cls.objects.filter(program=program).delete()

    @classmethod
    def bulk_add_pairs(cls, deduplication_set_id: str, duplicates_data: list[SimilarityPair]) -> None:
        from models.program import Program

        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        duplicates = []
        for pair in duplicates_data:
            if pair.first and pair.second:
                # Ensure consistent ordering of individual1 and individual2
                individual1, individual2 = sorted([pair.first, pair.second])
            elif not (pair.first or pair.second):
                continue
            else:
                individual1, individual2 = pair.first, pair.second

            if individual1 == individual2:
                logger.warning(f"Skipping duplicate pair ({individual1}, {individual2})")
                continue

            duplicates.append(
                cls(
                    program=program,
                    individual1_id=individual1,
                    individual2_id=individual2,
                    status_code=pair.status_code,
                    similarity_score=pair.score * 100,
                )
            )
        if duplicates:
            with transaction.atomic():
                cls.objects.bulk_create(duplicates, ignore_conflicts=True)

    def serialize_for_ticket(self) -> dict[str, Any]:
        results = {
            "similarity_score": float(self.similarity_score),
            "status_code": self.get_status_code_display(),
        }
        for i, ind in enumerate([self.individual1, self.individual2]):
            results[f"individual{i + 1}"] = {
                "id": str(ind.id) if ind else "",
                "unicef_id": str(ind.unicef_id) if ind else "",
                "full_name": ind.full_name if ind else "",
                "photo_name": str(ind.photo.name) if ind and ind.photo else None,
            }

        return results

    @classmethod
    def serialize_for_individual(
        cls,
        individual: Individual,
        similarity_pairs: QuerySet["DeduplicationEngineSimilarityPair"],
    ) -> list:
        duplicates = []
        for pair in similarity_pairs:
            duplicate = pair.individual2 if pair.individual1 == individual else pair.individual1
            household = duplicate.household
            duplicates.append(
                {
                    "id": str(duplicate.id),
                    "unicef_id": str(duplicate.unicef_id),
                    "full_name": duplicate.full_name,
                    "similarity_score": float(pair.similarity_score),
                    "age": duplicate.age,
                    "location": household.admin2.name if duplicate.household and duplicate.household.admin2 else None,
                }
            )

        return duplicates
