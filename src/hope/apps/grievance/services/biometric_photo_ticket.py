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

    individuals_with_error: dict[str, Individual] = {}
    for pair in deduplication_pairs:
        present = [individual for individual in (pair.individual1, pair.individual2) if individual]
        if len(present) != 1:
            continue
        individual = present[0]
        if individual.registration_data_import_id == rdi.id and str(individual.id) not in individuals_with_error:
            individuals_with_error[str(individual.id)] = individual

    for individual in individuals_with_error.values():
        _create_biometrics_photo_data_change_ticket(individual, rdi)


def _create_biometrics_photo_data_change_ticket(individual: Individual, rdi: RegistrationDataImport) -> None:
    ticket_already_exists = (
        TicketIndividualDataUpdateDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .filter(individual=individual, ticket__issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO)
        .exists()
    )
    if ticket_already_exists:
        return

    household = individual.household
    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_PHOTO,
        business_area=rdi.program.business_area,
        admin2=household.admin2 if household else None,
        area=household.village if household else "",
        registration_data_import=rdi,
        submission_channel=SUBMISSION_CHANNEL_HOPE,
        description="Biometric deduplication could not read this individual's photo. Upload a valid photo to resolve.",
    )
    ticket.programs.set([individual.program])

    current_photo = individual.photo.name if individual.photo else ""
    TicketIndividualDataUpdateDetails.objects.create(
        ticket=ticket,
        individual=individual,
        individual_data={"photo": {"value": None, "approve_status": False, "previous_value": current_photo}},
    )
    ticket.save()  # populate household_unicef_id now that the details (and household) exist
