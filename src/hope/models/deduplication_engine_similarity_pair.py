from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal

from django.db import models, transaction
from django.db.models import Q, QuerySet

from hope.apps.registration_data.api.deduplication_engine import (
    BiographicHDEFinding,
    BiometricHDEFinding,
    HDEFinding,
)
from hope.models.individual import Individual, PendingIndividual
from hope.models.registration_data_import import logger
from hope.models.utils import MergeStatusModel

if TYPE_CHECKING:
    from hope.models.program import Program
    from hope.models.registration_data_import import RegistrationDataImport


IndividualIdField = Literal["country_workspace_id", "id"]


class DedupEngineSimilarityPairQuerySet(models.QuerySet):
    def for_rdi_against_batch(self, rdi: "RegistrationDataImport") -> QuerySet:
        rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
        return self.filter(
            Q(individual1__in=rdi_individuals) & Q(individual2__in=rdi_individuals),
            program=rdi.program,
        ).distinct()

    def for_rdi_against_population(self, rdi: "RegistrationDataImport", rdi_merged: bool = False) -> QuerySet:
        if rdi_merged:
            rdi_individuals = Individual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program)
        else:
            rdi_individuals = PendingIndividual.objects.filter(registration_data_import=rdi).only("id")
            other_pending_rdis_individuals = PendingIndividual.objects.filter(program=rdi.program).exclude(
                id__in=rdi_individuals
            )

        qs = self.filter(
            Q(individual1__in=rdi_individuals) | Q(individual2__in=rdi_individuals),
            (Q(individual1__duplicate=False) | Q(individual1__isnull=True))
            & (Q(individual2__duplicate=False) | Q(individual2__isnull=True)),
            (Q(individual1__withdrawn=False) | Q(individual1__isnull=True))
            & (Q(individual2__withdrawn=False) | Q(individual2__isnull=True)),
            (
                Q(individual1__rdi_merge_status=MergeStatusModel.MERGED)
                | Q(individual1__isnull=True)
                | Q(individual2__rdi_merge_status=MergeStatusModel.MERGED)
                | Q(individual2__isnull=True)
            ),
            program=rdi.program,
        ).exclude(Q(individual1__in=other_pending_rdis_individuals) | Q(individual2__in=other_pending_rdis_individuals))

        return qs.distinct()


class DedupEngineSimilarityPair(models.Model):
    if TYPE_CHECKING:
        program: models.ForeignKey["Program"]
        individual1: models.ForeignKey[Individual | None]
        individual2: models.ForeignKey[Individual | None]

    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    objects = DedupEngineSimilarityPairQuerySet.as_manager()

    class Meta:
        abstract = True
        app_label = "registration_data"
        ordering = ("id",)
        unique_together = ("individual1", "individual2")

    def __str__(self) -> str:
        return f"[{self._meta.verbose_name}] {self.program} - {self.individual1} / {self.individual2}"

    @classmethod
    def bulk_add_pairs(
        cls,
        program: "Program",
        hde_findings: Sequence[HDEFinding],
        id_field_name: IndividualIdField = "id",
    ) -> None:
        if not hde_findings:
            return

        all_unique_ind_ids = cls._extract_unique_ids(hde_findings)
        id_to_hope_pk = cls._resolve_id_to_hope_pk(all_unique_ind_ids, id_field_name, program)

        duplicates: list[DedupEngineSimilarityPair] = []
        for finding in hde_findings:
            if not (finding.first or finding.second):
                logger.warning("Dedup Engine Findings, both Individuals empty")
                continue

            first_pk = id_to_hope_pk.get(finding.first) if finding.first else None
            second_pk = id_to_hope_pk.get(finding.second) if finding.second else None

            if (finding.first and not first_pk) or (finding.second and not second_pk):
                logger.warning(
                    f"Dedup Engine Findings, one of Individuals ({finding.first}, {finding.second}) does not exist"
                )
                continue

            individual1: str | None
            individual2: str | None
            if first_pk and second_pk:
                individual1, individual2 = sorted([first_pk, second_pk])
            else:
                individual1, individual2 = first_pk, second_pk

            if individual1 == individual2:
                logger.warning(f"Dedup Engine Findings, skipping duplicate pair ({individual1}, {individual2})")
                continue

            duplicates.append(cls._build_pair(program, individual1, individual2, finding))

        if duplicates:
            with transaction.atomic():
                cls.objects.bulk_create(duplicates, ignore_conflicts=True)

    @classmethod
    def _build_pair(
        cls, program: "Program", individual1_id: str | None, individual2_id: str | None, finding: HDEFinding
    ) -> "DedupEngineSimilarityPair":
        raise NotImplementedError

    @staticmethod
    def _extract_unique_ids(hde_findings: Sequence[HDEFinding]) -> set[str]:
        unique_ids: set[str] = set()
        for finding in hde_findings:
            if finding.first:
                unique_ids.add(finding.first)
            if finding.second:
                unique_ids.add(finding.second)
        return unique_ids

    @staticmethod
    def _resolve_id_to_hope_pk(
        unique_ids: set[str], id_field_name: IndividualIdField, program: "Program"
    ) -> dict[str, str]:
        # When an RDI is pushed from CW, HDEFinding.first/second carry country_workspace_ids.
        # Otherwise HDEFinding.first/second is HOPE individual id.
        # _resolve_id_to_hope_pk returns a map HOPE_ID | country_workspace_id -> HOPE_ID
        return {
            str(key): str(pk)
            for key, pk in Individual.all_objects.filter(
                program=program,
                is_removed=False,
                withdrawn=False,
                **{f"{id_field_name}__in": unique_ids},
            ).values_list(id_field_name, "id")
        }


