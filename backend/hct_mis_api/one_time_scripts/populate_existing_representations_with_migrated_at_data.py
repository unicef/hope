import logging

from django.utils import timezone

from hct_mis_api.apps.accountability.models import Feedback, Message
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualRoleInHousehold,
)

logger = logging.getLogger(__name__)


def accountability_populate_existing_representations_with_migrated_at_data() -> None:
    now = timezone.now()
    Feedback.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )
    Message.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )


def grievance_populate_existing_representations_with_migrated_at_data() -> None:
    GrievanceTicket.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=timezone.now()
    )


def household_populate_existing_representations_with_migrated_at_data() -> None:
    now = timezone.now()
    logger.info("Updating Households")
    Household.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )
    logger.info("Updating Individuals")
    Individual.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)

    logger.info("Updating IndividualRoleInHouseholds")
    IndividualRoleInHousehold.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
