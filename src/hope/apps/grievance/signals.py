from typing import Any

from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import Signal, receiver

from hope.api.caches import get_or_create_cache_key, increment_cache_key
from hope.apps.grievance.models import GrievanceTicket

individual_added = Signal()
individual_marked_as_duplicated = Signal()
individual_marked_as_distinct = Signal()


def increment_grievance_ticket_version_cache(business_area_slug: str, program_codes: set[str]) -> None:
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

    for program_code in program_codes:
        version_key = f"{business_area_slug}:{business_area_version}:{program_code}:grievance_ticket_list"
        increment_cache_key(version_key)


def increment_grievance_ticket_version_cache_for_ticket_ids(
    business_area_slug: str,
    ticket_ids: list[str],
) -> None:
    program_codes = set(
        GrievanceTicket.programs.through.objects.filter(grievanceticket_id__in=ticket_ids).values_list(
            "program__slug",
            flat=True,
        )
    )
    if program_codes:
        increment_grievance_ticket_version_cache(business_area_slug, program_codes)


@receiver(post_save, sender=GrievanceTicket)
@receiver(pre_delete, sender=GrievanceTicket)
def increment_grievance_ticket_version_cache_on_save_delete(
    sender: Any, instance: GrievanceTicket, **kwargs: dict
) -> None:
    program_codes = set(instance.programs.values_list("slug", flat=True))
    if program_codes:
        increment_grievance_ticket_version_cache(instance.business_area.slug, program_codes)


@receiver(m2m_changed, sender=GrievanceTicket.programs.through)
def increment_grievance_ticket_version_cache_on_program_change(
    sender: Any,
    instance: GrievanceTicket,
    action: str,
    reverse: bool,
    **kwargs: dict,
) -> None:
    if reverse:
        return

    model = kwargs.get("model")
    pk_set = kwargs.get("pk_set")

    if action in {"post_add", "post_remove"} and pk_set:
        program_codes = set(model.objects.filter(pk__in=pk_set).values_list("slug", flat=True))
    elif action == "pre_clear":
        program_codes = set(instance.programs.values_list("slug", flat=True))
    else:
        return

    if program_codes:
        increment_grievance_ticket_version_cache(instance.business_area.slug, program_codes)
