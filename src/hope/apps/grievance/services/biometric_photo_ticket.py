from django.db.models import QuerySet

from hope.apps.grievance.constants import SUBMISSION_CHANNEL_HOPE
from hope.apps.grievance.models import GrievanceTicket, TicketIndividualDataUpdateDetails
from hope.models import DeduplicationEngineSimilarityPair, Individual, RegistrationDataImport


def create_biometrics_photo_data_change_tickets(
    deduplication_pairs: QuerySet[DeduplicationEngineSimilarityPair],
    rdi: RegistrationDataImport,
) -> None:
    """Create a photo-fix Data Change ticket for each individual whose photo the engine couldn't read.

    Photo-error findings are single-sided (one individual), so each yields one Individual Data
    Update ticket, scoped to ``rdi``, with the photo change left pending for the operator to fill in.
    """
    deduplication_pairs = deduplication_pairs.select_related(
        "individual1__household", "individual2__household", "individual1__program", "individual2__program"
    )

    errors: dict[str, tuple[Individual, str]] = {}
    for pair in deduplication_pairs:
        present = [individual for individual in (pair.individual1, pair.individual2) if individual]
        # Defensive: the engine only ever names one individual on a photo error.
        if len(present) != 1:
            continue
        individual = present[0]
        errors[str(individual.id)] = (individual, f"{pair.status_code} - {pair.get_status_code_display()}")

    if not errors:
        return

    already_ticketed_ids = set(
        TicketIndividualDataUpdateDetails.objects.filter(
            individual_id__in=errors.keys(),
            ticket__issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO,
        )
        .exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .values_list("individual_id", flat=True)
    )

    for individual, error_description in errors.values():
        if individual.id not in already_ticketed_ids:
            _create_biometrics_photo_data_change_ticket(individual, rdi, error_description)


def _create_biometrics_photo_data_change_ticket(
    individual: Individual, rdi: RegistrationDataImport, error_description: str
) -> None:
    household = individual.household
    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO,
        business_area=rdi.program.business_area,
        admin2_id=household.admin2_id if household else None,
        area=household.village if household else "",
        registration_data_import=rdi,
        submission_channel=SUBMISSION_CHANNEL_HOPE,
        household_unicef_id=household.unicef_id if household else None,
        description=(
            f"Biometric deduplication could not read this individual's photo "
            f"({error_description}). Upload a valid photo to resolve."
        ),
    )
    ticket.programs.set([individual.program])

    current_photo = individual.photo.name if individual.photo else ""
    TicketIndividualDataUpdateDetails.objects.create(
        ticket=ticket,
        individual=individual,
        individual_data={"photo": {"value": None, "approve_status": False, "previous_value": current_photo}},
    )
