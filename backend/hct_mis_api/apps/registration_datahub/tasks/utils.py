def collectors_str_ids_to_list(values):
    if values is None:
        return
    return str(values).strip(";").replace(" ", "").split(";")
