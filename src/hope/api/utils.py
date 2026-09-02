from typing import Any

from rest_framework.authentication import SessionAuthentication


def humanize_errors(errors: dict) -> dict:
    try:
        households = errors.pop("households", [])
        errs = {}
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
            if h and isinstance(h, dict):
                _humanize_members(h)
            if h:
                hh_info_dict[f"Household #{idx}"] = [h]
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
        return {f"Member #{k}": [m] for k, m in members.items() if m}
    return {f"Member #{i}": [m] for i, m in enumerate(members, 1) if m}


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request: Any) -> None:
        return
