import logging

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    Document,
    Individual,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
    DeduplicateTask,
    HardDocumentDeduplication,
)
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index

logger = logging.getLogger(__name__)


def deduplicate_and_check_against_sanctions_list_task_single_individual(
    should_populate_index: bool, individual: Individual
) -> None:
    business_area = individual.business_area
    program = individual.program
    individuals_queryset = Individual.objects.filter(
        id=individual.id
    )  # many methods are using queryset, I cannot pass singe individual without refactoring them all

    if should_populate_index is True:
        populate_index(individuals_queryset, get_individual_doc(business_area.slug))

    if business_area.postpone_deduplication:
        logger.info("Postponing deduplication for business area %s", business_area)
        HardDocumentDeduplication().deduplicate(
            Document.objects.filter(individual_id__in=[individual.id]),
        )
        return
    DeduplicateTask(business_area.slug, program.id).deduplicate_individuals_from_other_source(individuals_queryset)
    golden_record_duplicates = individuals_queryset.filter(deduplication_golden_record_status=DUPLICATE)
    create_needs_adjudication_tickets(
        golden_record_duplicates,
        "duplicates",
        business_area,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )
    needs_adjudication = individuals_queryset.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
    create_needs_adjudication_tickets(
        needs_adjudication,
        "possible_duplicates",
        business_area,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )

    if (
        program.sanction_lists.exists()
    ):  # enable check against sanction list only if program has sanction lists selected
        check_against_sanction_list_pre_merge(program.id, individuals_ids=[str(individual.id)])

    HardDocumentDeduplication().deduplicate(
        Document.objects.filter(individual_id=individual.id),
    )
