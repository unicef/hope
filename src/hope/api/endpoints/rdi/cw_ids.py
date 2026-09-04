from collections import Counter
from collections.abc import Iterable
from typing import TYPE_CHECKING

from hope.models import Individual

if TYPE_CHECKING:
    from hope.models import BusinessArea


def duplicated_cw_ids(cw_ids: Iterable[str]) -> set[str]:
    """Country workspace ids appearing more than once in a single payload.

    Expects non-empty ids; the ``collect_*`` helpers below drop the empty ones.
    """
    return {cw_id for cw_id, count in Counter(cw_ids).items() if count > 1}


def existing_cw_ids(
    business_area: "BusinessArea",
    cw_ids: Iterable[str],
    exclude_originating_ids: Iterable[str] | None = None,
) -> set[str]:
    """Country workspace ids already taken by a live individual in this business area.

    Mirrors ``country_workspace_id_ind_unique_constraint``: withdrawn and soft-deleted
    individuals do not hold their id. ``exclude_originating_ids`` covers the lax re-push
    flow, where the rows holding those ids are hard-deleted before the new ones are created.
    Expects non-empty ids; the ``collect_*`` helpers below drop the empty ones.
    """
    cw_ids = list(cw_ids)
    if not cw_ids:
        return set()
    queryset = Individual.all_objects.filter(
        business_area=business_area,
        is_removed=False,
        withdrawn=False,
        country_workspace_id__in=cw_ids,
    )
    if exclude_originating_ids:
        queryset = queryset.exclude(originating_id__in=exclude_originating_ids)
    return set(queryset.values_list("country_workspace_id", flat=True))


def collect_cw_ids(request_data: Iterable[object]) -> list[str]:
    """Country workspace ids of a flat individual payload, cast the way the serializer casts them."""
    return [
        str(cw_id)
        for row in request_data
        if isinstance(row, dict) and isinstance(cw_id := row.get("country_workspace_id"), str | int) and cw_id != ""
    ]


def collect_originating_ids(request_data: Iterable[object]) -> set[str]:
    """Originating ids of a flat individual payload, i.e. the rows a re-push replaces."""
    return {row["originating_id"] for row in request_data if isinstance(row, dict) and row.get("originating_id")}


def collect_member_cw_ids(request_data: Iterable[object]) -> list[str]:
    """Country workspace ids of every member across a nested household payload."""
    cw_ids = []
    for household in request_data:
        if not isinstance(household, dict):
            continue
        for member in household.get("members") or []:
            if not isinstance(member, dict):
                continue
            cw_id = member.get("country_workspace_id")
            if isinstance(cw_id, str | int) and cw_id != "":
                cw_ids.append(str(cw_id))
    return cw_ids


def cw_id_error(cw_id: object, existing: set[str], duplicated: set[str]) -> dict | None:
    """Build the DRF error body for one country workspace id, or None when it is free."""
    cw_id = str(cw_id)
    if cw_id in existing:
        return {
            "country_workspace_id": [
                f"Individual with country_workspace_id '{cw_id}' already exists in this business area."
            ]
        }
    if cw_id in duplicated:
        return {"country_workspace_id": [f"country_workspace_id '{cw_id}' is duplicated within this payload."]}
    return None
