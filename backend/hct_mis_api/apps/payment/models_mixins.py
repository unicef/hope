from typing import List

from django.utils.functional import cached_property

from hct_mis_api.apps.core.field_attributes.fields_types import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    _PAYMENT_CHANNEL_DATA,
    Scope,
)


class DeliveryDataMixin:
    """Reused in registration_datahub.ImportedPaymentChannel / payment.PaymentChannel"""

    @cached_property
    def required_fields(self) -> List[str]:
        return self.delivery_mechanism.global_core_fields + self.delivery_mechanism.payment_channel_fields

    @cached_property
    def delivery_data(self) -> dict:
        from hct_mis_api.apps.core.field_attributes.core_fields_attributes import (
            FieldFactory,
        )

        associated_objects = {
            _INDIVIDUAL: self.individual,
            _HOUSEHOLD: self.individual.household,
            _PAYMENT_CHANNEL_DATA: self.payment_channel_data and self.payment_channel_data.data or {},
        }
        fields = FieldFactory.from_scopes([Scope.GLOBAL, Scope.PAYMENT_CHANNEL]).to_dict_by("name")

        delivery_data = {}
        for field_name in self.required_fields:
            associated_object = associated_objects.get(fields[field_name]["associated_with"])
            delivery_data[field_name] = getattr(associated_object, field_name, None)

        return delivery_data

    def validate(self):
        delivery_data = self.delivery_data

        for required_field in self.required_fields:
            if delivery_data.get(required_field, None) is None:
                self.is_valid = False

        self.is_valid = True
