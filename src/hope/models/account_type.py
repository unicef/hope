from django.contrib.postgres.fields import ArrayField
from django.db import models


class AccountType(models.Model):
    key = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    unique_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    payment_gateway_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = "payment"

    def __str__(self) -> str:
        return self.key

    @classmethod
    def get_targeting_field_names(cls) -> list[str]:
        return [
            f"{_account_type.key}__{field_name}"
            for _account_type in cls.objects.all()
            for field_name in _account_type.unique_fields
        ]
