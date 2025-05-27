from typing import Any, Dict, List, Tuple

from django.db import transaction

from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.universal_individual_update_script.universal_individual_update_script import \
    UniversalIndividualUpdateScript
from hct_mis_api.one_time_scripts.universal_individual_update_script.validator_and_handlers import (
    handle_admin_field, handle_simple_field, validate_admin, validate_date,
    validate_flex_field_string, validate_phone_number, validate_sex,
    validate_string)

household_fields: Dict[str, Tuple[str, Any, Any]] = {
    "admin1_h_c": ("admin1", validate_admin, handle_admin_field),
    "admin2_h_c": ("admin2", validate_admin, handle_admin_field),
    "admin3_h_c": ("admin3", validate_admin, handle_admin_field),
}

individual_fields: Dict[str, Tuple[str, Any, Any]] = {
    "given_name_i_c": ("given_name", validate_string, handle_simple_field),
    "middle_name_i_c": ("middle_name", validate_string, handle_simple_field),
    "family_name_i_c": ("family_name", validate_string, handle_simple_field),
    "full_name_i_c": ("full_name", validate_string, handle_simple_field),
    "birth_date": ("birth_date", validate_date, handle_simple_field),
    "sex": ("sex", validate_sex, handle_simple_field),
    "pp_phone_no_i_c": ("phone_no", validate_phone_number, handle_simple_field),
}

individual_flex_fields: Dict[str, Tuple[str, Any, Any]] = {
    "ss_hw_lot_num_i_f": ("ss_hw_lot_num_i_f", validate_flex_field_string, handle_simple_field),
    "ss_health_facility_name_i_f": ("ss_health_facility_name_i_f", validate_flex_field_string, handle_simple_field),
    "ss_hw_title_i_f": ("ss_hw_title_i_f", validate_flex_field_string, handle_simple_field),
    "ss_hw_work_id_i_f": ("ss_hw_work_id_i_f", validate_flex_field_string, handle_simple_field),
    "ss_hw_grade_i_f": ("ss_hw_grade_i_f", validate_flex_field_string, handle_simple_field),
    "ss_hw_qualifications_i_f": ("ss_hw_qualifications_i_f", validate_flex_field_string, handle_simple_field),
    "ss_hw_cadre_i_f": ("ss_hw_cadre_i_f", validate_flex_field_string, handle_simple_field),
}

document_fields: List[Tuple[str, str]] = [
    ("national_id_no_i_c", "national_id_country_i_c"),
    ("birth_certificate_no_i_c", "birth_certificate_country_i_c"),
]


@transaction.atomic
def south_sudan_update_script(file_path: str, program_id: str, batch_size: int) -> None:
    program = Program.objects.get(id=program_id)
    business_area = program.business_area
    update = UniversalIndividualUpdateScript(
        business_area,
        program,
        file_path,
        household_fields=household_fields,
        individual_fields=individual_fields,
        individual_flex_fields=individual_flex_fields,
        document_fields=document_fields,
        deduplicate_documents=True,
        deduplicate_es=True,
        batch_size=batch_size,
    )
    update.execute()
