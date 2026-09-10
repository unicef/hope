"""Turning a user-supplied currency code into a ``Currency`` row.

A redenomination leaves a deprecated and an active row sharing one ``code``, so the code alone
does not identify a row. There is no safe default: every call site picks a function below.
"""

from hope.models.currency import Currency


def resolve_active_currency(code: str) -> Currency:
    """Return the active row for ``code``, for input that creates a record rather than updating it."""
    return Currency.objects.get_active_by_code(code)


def resolve_currency_for_update(code: str, current: Currency | None) -> Currency:
    """Return the currency to store when ``code`` is submitted for a record already on ``current``.

    An unchanged code keeps the existing row, so a record on a deprecated currency is not
    repointed onto the active one. Only a different code resolves to the active row.
    """
    if current is not None and current.code == code:
        return current
    return Currency.objects.get_active_by_code(code)


def resolve_currency_for_update_or_none(code: str, current: Currency | None) -> Currency | None:
    """:func:`resolve_currency_for_update`, returning ``None`` instead of raising.

    Only for call sites that validate the code at their own input boundary.
    """
    if current is not None and current.code == code:
        return current
    return Currency.objects.get_active_by_code_or_none(code)
