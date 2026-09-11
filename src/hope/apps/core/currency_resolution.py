"""Turning a user-supplied currency code into a ``Currency`` row.

A redenomination leaves a deprecated and an active row sharing one ``code``, so the code alone
does not identify a row. There is no safe default: every call site picks a function below.
"""

from hope.models.currency import Currency


def resolve_active_currency(code: str) -> Currency:
    """Return the active row for ``code``, for input where the code is a choice, not an echo of a stored value."""
    return Currency.objects.get_active_by_code(code)


def resolve_active_currency_or_none(code: str) -> Currency | None:
    """:func:`resolve_active_currency`, returning ``None`` instead of raising.

    Household edits (grievance, universal update) use it: the currency there is an edited field,
    so resubmitting the code of a deprecated row moves the household onto the active one.
    """
    return Currency.objects.get_active_by_code_or_none(code)


def resolve_currency_for_update(code: str, current: Currency | None) -> Currency:
    """Return the currency to store when ``code`` is submitted for a record already on ``current``.

    An unchanged code keeps the existing row, so a record on a deprecated currency is not
    repointed onto the active one. Only a different code resolves to the active row.
    """
    if current is not None and current.code == code:
        return current
    return Currency.objects.get_active_by_code(code)
