from typing import Any, Dict, List, Union


def collectors_str_ids_to_list(values: Any) -> Union[None, str, List[str]]:
    # TODO: refactor that?
    if values is None:
        return None

    if isinstance(values, float) and values.is_integer():
        temp_value = int(values)
        return str(temp_value)
    else:
        return str(values).strip(";").replace(" ", "").split(";")


def get_submission_metadata(household_data_dict: Dict) -> Dict:
    meta_fields_mapping = {
        "_uuid": "kobo_submission_uuid",
        "_xform_id_string": "kobo_asset_id",
        "_submission_time": "kobo_submission_time",
    }
    submission_meta_data = {}
    for meta_field, model_field_name in meta_fields_mapping.items():
        submission_meta_data[model_field_name] = household_data_dict.get(meta_field)

    return submission_meta_data
