import logging
from collections import defaultdict
from functools import reduce
from typing import List

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.utils import (
    get_combined_attributes,
    serialize_flex_attributes,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.registration_datahub.models import (
    ImportedPaymentChannel,
    ImportedPaymentChannelData,
)
from hct_mis_api.apps.registration_datahub.value_caster import (
    BooleanValueCaster,
    DateValueCaster,
    DecimalValueCaster,
    DefaultValueCaster,
    IntegerValueCaster,
    SelectManyValueCaster,
    SelectOneValueCaster,
    StringValueCaster,
)

logger = logging.getLogger(__name__)


class RdiPaymentChannelCreationMixin:
    def __init__(self):
        self.payment_channels_data = defaultdict(dict)
        self.delivery_mechanisms = DeliveryMechanism.objects.all()
        self.payment_channel_xlsx_fields: List[str] = self.get_payment_channel_related_fields()
        super().__init__()

    def get_payment_channel_related_fields(self) -> List[str]:
        payment_channel_fields = list(
            self.delivery_mechanisms.values_list("payment_channel_fields", flat=True).distinct()
        )
        available_fields_from_dms = [field for field_list in payment_channel_fields for field in field_list]
        fields_by_name = FieldFactory.from_scopes([Scope.PAYMENT_CHANNEL]).to_dict_by("name")

        return [fields_by_name[field]["xlsx_field"] for field in available_fields_from_dms]

    def _create_payment_channels(self):
        payment_channels_data_to_create = []
        payment_channels_to_create = []

        for individual in self.individuals:
            payment_channel_data = self.payment_channels_data.get(individual.id, {})
            payment_channel_data_instance = ImportedPaymentChannelData(data=payment_channel_data, individual=individual)
            payment_channels_data_to_create.append(payment_channel_data_instance)

        ImportedPaymentChannelData.objects.bulk_create(payment_channels_data_to_create)

        for individual, payment_channel_data_instance in zip(self.individuals, payment_channels_data_to_create):
            for delivery_mechanism in self.delivery_mechanisms:
                payment_channel = ImportedPaymentChannel(
                    individual=individual,
                    payment_channel_data=payment_channel_data_instance,
                    delivery_mechanism_id=delivery_mechanism.id,
                )
                payment_channel.validate()
                if payment_channel.is_valid:
                    payment_channels_to_create.append(payment_channel)

        ImportedPaymentChannel.objects.bulk_create(payment_channels_to_create)


class RdiBaseCreateTask:
    COMBINED_FIELDS = get_combined_attributes()
    FLEX_FIELDS = serialize_flex_attributes()

    @staticmethod
    def _assign_admin_areas_titles(household_obj):
        if household_obj.admin1:
            admin_area_level_1 = Area.objects.filter(p_code=household_obj.admin1).first()
            household_obj.admin1_title = getattr(admin_area_level_1, "name", "")
        if household_obj.admin2:
            admin_area_level_2 = Area.objects.filter(p_code=household_obj.admin2).first()
            household_obj.admin2_title = getattr(admin_area_level_2, "name", "")

        return household_obj

    def _cast_value(self, value, header):
        if isinstance(value, str):
            value = value.strip()

        if not value:
            return value

        field = self.COMBINED_FIELDS[header]

        casters = [
            DefaultValueCaster(),
            BooleanValueCaster,
            SelectOneValueCaster,
            SelectManyValueCaster,
            DecimalValueCaster,
            IntegerValueCaster,
            DateValueCaster,
            StringValueCaster,
        ]

        value_caster = reduce(lambda next_caster, caster: caster(next_caster), casters)
        return value_caster.cast(field, value)
