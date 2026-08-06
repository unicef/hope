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


def humanize_errors(errors: dict) -> dict:
    try:
        households = errors.pop("households", [])
        errs = {}
        if len(households) == 1 and isinstance(households[0], str):
            hh_info = households
        else:
            hh_info = []
            for i, h in enumerate(households, 1):
                if h and isinstance(h, dict):
                    members = h.pop("members", [])
                    mm_info: list | dict
                    if isinstance(members, list) and len(members) == 1 and isinstance(members[0], str):
                        mm_info = members
                    else:
                        mm_info = {f"Member #{i}": [m] for i, m in enumerate(members, 1) if m}
                    if mm_info:
                        h["members"] = mm_info
                if h:
                    hh_info.append({f"Household #{i}": [h]})
        if hh_info:
            errs["households"] = hh_info
        errs.update(**errors)
        return errs
    except (ValueError, AttributeError):
        return errors


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request: Any) -> None:
        return
