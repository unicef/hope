import hashlib
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.kobo.common import get_field_name
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program


def post_process_dedupe_results(record: Any) -> None:
    max_score = 0
    min_score = sys.maxsize
    for field in [record.deduplication_batch_results, record.deduplication_golden_record_results]:
        if "duplicates" in field:
            duplicates = field["duplicates"]
            for entry in field["duplicates"]:
                max_score = max(max_score, entry["score"])
                min_score = min(min_score, entry["score"])
            field["score"] = {"max": max_score, "min": min_score, "qty": len(duplicates)}


def combine_collections(a: Dict, b: Dict, path: Optional[List] = None, update: bool = True) -> Dict:
    """merges b into a
    version from flex registration"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                combine_collections(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx in range(len(b[key])):
                    a[key][idx] = combine_collections(
                        a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update
                    )
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def find_attachment_in_kobo(attachments: List[Dict], value: str) -> Optional[Dict]:
    file_extension = value.split(".")[-1]
    filename = re.escape(".".join(value.split(".")[:-1]))
    regex_name = re.compile(f"{filename}(_\\w+)?\\.{file_extension}")
    for attachment in attachments:
        if regex_name.match(get_field_name(attachment["filename"])):
            return attachment
    return None


def calculate_hash_for_kobo_submission(submission: Dict) -> str:
    keys_to_remove = [
        "_id",
        "start",
        "end",
        "_submission_time",
        "_attachments",
    ]
    submission_copy = submission.copy()
    for key in keys_to_remove:
        if key in submission_copy:
            del submission_copy[key]

    d_string = json.dumps(submission_copy, sort_keys=True)
    d_bytes = d_string.encode("utf-8")
    hash_object = hashlib.sha256(d_bytes)
    hex_dig = hash_object.hexdigest()
    return hex_dig


def get_rdi_program_population(
    import_from_program_id: str, import_to_program_id: str, import_from_ids: Optional[str]
) -> Tuple[QuerySet[Household], QuerySet[Individual]]:
    program = get_object_or_404(Program, pk=import_to_program_id)

    # filter by rdi.import_from_ids HH or Ins ids based on Program.DCT
    list_of_ids = [item.strip() for item in import_from_ids.split(",")] if import_from_ids else []
    if list_of_ids:
        # add Individuals who can have any role in household
        ind_ids_with_role = list(
            IndividualRoleInHousehold.objects.filter(household__unicef_id__in=list_of_ids)
            .exclude(Q(individual__withdrawn=True) | Q(individual__duplicate=True))
            .values_list("individual__unicef_id", flat=True)
        )

        individual_ids_q = (
            Q(unicef_id__in=list_of_ids + ind_ids_with_role)
            if program.is_social_worker_program
            else Q(Q(household__unicef_id__in=list_of_ids) | Q(unicef_id__in=ind_ids_with_role))
        )
        household_ids_q = (
            Q(unicef_id__in=list_of_ids)
            if not program.is_social_worker_program
            else Q(individuals__unicef_id__in=list_of_ids)
        )
    else:
        individual_ids_q = Q()
        household_ids_q = Q()

    households_to_exclude = Household.all_merge_status_objects.filter(
        program=import_to_program_id,
    ).values_list("unicef_id", flat=True)
    households = (
        Household.objects.filter(
            household_ids_q,
            program_id=import_from_program_id,
            withdrawn=False,
        )
        .exclude(unicef_id__in=households_to_exclude)
        .distinct()
    )
    individuals_to_exclude = Individual.all_merge_status_objects.filter(
        program=import_to_program_id,
    ).values_list("unicef_id", flat=True)
    individuals = (
        Individual.objects.filter(
            individual_ids_q,
            program_id=import_from_program_id,
            withdrawn=False,
            duplicate=False,
        )
        .exclude(unicef_id__in=individuals_to_exclude)
        .distinct()
        .order_by("first_registration_date")
    )
    return households, individuals
