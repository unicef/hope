from functools import cached_property
import hashlib
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, models, transaction
from django.db.models import JSONField, Q, QuerySet

from hope.models.financial_institution import FinancialInstitution
from hope.models.utils import MergedManager, MergeStatusModel, PendingManager, SignatureMixin, TimeStampedUUIDModel


class Account(MergeStatusModel, TimeStampedUUIDModel, SignatureMixin):
    ACCOUNT_FIELD_PREFIX = "account__"

    individual = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    account_type = models.ForeignKey(
        "payment.AccountType",
        on_delete=models.PROTECT,
    )
    financial_institution = models.ForeignKey(
        "payment.FinancialInstitution",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    number = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    data = JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    unique_key = models.CharField(max_length=256, blank=True, null=True, editable=False)  # type: ignore
    is_unique = models.BooleanField(default=True, db_index=True)
    active = models.BooleanField(default=True, db_index=True)  # False for duplicated/withdrawn individual

    signature_fields = (
        "data",
        "account_type",
    )

    objects = MergedManager()
    all_objects = models.Manager()

    class Meta:
        app_label = "payment"
        constraints = [
            models.UniqueConstraint(
                fields=("unique_key", "active", "is_unique"),
                condition=Q(active=True) & Q(unique_key__isnull=False) & Q(is_unique=True),
                name="unique_active_wallet",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.individual} - {self.account_type}"

    @classmethod
    def is_valid_iban(cls, number: str | None) -> bool:
        if not number:
            return False

        # Country code -> length
        iban_lengths = {
            "AL": 28,
            "AD": 24,
            "AT": 20,
            "AZ": 28,
            "BH": 22,
            "BE": 16,
            "BA": 20,
            "BR": 29,
            "BG": 22,
            "CR": 22,
            "HR": 21,
            "CY": 28,
            "CZ": 24,
            "DK": 18,
            "DO": 28,
            "EE": 20,
            "FO": 18,
            "FI": 18,
            "FR": 27,
            "GE": 22,
            "DE": 22,
            "GI": 23,
            "GR": 27,
            "GL": 18,
            "GT": 28,
            "HU": 28,
            "IS": 26,
            "IE": 22,
            "IL": 23,
            "IT": 27,
            "JO": 30,
            "KZ": 20,
            "KW": 30,
            "LV": 21,
            "LB": 28,
            "LI": 21,
            "LT": 20,
            "LU": 20,
            "MK": 19,
            "MT": 31,
            "MR": 27,
            "MU": 30,
            "MD": 24,
            "MC": 27,
            "ME": 22,
            "NL": 18,
            "NO": 15,
            "PK": 24,
            "PS": 29,
            "PL": 28,
            "PT": 25,
            "QA": 29,
            "RO": 24,
            "SM": 27,
            "SA": 24,
            "RS": 22,
            "SK": 24,
            "SI": 19,
            "ES": 24,
            "SE": 24,
            "CH": 21,
            "TN": 24,
            "TR": 26,
            "AE": 23,
            "GB": 22,
            "VG": 24,
            "DZ": 24,
            "AO": 25,
            "BJ": 28,
            "BF": 27,
            "BI": 16,
            "CM": 27,
            "CV": 25,
            "IR": 26,
            "CI": 28,
            "MG": 27,
            "ML": 28,
            "MZ": 25,
            "SN": 28,
            "UA": 29,
        }

        iban_format = re.compile(r"^[A-Z]{2}\d{2}[A-Z0-9]+$")

        if not isinstance(number, str):
            number = str(number)

        number = number.replace(" ", "").upper()
        if not iban_format.match(number):
            return False

        cc = number[:2]
        expected_length = iban_lengths.get(cc)
        return len(number) == expected_length if expected_length is not None else True

    @property
    def account_data(self) -> dict:
        data = self.data.copy()
        data["number"] = self.number or data.get("number", "")
        data["financial_institution"] = str(self.financial_institution.id) if self.financial_institution else ""
        return data

    @account_data.setter
    def account_data(self, account_values: dict) -> None:
        for field_name, value in account_values.items():
            if field_name == "number":
                self.number = value
            elif field_name == "financial_institution":
                self.financial_institution = FinancialInstitution.objects.filter(id=value).first()
            else:
                self.data[field_name] = value

    @cached_property
    def unique_delivery_data_for_account_type(self) -> dict:
        delivery_data = {}
        unique_fields = self.account_type.unique_fields

        for field in unique_fields:
            delivery_data[field] = self.data.get(field, None)

        if self.number:
            delivery_data["number"] = self.number

        return delivery_data

    @property
    def unique_fields(self) -> list[str]:
        return self.account_type.unique_fields

    def update_unique_field(self) -> None:
        if hasattr(self, "unique_fields") and isinstance(self.unique_fields, list | tuple):
            if not self.unique_fields:
                self.is_unique = True
                self.unique_key = None
                self.save(update_fields=["unique_key", "is_unique"])
                return

            sha256 = hashlib.sha256()
            sha256.update(self.individual.program.name.encode("utf-8"))
            sha256.update(self.account_type.key.encode("utf-8"))

            for field_name in self.unique_fields:
                if value := self.unique_delivery_data_for_account_type.get(field_name, None):
                    sha256.update(str(value).encode("utf-8"))

            self.unique_key = sha256.hexdigest()
            try:
                with transaction.atomic():
                    self.is_unique = True
                    self.save(update_fields=["unique_key", "is_unique"])
            except IntegrityError:
                with transaction.atomic():
                    self.is_unique = False
                    self.save(update_fields=["unique_key", "is_unique"])

    @classmethod
    def validate_uniqueness(cls, qs: QuerySet["Account"] | list["Account"]) -> None:
        for dmd in qs:
            dmd.update_unique_field()


class PendingAccount(Account):
    objects: PendingManager = PendingManager()  # type: ignore

    class Meta:
        app_label = "payment"
        proxy = True
        verbose_name = "Imported Account"
        verbose_name_plural = "Imported Accounts"
