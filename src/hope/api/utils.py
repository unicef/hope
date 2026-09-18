from enum import Enum
from typing import Any

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db import models
from django.utils.encoding import smart_str
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication

from hope.apps.core.currency_resolution import resolve_currency_for_update
from hope.models.currency import Currency


class OnUnchangedCode(Enum):
    """What a submitted code that matches the record's current currency means."""

    #: Keep the currency already on the record. For serializers that update.
    KEEP_CURRENT_ROW = "keep_current_row"
    #: Always resolve to the active row. For serializers that only ever create.
    ALWAYS_ACTIVE = "always_active"


class CurrencySlugRelatedField(serializers.SlugRelatedField):
    """Accepts an ISO ``code`` and resolves it to a ``Currency``.

    ``slug_field`` and ``queryset`` are fixed; ``on_unchanged_code`` has no default on
    purpose -- see :class:`OnUnchangedCode`.
    """

    def __init__(self, *, on_unchanged_code: OnUnchangedCode, **kwargs: Any) -> None:
        for fixed in ("slug_field", "queryset"):
            if fixed in kwargs:
                raise TypeError(
                    f"CurrencySlugRelatedField resolves by active `code`; `{fixed}` is fixed and "
                    "passing it would imply it affects validation."
                )
        self.on_unchanged_code = on_unchanged_code
        super().__init__(slug_field="code", queryset=Currency.objects.active(), **kwargs)

    def bind(self, field_name: str, parent: serializers.BaseSerializer) -> None:
        super().bind(field_name, parent)
        if self.on_unchanged_code is OnUnchangedCode.KEEP_CURRENT_ROW and len(self.source_attrs) != 1:
            # Empty for ``source="*"``, multi-valued for a dotted source: either way the field
            # cannot tell which object it is updating.
            raise ImproperlyConfigured(
                f"{parent.__class__.__name__}.{field_name}: OnUnchangedCode.KEEP_CURRENT_ROW needs a "
                f"plain source, got source={self.source!r}. Resolve the currency explicitly with "
                "hope.apps.core.currency_resolution instead."
            )

    def _current_currency(self) -> Currency | None:
        """Return the currency already attached to the object being updated.

        ``KEEP_CURRENT_ROW`` cannot tell a create from a caller that forgot the instance, so it
        requires one; a create-only serializer declares ``ALWAYS_ACTIVE`` instead.
        """
        if self.on_unchanged_code is OnUnchangedCode.ALWAYS_ACTIVE:
            return None
        instance = getattr(self.parent, "instance", None)
        if instance is None:
            raise ImproperlyConfigured(
                f"{self.parent.__class__.__name__}.{self.field_name}: OnUnchangedCode.KEEP_CURRENT_ROW "
                "needs the object being updated. Pass it as `get_serializer(instance, data=...)`, or "
                "declare OnUnchangedCode.ALWAYS_ACTIVE if this serializer only ever creates."
            )
        if isinstance(instance, (list, models.QuerySet)):
            # With ``many=True`` DRF passes the whole list down to the child serializer, so
            # there is no single object to compare against.
            raise ImproperlyConfigured(
                f"{self.parent.__class__.__name__}.{self.field_name}: OnUnchangedCode.KEEP_CURRENT_ROW "
                "cannot be used with many=True; there is no single instance to compare against."
            )
        current = getattr(instance, self.source_attrs[0], None)
        return current if isinstance(current, self.get_queryset().model) else None

    def to_internal_value(self, data: Any) -> Any:
        try:
            return resolve_currency_for_update(data, self._current_currency())
        except ObjectDoesNotExist:
            self.fail("does_not_exist", slug_name=self.slug_field, value=smart_str(data))
        except (TypeError, ValueError):
            self.fail("invalid")


def humanize_errors(errors: dict) -> dict:
    try:
        errs: dict[str, Any] = {}
        if isinstance(errors, list):
            errors = dict(enumerate(errors))
        if errors and all(isinstance(key, int) for key in errors):
            hh_info = _humanize_households(errors)
            if hh_info:
                errs["households"] = hh_info
            return errs

        households = errors.pop("households", [])
        hh_info = _humanize_households(households)
        if hh_info:
            errs["households"] = hh_info
        errs.update(**errors)
        return errs
    except (ValueError, AttributeError):
        return errors


def _humanize_households(households: Any) -> list | dict:
    if isinstance(households, str):
        return [households]
    if isinstance(households, list) and len(households) == 1 and isinstance(households[0], str):
        return households
    if isinstance(households, dict):
        hh_info_dict: dict[str, Any] = {}
        for idx, h in households.items():
            if isinstance(idx, int):
                if h and isinstance(h, dict):
                    _humanize_members(h)
                if h:
                    hh_info_dict[f"Household #{idx + 1}"] = [h]
            else:
                hh_info_dict[idx] = h
        return hh_info_dict
    hh_info_list: list[dict[str, Any]] = []
    for i, h in enumerate(households, 1):
        if h and isinstance(h, dict):
            _humanize_members(h)
        if h:
            hh_info_list.append({f"Household #{i}": [h]})
    return hh_info_list


def _humanize_members(household: dict) -> dict:
    members = household.pop("members", [])
    mm_info = _humanize_members_info(members)
    if mm_info:
        household["members"] = mm_info
    return household


def _humanize_members_info(members: Any) -> list | dict:
    if isinstance(members, str):
        return [members]
    if isinstance(members, list) and len(members) == 1 and isinstance(members[0], str):
        return members
    if isinstance(members, dict):
        return {
            (f"Member #{int(k) + 1}" if isinstance(k, int) else k): ([m] if isinstance(k, int) else m)
            for k, m in members.items()
            if m
        }
    return {f"Member #{i}": [m] for i, m in enumerate(members, 1) if m}


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request: Any) -> None:
        return
