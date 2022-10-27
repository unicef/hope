import decimal
from typing import Any, Dict, List

from hct_mis_api.apps.core.utils import nested_getattr


def field_list_to_dict(field_list: List) -> Dict:
    return {field: field for field in field_list}


def create_mapping_dict(simple_mapping, complex_mapping=None) -> Dict:
    concatenated_dict = {}
    concatenated_dict.update({field: field for field in simple_mapping})
    if complex_mapping is not None:
        concatenated_dict.update(complex_mapping)
    return concatenated_dict


def create_diff(old_object, new_object, mapping) -> Dict:
    changes_dict = {}
    for (field_name, repr_name) in mapping.items():
        old_value = None
        new_value = None
        if old_object:
            old_value = nested_getattr(old_object, field_name, None)
        if new_object:
            new_value = nested_getattr(new_object, field_name, None)
        if old_value is None and isinstance(new_value, str) and len(new_value) == 0:
            continue

        if isinstance(old_value, decimal.Decimal):
            old_value = old_value.normalize()

        if isinstance(new_value, decimal.Decimal):
            new_value = new_value.normalize()

        if str(old_value) == str(new_value):
            continue
        change: Dict[str, Any] = {"from": None, "to": None}
        if old_value is not None:
            change["from"] = str(old_value)
        if new_value is not None:
            change["to"] = str(new_value)
        changes_dict[repr_name] = change
    return changes_dict


def copy_model_object(model_object) -> Dict:
    model_dict = {}
    model_dict.update(model_object.__dict__)
    if "_state" in model_dict:
        del model_dict["_state"]
    if "_django_version" in model_dict:
        del model_dict["_django_version"]
    return model_object.__class__(**model_dict)
