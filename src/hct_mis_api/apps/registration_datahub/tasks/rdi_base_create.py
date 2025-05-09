import logging
from collections import defaultdict
from functools import reduce
from typing import Any

from hct_mis_api.apps.core.utils import (
    get_combined_attributes,
    serialize_flex_attributes,
)
from hct_mis_api.apps.household.models import PendingIndividual
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    PendingDeliveryMechanismData,
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
from hct_mis_api.apps.utils.models import MergeStatusModel

logger = logging.getLogger(__name__)


class RdiBaseCreateTask:
    def __init__(self) -> None:
        self.COMBINED_FIELDS = get_combined_attributes()
        self.FLEX_FIELDS = serialize_flex_attributes()
        self.delivery_mechanisms_data = defaultdict(dict)
        self.delivery_mechanisms_required_fields_map = (
            DeliveryMechanism.get_delivery_mechanisms_to_xlsx_fields_mapping()
        )
        self.available_delivery_mechanisms = DeliveryMechanism.objects.filter(is_active=True).in_bulk(field_name="code")

    def _cast_value(self, value: Any, header: str) -> Any:
        if isinstance(value, str):
            value = value.strip()

        if not value:
            return value

        field = self.COMBINED_FIELDS[header]

        casters: list = [
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

    def _handle_delivery_mechanism_fields(
        self,
        value: Any,
        header: str,
        row_num: int,
        individual: PendingIndividual,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if value is None:
            return

        name = header.replace("pp_", "")

        self.delivery_mechanisms_data[f"individual_{row_num}"]["individual"] = individual
        for delivery_mechanism, required_fields in self.delivery_mechanisms_required_fields_map.items():
            if name in required_fields:
                name = name.replace("_i_c", "")
                if delivery_mechanism not in self.delivery_mechanisms_data[f"individual_{row_num}"]:
                    self.delivery_mechanisms_data[f"individual_{row_num}"][delivery_mechanism] = {name: value}
                else:
                    self.delivery_mechanisms_data[f"individual_{row_num}"][delivery_mechanism].update({name: value})

    def _create_delivery_mechanisms_data(self) -> None:
        imported_delivery_mechanism_data = []
        for _, data in self.delivery_mechanisms_data.items():
            individual = data.pop("individual")
            for delivery_type, values in data.items():
                imported_delivery_mechanism_data.append(
                    PendingDeliveryMechanismData(
                        individual=individual,
                        delivery_mechanism=self.available_delivery_mechanisms[delivery_type],
                        data=values,
                        rdi_merge_status=MergeStatusModel.PENDING,
                    )
                )
        PendingDeliveryMechanismData.objects.bulk_create(imported_delivery_mechanism_data)
