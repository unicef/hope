import phonenumbers


def is_valid_phone_number(phone_number: object) -> bool:
    if not isinstance(phone_number, str):
        phone_number = str(phone_number)

    try:
        parsed_number = phonenumbers.parse(phone_number)
    except phonenumbers.NumberParseException:
        return False
    else:
        return phonenumbers.is_valid_number(parsed_number)


def calculate_phone_numbers_validity(obj: object) -> object:
    obj.phone_no_valid = is_valid_phone_number(str(obj.phone_no))
    obj.phone_no_alternative_valid = is_valid_phone_number(str(obj.phone_no_alternative))
    return obj


def recalculate_phone_numbers_validity(obj: object, model: type) -> object:
    if obj._state.adding is True:
        # create
        obj = calculate_phone_numbers_validity(obj)
    # Used like this and not as an abstract class because Individual has indexes and ImportedIndividual does not
    elif current := model.objects.filter(pk=obj.pk).first():
        # update
        if current.phone_no_valid is None or current.phone_no != obj.phone_no:
            obj.phone_no_valid = is_valid_phone_number(str(obj.phone_no))
        if current.phone_no_alternative_valid is None or current.phone_no_alternative != obj.phone_no_alternative:
            obj.phone_no_alternative_valid = is_valid_phone_number(str(obj.phone_no_alternative))

    return obj
