import random

from django.core.exceptions import ValidationError


def generate_numeric_token(digit_number: int = 3) -> int:
    while True:
        token = "".join(random.choices("1234567890", k=digit_number))
        if not token.startswith("0") and not has_repeated_digits(token):
            return int(token)


def has_repeated_digits(token: str) -> bool:
    """
    check if the token has the same digit repeated more than 3 times in a row (like 1111)
    """
    for i in range(len(token) - 3):
        if token[i] == token[i + 1] == token[i + 2] == token[i + 3]:
            return True
    return False


def payment_token_and_order_number_validator(value: int) -> None:
    if str(value).startswith("0"):
        raise ValidationError("Token and Order Number must not start with 0.")
    if has_repeated_digits(str(value)):
        raise ValidationError("Token and Order Number must not has the same digit more than 3 times in a row.")
