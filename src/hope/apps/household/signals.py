from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from hope.apps.core.signals import post_bulk_create, post_bulk_update

individual_withdrawn = Signal()
household_withdrawn = Signal()
household_deleted = Signal()
individual_deleted = Signal()


@receiver(post_save, sender="household.Household")
@receiver(pre_delete, sender="household.Household")
@receiver(post_save, sender="household.Individual")
@receiver(pre_delete, sender="household.Individual")
def increment_household_list_cache_version(sender, instance, **kwargs):
    from hope.apps.household.api.caches import increment_household_list_program_key

    increment_household_list_program_key(instance.program.id)


@receiver(post_save, sender="household.Individual")
@receiver(pre_delete, sender="household.Individual")
def increment_individual_list_cache_version(sender, instance, **kwargs):
    from hope.apps.household.api.caches import increment_individual_list_program_key

    increment_individual_list_program_key(instance.program.id)


def increment_household_list_cache_version_from_bulk(sender, instances, **kwargs):
    from hope.apps.household.api.caches import increment_household_list_program_key

    program_ids = {instance.program_id for instance in instances}
    for program_id in program_ids:
        increment_household_list_program_key(program_id)


def increment_individual_list_cache_version_from_bulk(sender, instances, **kwargs):
    from hope.apps.household.api.caches import increment_individual_list_program_key

    program_ids = {instance.program_id for instance in instances}
    for program_id in program_ids:
        increment_individual_list_program_key(program_id)


# Register signals - use lazy import to avoid circular dependency
def register_bulk_signals():
    from hope.models import Household, Individual

    post_bulk_update.connect(increment_household_list_cache_version_from_bulk, sender=Household)
    post_bulk_create.connect(increment_household_list_cache_version_from_bulk, sender=Household)
    post_bulk_update.connect(increment_household_list_cache_version_from_bulk, sender=Individual)
    post_bulk_create.connect(increment_household_list_cache_version_from_bulk, sender=Individual)

    post_bulk_update.connect(increment_individual_list_cache_version_from_bulk, sender=Individual)
    post_bulk_create.connect(increment_individual_list_cache_version_from_bulk, sender=Individual)
