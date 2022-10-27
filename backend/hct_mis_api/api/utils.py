from typing import List


def humanize_errors(errors: List) -> List:
    try:
        households = errors.pop("households")
        errs = {}
        if len(households) == 1 and isinstance(households[0], str):
            hh_info = households
        else:
            hh_info = []
            for i, h in enumerate(households, 1):
                if h and isinstance(h, dict):
                    members = h.pop("members", [])
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
