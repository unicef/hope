from typing import Any, List, Union


def collectors_str_ids_to_list(values: Any) -> Union[None, str, List[str]]:
    # TODO: refactor that?
    if values is None:
        return None

    if isinstance(values, float) and values.is_integer():
        temp_value = int(values)
        return [str(temp_value)]
    else:
        return str(values).strip(";").replace(" ", "").split(";")
