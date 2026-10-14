import logging
from typing import Any

from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.signals import population_delete_signals_muted
from hope.apps.utils.elasticsearch_utils import remove_elasticsearch_documents_by_matching_ids
from hope.models import Household, Individual, Program, RegistrationDataImport

logger = logging.getLogger(__name__)


def _remove_rdi_elasticsearch_documents(
    program: Program | None,
    individual_ids: list[Any],
    household_ids: list[Any],
) -> None:
    """Remove an RDI's Elasticsearch documents (ACTIVE programs only)."""
    if not program or program.status != Program.ACTIVE:
        return
    remove_elasticsearch_documents_by_matching_ids(individual_ids, get_individual_doc(str(program.id)))
    remove_elasticsearch_documents_by_matching_ids(household_ids, get_household_doc(str(program.id)))


def remove_rdi_population(
    rdi: RegistrationDataImport,
    *,
    delete_rdi: bool,
    swallow_es_errors: bool = False,
) -> None:
    """Remove an RDI's population and Elasticsearch docs.

    When ``delete_rdi`` is True it also drops the RDI row.

    The deletes run with the per-row Household/Individual delete receivers muted: the cascade
    would otherwise queue one cache increment and one Elasticsearch delete-by-query per row,
    duplicating the bulk cleanup below. The list caches are invalidated once on block exit.

    ``swallow_es_errors`` keeps an Elasticsearch cleanup failure from rolling back the surrounding
    transaction.
    """
    program = rdi.program

    household_rows = list(
        Household.all_objects.filter(registration_data_import=rdi).values_list("id", "head_of_household_id")
    )
    individual_ids = list(Individual.all_objects.filter(registration_data_import=rdi).values_list("id", flat=True))
    household_ids = [row[0] for row in household_rows]
    hoh_ids = [row[1] for row in household_rows if row[1] is not None]

    logger.debug(
        "Removing RDI %s population: %d households, %d individuals (delete_rdi=%s)",
        rdi.id,
        len(household_ids),
        len(individual_ids),
        delete_rdi,
    )
    Household.all_objects.filter(registration_data_import=rdi).update(head_of_household=None)

    with population_delete_signals_muted([program.id] if program else []):
        if delete_rdi:
            rdi.delete()
        else:
            Individual.all_objects.filter(id__in=hoh_ids).delete()
            Household.all_objects.filter(registration_data_import=rdi).delete()

    try:
        _remove_rdi_elasticsearch_documents(program, individual_ids, household_ids)
    except Exception:
        if not swallow_es_errors:
            raise
        logger.exception("Failed to remove RDI documents from Elasticsearch for program %s", program.id)
