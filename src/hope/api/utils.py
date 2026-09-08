from typing import Any

from django.utils.encoding import smart_str
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication


class CurrencySlugRelatedField(serializers.SlugRelatedField):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(slug_field="code", **kwargs)

    def to_internal_value(self, data: Any) -> Any:
        queryset = self.get_queryset()
        try:
            return queryset.resolve_code(data)
        except queryset.model.DoesNotExist:
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
