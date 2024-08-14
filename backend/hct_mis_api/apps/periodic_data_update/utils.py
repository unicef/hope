import re


def field_label_to_field_name(input_string: str) -> str:
    """
    Convert a field label to a field name.
    Change " " into "_", remove special characters and convert to lowercase.
    """

    input_string = input_string.replace(" ", "_")
    input_string = re.sub(r"[^\w]", "", input_string)
    input_string = re.sub(r"__+", "_", input_string)
    input_string = input_string.strip("_")
    return input_string.lower()
