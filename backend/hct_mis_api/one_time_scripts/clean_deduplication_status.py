import logging

from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hct_mis_api.apps.household.models import DUPLICATE, NEEDS_ADJUDICATION, Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)


# Run for these ids
# - "12a8dae8-45fa-4608-b90d-5650addc7f4f"
# - "9978582f-1d5a-4b4b-837d-2913fffb7776"
def clean_deduplication_status(rdi_id: str) -> None:
    rdi = RegistrationDataImport.objects.get(id=rdi_id)

    clean_golden_record_duplicates(rdi)
    clean_needs_adjudication(rdi)


def clean_golden_record_duplicates(rdi: RegistrationDataImport) -> None:
    golden_record_duplicates = Individual.objects.filter(
        registration_data_import=rdi, deduplication_golden_record_status=DUPLICATE
    )
    duplicates_count = golden_record_duplicates.count()
    logger.info(f"Found {duplicates_count} golden record duplicates")
    create_needs_adjudication_tickets(
        golden_record_duplicates, "duplicates", rdi.business_area, registration_data_import=rdi
    )
    still_duplicated_count = golden_record_duplicates.count()
    logger.info(f"Created {still_duplicated_count} tickets for golden record duplicates")
    logger.info(f"Cleaned {duplicates_count - still_duplicated_count} golden records")


def clean_needs_adjudication(rdi: RegistrationDataImport) -> None:
    needs_adjudication = Individual.objects.filter(
        registration_data_import=rdi, deduplication_golden_record_status=NEEDS_ADJUDICATION
    )
    needs_adjudication_count = needs_adjudication.count()
    logger.info(f"Found {needs_adjudication_count} needs adjudication")
    create_needs_adjudication_tickets(
        needs_adjudication, "possible_duplicates", rdi.business_area, registration_data_import=rdi
    )
    still_needs_adjudication = needs_adjudication.count()
    logger.info(f"Created {still_needs_adjudication} tickets for needs adjudication")
    logger.info(f"Cleaned {needs_adjudication_count - still_needs_adjudication} needs adjudication")
