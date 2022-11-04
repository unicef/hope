import logging
from typing import Any

import phonenumbers


def is_right_phone_number_format(phone_number) -> bool:
    # from phonenumbers.parse method description:
    # This method will throw a NumberParseException if the number is not
    # considered to be a possible number.
    #
    # so if `parse` does not throw, we may assume it's ok

    if not isinstance(phone_number, str):
        phone_number = str(phone_number)

    phone_number = phone_number.replace(" ", "")
    if phone_number.startswith("00"):
        phone_number = f"+{phone_number[2:]}"

    # phonenumbers lib accepts numbers such 123 123 XXX and treats them as 123 123 999 :o
    if any(char.isalpha() for char in phone_number):
        return False

    try:
        return phonenumbers.is_possible_number(phonenumbers.parse(phone_number))
    except phonenumbers.NumberParseException:
        logging.warning(f"'{phone_number}' is not a valid phone number")
        return False


def calculate_phone_numbers_validity(obj) -> Any:
    obj.phone_no_valid = is_right_phone_number_format(str(obj.phone_no))
    obj.phone_no_alternative_valid = is_right_phone_number_format(str(obj.phone_no_alternative))
    return obj


def recalculate_phone_numbers_validity(obj, model) -> Any:
    # Used like this and not as an abstract class because Individual has indexes and ImportedIndividual does not
    if current := model.objects.filter(pk=obj.pk).first():
        # update
        if current.phone_no_valid is None or current.phone_no != obj.phone_no:
            obj.phone_no_valid = is_right_phone_number_format(str(obj.phone_no))
        if current.phone_no_alternative_valid is None or current.phone_no_alternative != obj.phone_no_alternative:
            obj.phone_no_alternative_valid = is_right_phone_number_format(str(obj.phone_no_alternative))
    else:
        # create
        obj = calculate_phone_numbers_validity(obj)
    return obj