class BiometricDedupeSimilarityPair(DedupEngineSimilarityPair):
    class StatusCode(models.TextChoices):
        STATUS_200 = "200", "Deduplication success"
        STATUS_404 = "404", "No file found"
        STATUS_412 = "412", "No face detected"
        STATUS_416 = "416", "Face below confidence"
        STATUS_418 = "418", "Image quality below threshold"
        STATUS_429 = "429", "Multiple faces detected"
        STATUS_500 = "500", "Generic error"

        @staticmethod
        def _status_code_choices() -> list[tuple[str, str]]:
            return BiometricDedupeSimilarityPair.StatusCode.choices

        @classmethod
        def photo_error_codes(cls) -> tuple[str, ...]:
            # The photo was unusable, so no valid biometric comparison was possible
            # (score 0). These pairs are rerouted to a photo-fix Data Change ticket.
            return (cls.STATUS_412.value, cls.STATUS_416.value, cls.STATUS_418.value, cls.STATUS_429.value)

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
    status_code = models.CharField(max_length=20, choices=StatusCode._status_code_choices)

    class Meta(DedupEngineSimilarityPair.Meta):
        constraints = [
            # Prevent an Individual from being marked as a duplicate of itself
            # Enforce a consistent ordering to avoid duplicate entries in reverse
            models.CheckConstraint(
                condition=models.Q(individual1__lt=models.F("individual2")),
                name="biometric_individual1_lt_individual2",
            ),
        ]

    @classmethod
    def _build_pair(
        cls, program: "Program", individual1_id: str | None, individual2_id: str | None, finding: HDEFinding
    ) -> "BiometricDedupeSimilarityPair":
        if not isinstance(finding, BiometricHDEFinding):
            raise TypeError(f"Expected BiometricHDEFinding, got {type(finding).__name__}")
        return cls(
            program=program,
            individual1_id=individual1_id,
            individual2_id=individual2_id,
            status_code=finding.status_code,
            similarity_score=finding.score * 100,
        )

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
        similarity_pairs: QuerySet["BiometricDedupeSimilarityPair"],
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


class BiographicDedupeSimilarityPair(DedupEngineSimilarityPair):
    program = models.ForeignKey(
        "program.Program",
        related_name="biographic_dedup_similarity_pairs",
        on_delete=models.CASCADE,
    )
    individual1 = models.ForeignKey(
        "household.Individual",
        related_name="biographic_duplicates_1",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    individual2 = models.ForeignKey(
        "household.Individual",
        related_name="biographic_duplicates_2",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    proximity_to_score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta(DedupEngineSimilarityPair.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(individual1__lt=models.F("individual2")),
                name="biographic_individual1_lt_individual2",
            ),
        ]

    @classmethod
    def _build_pair(
        cls, program: "Program", individual1_id: str | None, individual2_id: str | None, finding: HDEFinding
    ) -> "BiographicDedupeSimilarityPair":
        if not isinstance(finding, BiographicHDEFinding):
            raise TypeError(f"Expected BiographicHDEFinding, got {type(finding).__name__}")
        return cls(
            program=program,
            individual1_id=individual1_id,
            individual2_id=individual2_id,
            similarity_score=finding.score,
            proximity_to_score=finding.proximity_to_score,
        )
