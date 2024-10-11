import logging
from typing import Any, Union

import phonenumbers

logger = logging.getLogger(__name__)


def is_right_phone_number_format(phone_number: Union[str, Any]) -> bool:
    # from phonenumbers.parse method description:
    # This method will throw a NumberParseException if the number is not
    # considered to be a possible number.
    #
    # so if `parse` does not throw, we may assume it's ok
    if not isinstance(phone_number, str):
        phone_number = str(phone_number)

    phone_number = phone_number.strip()
    if phone_number.startswith("00"):
        phone_number = f"+{phone_number[2:]}"

    try:
        phonenumbers.parse(phone_number)
    except phonenumbers.NumberParseException:
        logger.warning(f"'{phone_number}' is not a valid phone number")
        return False
    return True
