from typing import Any


def collectors_str_ids_to_list(values: Any) -> None | str | list[str]:
    # TODO: refactor that?
    if values is None:
        return None

    if isinstance(values, float) and values.is_integer():
        temp_value = int(values)
        return [str(temp_value)]
    return str(values).strip(";").replace(" ", "").split(";")
