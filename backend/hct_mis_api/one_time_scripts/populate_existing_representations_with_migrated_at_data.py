from django.utils import timezone

from hct_mis_api.apps.accountability.models import Feedback, Message
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    BankAccountInfo,
    Document,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.targeting.models import HouseholdSelection


def targeting_populate_existing_representations_with_migrated_at_data():
    HouseholdSelection.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=timezone.now()
    )


def accountability_populate_existing_representations_with_migrated_at_data():
    now = timezone.now()
    Feedback.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )
    Message.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )


def grievance_populate_existing_representations_with_migrated_at_data():
    GrievanceTicket.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=timezone.now()
    )


def household_populate_existing_representations_with_migrated_at_data():
    now = timezone.now()
    Household.objects.filter(migrated_at__isnull=True, is_migration_handled=True, is_original=True).update(
        migrated_at=now
    )
    Individual.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
    BankAccountInfo.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
    Document.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
    IndividualIdentity.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
    IndividualRoleInHousehold.objects.filter(
        migrated_at__isnull=True, is_migration_handled=False, is_original=True, copied_to__isnull=False
    ).update(migrated_at=now, is_migration_handled=True)
