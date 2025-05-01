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
    AccountType,
    FinancialInstitution,
    PendingAccount,
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
        self.accounts = defaultdict(dict)

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
    ) -> None:
        if value is None:
            return

        name = header.replace("_i_c", "").replace("pp_", "")

        self.accounts[f"individual_{row_num}"]["individual"] = individual
        _account_prefix, account_type, field_name = name.split("__")
        if account_type not in self.accounts[f"individual_{row_num}"]:
            self.accounts[f"individual_{row_num}"][account_type] = {field_name: value}
        else:
            self.accounts[f"individual_{row_num}"][account_type].update({field_name: value})

    def _create_accounts(self) -> None:
        account_types_dict = {obj.key: obj for obj in AccountType.objects.all()}

        imported_delivery_mechanism_data = []
        for data in self.accounts.values():
            individual = data.pop("individual")
            for account_type, values in data.items():
                financial_institution_code = values.get("code", None)
                imported_delivery_mechanism_data.append(
                    PendingAccount(
                        individual=individual,
                        account_type=account_types_dict[account_type],
                        number=values.get("number", None),
                        financial_institution=FinancialInstitution.objects.filter(
                            code=financial_institution_code
                        ).first()
                        if financial_institution_code
                        else None,
                        data=values,
                        rdi_merge_status=MergeStatusModel.PENDING,
                    )
                )
        PendingAccount.objects.bulk_create(imported_delivery_mechanism_data)
