import hashlib
from collections import defaultdict
from functools import cached_property
from typing import Any, Dict, List

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryDataMixin:
    """Reused in registration_datahub.ImportedPaymentChannel / payment.PaymentChannel"""

    VALIDATION_ERROR_DATA_NOT_UNIQUE = _("Payment data not unique across Program")
    VALIDATION_ERROR_MISSING_DATA = _("Missing required payment data")

    def get_associated_object(self, associated_with: str) -> Any:
        from hct_mis_api.apps.core.field_attributes.fields_types import (
            _DELIVERY_MECHANISM_DATA,
            _HOUSEHOLD,
            _INDIVIDUAL,
        )

        associated_objects = {
            _INDIVIDUAL: self.individual,
            _HOUSEHOLD: self.individual.household,
            _DELIVERY_MECHANISM_DATA: self.data,
        }
        return associated_objects.get(associated_with)

    @property
    def delivery_data(self) -> Dict:
        delivery_data = {}
        for field in self.delivery_mechanism_fields:
            associated_object = self.get_associated_object(field["associated_with"])
            delivery_data[field["name"]] = getattr(associated_object, field["name"], None)

        return delivery_data

    def validate(self):
        self.validation_errors = {}
        for required_field in self.required_fields:
            associated_object = self.get_associated_object(required_field["associated_with"])
            value = getattr(associated_object, required_field["name"], None)
            if value is None:
                self.validation_errors[required_field["name"]] = self.VALIDATION_ERROR_MISSING_DATA
                self.is_valid = False
        if not self.validation_errors:
            self.is_valid = True

    def _normalize(self, name: str, value: Any) -> Any:
        if "." in name:
            return value
        field = self.__class__._meta.get_field(name)
        if isinstance(field, models.DecimalField) and value is not None:
            return f"{{:.{field.decimal_places}f}}".format(value)
        return value

    def update_unique_field(self) -> None:
        if self.is_valid and hasattr(self, "unique_fields") and isinstance(self.unique_fields, (list, tuple)):
            sha256 = hashlib.sha256()
            sha256.update(self.individual.program.name.encode("utf-8"))

            for field_name in self.unique_fields:
                value = getattr(self.data, field_name, None)
                value = self._normalize(field_name, value)
                sha256.update(str(value).encode("utf-8"))

            unique_key = sha256.hexdigest()
            possible_duplicates = self.model.objects.filter(
                unique_key__isnull=False,
                unique_key=unique_key,
                individual__program=self.individual.program,
                individual__withdrawn=False,
                individual__duplicate=False,
            ).exclude(pk=self.pk)

            if possible_duplicates.exists():
                self.unique_key = None
                self.is_valid = False
                self.validation_errors[str(self.unique_fields)] = f"{self.VALIDATION_ERROR_DATA_NOT_UNIQUE}"
                self.possible_duplicate_of = possible_duplicates.first()
            else:
                self.unique_key = unique_key

    signature_fields = (
        "data",
        "delivery_mechanism",
    )

    @cached_property
    def delivery_mechanism_fields(self) -> List[dict]:
        return self.get_delivery_mechanism_fields(self.delivery_mechanism)

    @property
    def required_fields(self) -> List[dict]:
        return [field for field in self.delivery_mechanism_fields if field.get("required_for_payment", False)]

    @property
    def unique_fields(self) -> List[dict]:
        return [field for field in self.delivery_mechanism_fields if field.get("unique_for_payment", False)]

    @classmethod
    def get_delivery_mechanism_fields(cls, delivery_mechanism: str) -> List[dict]:
        fields = cls.get_all_delivery_mechanisms_fields()
        return [field for field in fields if delivery_mechanism in field.get("delivery_mechanisms", [])]

    @classmethod
    def get_all_delivery_mechanisms_fields(cls, by: str = "name") -> List[dict]:
        from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
            FieldFactory,
        )
        from hct_mis_api.apps.core.field_attributes.fields_types import Scope

        global_fields = [
            _field
            for _field in FieldFactory.from_scope(Scope.GLOBAL).to_dict_by(by).values()
            if _field.get("delivery_mechanisms", [])
        ]
        delivery_mechanisms_fields = [
            _field for _field in FieldFactory.from_scope(Scope.DELIVERY_MECHANISM).to_dict_by(by).values()
        ]

        return global_fields + delivery_mechanisms_fields

    @classmethod
    def get_scope_delivery_mechanisms_fields(cls, by: str = "name") -> List[dict]:
        from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
            FieldFactory,
        )
        from hct_mis_api.apps.core.field_attributes.fields_types import Scope

        delivery_mechanisms_fields = [
            _field for _field in FieldFactory.from_scope(Scope.DELIVERY_MECHANISM).to_dict_by(by).values()
        ]

        return delivery_mechanisms_fields

    @classmethod
    def get_delivery_mechanisms_to_xlsx_fields_mapping(
        cls, by: str = "name", required: bool = False
    ) -> Dict[str, List[Dict]]:
        fields = cls.get_all_delivery_mechanisms_fields()
        fields = {
            field[by]: field.get("delivery_mechanisms", [])
            for field in fields
            if not required or field.get("required_for_payment", False)
        }
        dm_required_fields_map = defaultdict(list)
        for field_name, delivery_mechanisms in fields.items():
            for dm in delivery_mechanisms:
                dm_required_fields_map[dm].append(field_name)
        return dm_required_fields_map

    def save(self, *args: Any, validate: bool = True, deduplicate: bool = False, **kwargs: Any) -> None:
        if validate:
            self.validate()
        if deduplicate:
            self.update_unique_field()
        super().save(*args, **kwargs)
