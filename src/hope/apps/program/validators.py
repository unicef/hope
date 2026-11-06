from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hope.models import BeneficiaryGroup, DataCollectingType, Program


def get_payee_configuration_errors(
    data_collecting_type: DataCollectingType,
    beneficiary_group: BeneficiaryGroup,
    *,
    previous_program: Program | None = None,
) -> dict[str, str]:
    data_collecting_type_changed = (
        previous_program is None or previous_program.data_collecting_type_id != data_collecting_type.pk
    )
    beneficiary_group_changed = (
        previous_program is None or previous_program.beneficiary_group_id != beneficiary_group.pk
    )
    if not (data_collecting_type_changed or beneficiary_group_changed):
        return {}

    payee_type = data_collecting_type.payee_type
    if payee_type is None:
        return {"data_collecting_type": "Data Collecting Type has no Payee Type."}

    errors: dict[str, str] = {}
    payee_type_changed = (
        previous_program is None or previous_program.data_collecting_type.payee_type_id != payee_type.pk
    )
    if payee_type_changed and not payee_type.active:
        errors["data_collecting_type"] = "Payee Type of the selected Data Collecting Type is inactive."
    if beneficiary_group.payee_type_id != payee_type.pk:
        errors["beneficiary_group"] = "Payee Label does not belong to the selected Payee Type."
    elif (
        beneficiary_group.data_collecting_types.exists()
        and not beneficiary_group.data_collecting_types.filter(pk=data_collecting_type.pk).exists()
    ):
        errors["beneficiary_group"] = "Payee Label is not permitted for the selected Data Collecting Type."
    elif beneficiary_group_changed and not beneficiary_group.active:
        errors["beneficiary_group"] = "Only active Payee Label can be used in Program."
    return errors
