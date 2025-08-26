from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class DocumentType(TimeStampedUUIDModel):
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    is_identity_document = models.BooleanField(default=True)
    unique_for_individual = models.BooleanField(default=False)
    valid_for_deduplication = models.BooleanField(default=False)

    class Meta:
        app_label = "household"
        ordering = [
            "label",
        ]

    def __str__(self) -> str:
        return f"{self.label}"

    @classmethod
    def get_all_doc_types_choices(cls) -> list[tuple[str, str]]:
        """Return list of Document Types choices."""
        return [(obj.key, obj.label) for obj in cls.objects.all()]

    @classmethod
    def get_all_doc_types(cls) -> list[str]:
        """Return list of Document Types keys."""
        return list(cls.objects.all().only("key").values_list("key", flat=True))
