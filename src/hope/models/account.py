import hashlib
from functools import cached_property

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction, IntegrityError
from django.db.models import JSONField, Q, QuerySet

from hope.models.financial_institution import FinancialInstitution
from hope.models.utils import MergeStatusModel, TimeStampedUUIDModel, SignatureMixin, MergedManager, PendingManager


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

    @property
    def account_data(self) -> dict:
        data = self.data.copy()
        if self.number:
            data["number"] = self.number
        if self.financial_institution:
            data["financial_institution"] = str(self.financial_institution.id)
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
