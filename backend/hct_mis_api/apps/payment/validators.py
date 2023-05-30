import random
import re

from django.core.exceptions import ValidationError


def generate_numeric_token(digit_number: int = 3) -> int:
    while True:
        # Token and Order Number must not start with 0
        token = random.randint(10 ** (digit_number - 1), (10**digit_number) - 1)
        # Token and Order Number must not have the same digit more than 3 times in a row
        if not has_repeated_digits_more_than_3_times(token):
            return token


def has_repeated_digits_more_than_3_times(token: int) -> bool:
    """
    check if the token has the same digit repeated more than 3 times in a row (like 1111)
    """
    pattern = r"(\d)\1{3,}"
    return bool(re.search(pattern, str(token)))


def payment_token_and_order_number_validator(value: int) -> None:
    if has_repeated_digits_more_than_3_times(value):
        raise ValidationError("Token and Order Number must not have the same digit more than 3 times in a row.")
