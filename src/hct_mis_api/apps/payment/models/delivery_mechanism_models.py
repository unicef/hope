import hashlib
import json
import uuid
from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
    CORE_FIELDS_ATTRIBUTES,
    get_core_fields_attributes,
)
from hct_mis_api.apps.core.field_attributes.fields_types import (
    _DELIVERY_MECHANISM_DATA,
    TYPE_STRING,
    Scope,
)
from hct_mis_api.apps.utils.models import (
    MergedManager,
    MergeStatusModel,
    PendingManager,
    SignatureMixin,
    TimeStampedUUIDModel,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.grievance.models import GrievanceTicket


class DeliveryMechanismData(MergeStatusModel, TimeStampedUUIDModel, SignatureMixin):
    VALIDATION_ERROR_DATA_NOT_UNIQUE = _("Payment data not unique across Program")
    VALIDATION_ERROR_MISSING_DATA = _("Missing required payment data")

    individual = models.ForeignKey(
        "household.Individual", on_delete=models.CASCADE, related_name="delivery_mechanisms_data"
    )
    delivery_mechanism = models.ForeignKey("DeliveryMechanism", on_delete=models.PROTECT)
    data = models.JSONField(default=dict, blank=True)

    is_valid: bool = models.BooleanField(default=False)  # type: ignore
    validation_errors: dict = models.JSONField(default=dict)  # type: ignore
    possible_duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="possible_duplicates",
        null=True,
        blank=True,
    )
    unique_key = models.CharField(max_length=256, blank=True, null=True, unique=True, editable=False)  # type: ignore

    signature_fields = (
        "data",
        "delivery_mechanism",
    )

    objects = MergedManager()
    all_objects = models.Manager()

    def __str__(self) -> str:
        return f"{self.individual} - {self.delivery_mechanism}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["individual", "delivery_mechanism"],
                name="unique_individual_delivery_mechanism",
            ),
        ]

    def get_associated_object(self, associated_with: str) -> Any:
        from hct_mis_api.apps.core.field_attributes.fields_types import (
            _DELIVERY_MECHANISM_DATA,
            _HOUSEHOLD,
            _INDIVIDUAL,
        )

        associated_objects = {
            _INDIVIDUAL: self.individual,
            _HOUSEHOLD: self.individual.household,
            _DELIVERY_MECHANISM_DATA: self._data,
        }
        return associated_objects.get(associated_with)

    @property
    def _data(self) -> Dict:
        return json.loads(self.data) if not isinstance(self.data, dict) else self.data

    @cached_property
    def delivery_data(self) -> Dict:
        delivery_data = {}
        for field in self.delivery_mechanism_all_fields_definitions:
            associated_object = self.get_associated_object(field["associated_with"])
            if isinstance(associated_object, dict):
                delivery_data[field["name"]] = associated_object.get(field["name"], None)
            else:
                delivery_data[field["name"]] = getattr(associated_object, field["name"], None)

        return delivery_data

    def validate(self) -> None:
        self.validation_errors = {}
        for required_field in self.delivery_mechanism_required_fields_definitions:
            associated_object = self.get_associated_object(required_field["associated_with"])
            if isinstance(associated_object, dict):
                value = associated_object.get(required_field["name"], None)
            else:
                value = getattr(associated_object, required_field["name"], None)
            if value in [None, ""]:
                self.validation_errors[required_field["name"]] = str(self.VALIDATION_ERROR_MISSING_DATA)
                self.is_valid = False
        if not self.validation_errors:
            self.is_valid = True

    def update_unique_field(self) -> None:
        if self.is_valid and hasattr(self, "unique_fields") and isinstance(self.unique_fields, (list, tuple)):
            sha256 = hashlib.sha256()
            sha256.update(self.individual.program.name.encode("utf-8"))

            for field_name in self.unique_fields:
                value = self.delivery_data.get(field_name, None)
                sha256.update(str(value).encode("utf-8"))

            unique_key = sha256.hexdigest()
            possible_duplicates = self.__class__.all_objects.filter(
                is_valid=True,
                unique_key__isnull=False,
                unique_key=unique_key,
                individual__program=self.individual.program,
                individual__withdrawn=False,
                individual__duplicate=False,
            ).exclude(pk=self.pk)

            if possible_duplicates.exists():
                self.unique_key = None
                self.is_valid = False
                for field_name in self.unique_fields:
                    self.validation_errors[field_name] = str(self.VALIDATION_ERROR_DATA_NOT_UNIQUE)
                self.possible_duplicate_of = possible_duplicates.first()
            else:
                self.unique_key = unique_key

    @property
    def delivery_mechanism_all_fields_definitions(self) -> List[dict]:
        all_core_fields = get_core_fields_attributes()
        return [field for field in all_core_fields if field["name"] in self.all_fields]

    @property
    def delivery_mechanism_required_fields_definitions(self) -> List[dict]:
        all_core_fields = get_core_fields_attributes()
        return [field for field in all_core_fields if field["name"] in self.required_fields]

    @property
    def all_fields(self) -> List[dict]:
        return self.delivery_mechanism.all_fields

    @property
    def all_dm_fields(self) -> List[dict]:
        return self.delivery_mechanism.all_dm_fields

    @property
    def unique_fields(self) -> List[str]:
        return self.delivery_mechanism.unique_fields

    @property
    def required_fields(self) -> List[str]:
        return self.delivery_mechanism.required_fields

    @classmethod
    def get_all_delivery_mechanisms_fields(cls, by_xlsx_name: bool = False) -> List[str]:
        fields = []
        for dm in DeliveryMechanism.objects.filter(is_active=True):
            fields.extend([f for f in dm.all_dm_fields if f not in fields])

        if by_xlsx_name:
            return [f"{field}_i_c" for field in fields]

        return fields

    @classmethod
    def get_scope_delivery_mechanisms_fields(cls, by: str = "name") -> List[str]:
        from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
            FieldFactory,
        )
        from hct_mis_api.apps.core.field_attributes.fields_types import Scope

        delivery_mechanisms_fields = list(FieldFactory.from_scope(Scope.DELIVERY_MECHANISM).to_dict_by(by).keys())

        return delivery_mechanisms_fields

    def get_grievance_ticket_payload_for_errors(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "label": self.delivery_mechanism.name,
            "approve_status": False,
            "data_fields": [
                {
                    "name": field,
                    "value": None,
                    "previous_value": self.delivery_data.get(field),
                }
                for field, value in self.validation_errors.items()
            ],
        }

    def revalidate_for_grievance_ticket(self, grievance_ticket: "GrievanceTicket") -> None:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        self.refresh_from_db()
        self.validate()
        if not self.is_valid:
            grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
            description = (
                f"Missing required fields {list(self.validation_errors.keys())}"
                f" values for delivery mechanism {self.delivery_mechanism.name}"
            )
            grievance_ticket.description = description
            individual_data_with_approve_status = self.get_grievance_ticket_payload_for_errors()
            grievance_ticket.individual_data_update_ticket_details.individual_data = {
                "delivery_mechanism_data_to_edit": [individual_data_with_approve_status]
            }
            grievance_ticket.individual_data_update_ticket_details.save()
            grievance_ticket.save()
        else:
            self.update_unique_field()
            if not self.is_valid:
                grievance_ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
                description = (
                    f"Fields not unique {list(self.validation_errors.keys())} across program"
                    f" for delivery mechanism {self.delivery_mechanism.name}, possible duplicate of {self.possible_duplicate_of}"
                )
                grievance_ticket.description = description
                individual_data_with_approve_status = self.get_grievance_ticket_payload_for_errors()
                grievance_ticket.individual_data_update_ticket_details.individual_data = {
                    "delivery_mechanism_data_to_edit": [individual_data_with_approve_status]
                }
                grievance_ticket.individual_data_update_ticket_details.save()
                grievance_ticket.save()


