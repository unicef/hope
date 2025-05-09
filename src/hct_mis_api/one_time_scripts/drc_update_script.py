from typing import Any

from django.db import transaction

from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.universal_individual_update_script.universal_individual_update_script import (
    UniversalIndividualUpdateScript,
)
from hct_mis_api.one_time_scripts.universal_individual_update_script.validator_and_handlers import (
    handle_simple_field,
    validate_phone_number,
)

individual_fields: dict[str, tuple[str, Any, Any]] = {
    "phone_no": ("phone_no", validate_phone_number, handle_simple_field),
    "payment_delivery_phone_no_i_c": ("payment_delivery_phone_no", validate_phone_number, handle_simple_field),
}

deliver_mechanism_data_fields: dict[str, tuple[list[str], ...]] = {
    "mobile_money": (
        ["service_provider_code__mobile_money_i_c", "service_provider_code__mobile_money"],
        ["provider__mobile_money_i_c", "provider__mobile_money"],
        ["payment_delivery_phone_no_i_c", "delivery_phone_number__mobile_money"],
    )
}


@transaction.atomic
def drc_update_script(file_path: str, program_id: str, batch_size: int) -> None:
    program = Program.objects.get(id=program_id)
    business_area = program.business_area
    update = UniversalIndividualUpdateScript(
        business_area,
        program,
        file_path,
        individual_fields=individual_fields,
        deliver_mechanism_data_fields=deliver_mechanism_data_fields,
        deduplicate_documents=True,
        deduplicate_es=True,
        batch_size=batch_size,
    )
    update.execute()
