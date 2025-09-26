from django.db.models.signals import post_save, pre_delete
from django.dispatch import Signal, receiver

from hope.apps.core.signals import post_bulk_update, post_bulk_create

individual_withdrawn = Signal()
household_withdrawn = Signal()
household_deleted = Signal()
individual_deleted = Signal()


@receiver(post_save, sender='household.Household')
@receiver(pre_delete, sender='household.Household')
@receiver(post_save, sender='household.Individual')
@receiver(pre_delete, sender='household.Individual')
def increment_household_list_cache_version(sender, instance, **kwargs):
    from hope.apps.household.api.caches import increment_household_list_program_key

    increment_household_list_program_key(instance.program.id)


@receiver(post_bulk_update, sender='household.Household')
@receiver(post_bulk_create, sender='household.Household')
@receiver(post_bulk_update, sender='household.Individual')
@receiver(post_bulk_create, sender='household.Individual')
def increment_household_list_cache_version_from_bulk(sender, instances, **kwargs):
    from hope.apps.household.api.caches import increment_household_list_program_key
    from hope.apps.household.models import Household, Individual

    program_ids = {instance.program_id for instance in instances if isinstance(instance, (Household, Individual))}
    for program_id in program_ids:
        increment_household_list_program_key(program_id)
