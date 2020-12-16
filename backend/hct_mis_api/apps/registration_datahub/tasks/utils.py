def collectors_str_ids_to_list(values):
    if values is None:
        return

    if isinstance(values, float) and values.is_integer():
        temp_value = int(values)
        return str(temp_value)
    else:
        return str(values).strip(";").replace(" ", "").split(";")
