import logging
from django.db import models

from hope.models.country import Country
from hope.models.utils import TimeStampedModel


logger = logging.getLogger(__name__)


class FinancialInstitution(TimeStampedModel):
    class FinancialInstitutionType(models.TextChoices):
        BANK = "bank", "Bank"
        TELCO = "telco", "Telco"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=FinancialInstitutionType.choices)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    swift_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.id} {self.name}: {self.type}"  # pragma: no cover

    class Meta:
        app_label = "payment"

    @classmethod
    def get_rdi_template_choices(cls) -> dict:
        return {
            "account__ACCOUNT_TYPE__financial_institution": {
                "choices": [{"value": fi.pk, "label": {"English(EN)": fi.name}} for fi in cls.objects.all()]
            }
        }

    @classmethod
    def get_generic_one(cls, account_type: str, is_valid_iban: bool) -> "FinancialInstitution":
        if account_type == "mobile":
            return cls.objects.get(name="Generic Telco Company")

        if account_type == "bank":
            if is_valid_iban:
                return cls.objects.get(name="IBAN Provider Bank")
            return cls.objects.get(name="Generic Bank")

        if account_type == "card":
            return cls.objects.get(name="Generic Bank")

        logger.error(f"Unknown account type for generic Financial Institution: {account_type}")
        return cls.objects.get(name="Generic Bank")

    @property
    def is_generic(self) -> bool:
        return self.country is None