class PendingDeliveryMechanismData(DeliveryMechanismData):
    objects: PendingManager = PendingManager()  # type: ignore

    class Meta:
        proxy = True
        verbose_name = "Imported Delivery Mechanism Data"
        verbose_name_plural = "Imported Delivery Mechanism Datas"


class DeliveryMechanism(TimeStampedUUIDModel):
    class TransferType(models.TextChoices):
        CASH = "CASH", "Cash"
        VOUCHER = "VOUCHER", "Voucher"
        DIGITAL = "DIGITAL", "Digital"

    payment_gateway_id = models.CharField(max_length=255, unique=True, null=True)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    optional_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    required_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    unique_fields = ArrayField(default=list, base_field=models.CharField(max_length=255))
    is_active = models.BooleanField(default=True)
    transfer_type = models.CharField(max_length=255, choices=TransferType.choices, default=TransferType.CASH)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["code"]
        verbose_name = "Delivery Mechanism"
        verbose_name_plural = "Delivery Mechanisms"

    def get_label_for_field(self, field: str) -> str:
        return (
            " ".join(word.capitalize() for word in field.replace("__", "_").split("_"))
            + f" ({self.name} Delivery Mechanism)"
        )

    @property
    def all_fields(self) -> List[str]:
        return self.required_fields + self.optional_fields

    @property
    def all_dm_fields(self) -> List[str]:
        core_fields = [cf["name"] for cf in CORE_FIELDS_ATTRIBUTES]
        return [field for field in self.all_fields if field not in core_fields]

    def get_core_fields_definitions(self) -> List[dict]:
        core_fields = [cf["name"] for cf in CORE_FIELDS_ATTRIBUTES]
        return [
            {
                "id": str(uuid.uuid4()),
                "type": TYPE_STRING,
                "name": field,
                "lookup": field,
                "required": False,
                "label": {"English(EN)": self.get_label_for_field(field)},
                "hint": "",
                "choices": [],
                "associated_with": _DELIVERY_MECHANISM_DATA,
                "required_for_payment": field in self.required_fields,
                "unique_for_payment": field in self.unique_fields,
                "xlsx_field": f"{field}_i_c",
                "scope": [Scope.XLSX, Scope.XLSX_PEOPLE, Scope.DELIVERY_MECHANISM],
            }
            for field in self.all_fields
            if field not in core_fields
        ]

    @classmethod
    def get_all_core_fields_definitions(cls) -> List[dict]:
        definitions = []
        for delivery_mechanism in cls.objects.filter(is_active=True).order_by("code"):
            definitions.extend(delivery_mechanism.get_core_fields_definitions())
        return definitions

    @classmethod
    def get_choices(cls, only_active: bool = True) -> List[Tuple[str, str]]:
        dms = cls.objects.all().values_list("code", "name")
        if only_active:
            dms.filter(is_active=True)
        return list(dms)

    @classmethod
    def get_delivery_mechanisms_to_xlsx_fields_mapping(cls) -> Dict[str, List[str]]:
        required_fields_map = defaultdict(list)
        for dm in cls.objects.filter(is_active=True):
            required_fields_map[dm.code].extend([f"{field}_i_c" for field in dm.required_fields])

        return required_fields_map
