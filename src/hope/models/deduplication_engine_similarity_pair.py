from typing import TYPE_CHECKING, Any

from django.db import models, transaction
from django.db.models import QuerySet

from hope.apps.registration_data.api.deduplication_engine import SimilarityPair
from hope.models.individual import Individual
from hope.models.registration_data_import import logger

if TYPE_CHECKING:
    from hope.models.program import Program


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
        app_label = "registration_data"
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
    def bulk_add_pairs(cls, program: "Program", duplicates_data: list[SimilarityPair]) -> None:
        duplicates = []

        all_unique_ind_ids: set = set()
        for pair in duplicates_data:
            if pair.first:
                all_unique_ind_ids.add(pair.first)
            if pair.second:
                all_unique_ind_ids.add(pair.second)

        existing_ind_ids = {
            str(pk) for pk in Individual.all_objects.filter(id__in=all_unique_ind_ids).values_list("id", flat=True)
        }

        for pair in duplicates_data:
            if not (pair.first or pair.second):
                logger.warning("Dedup Engine Findings, both Individuals empty")
                continue

            # Skip if either individual does NOT exist in DB
            if (pair.first and pair.first not in existing_ind_ids) or (
                pair.second and pair.second not in existing_ind_ids
            ):
                logger.warning(
                    f"Dedup Engine Findings, one of Individuals ({pair.first}, {pair.second}) does not exist",
                )
                continue

            if pair.first and pair.second:
                # Ensure consistent ordering of individual1 and individual2
                individual1, individual2 = sorted([pair.first, pair.second])
            else:
                individual1, individual2 = pair.first, pair.second

            if individual1 == individual2:
                logger.warning(f"Dedup Engine Findings, skipping duplicate pair ({individual1}, {individual2})")
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
            if not duplicate:
                continue
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
