import logging

from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import Signal, receiver

from hope.apps.core.signals import post_bulk_create, post_bulk_update

individual_withdrawn = Signal()
household_withdrawn = Signal()
household_deleted = Signal()
individual_deleted = Signal()
logger = logging.getLogger(__name__)


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


def _is_elasticsearch_enabled() -> bool:
    return getattr(settings, "ELASTICSEARCH_DSL_AUTOSYNC", False)


@receiver(pre_save, sender="program.Program")
def capture_program_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender="program.Program")
def handle_program_status_change(sender, instance, created, **kwargs):
    """Manage Elasticsearch indexes based on Program status changes."""
    from hope.apps.household.index_management import rebuild_program_indexes
    from hope.models import Program

    if not _is_elasticsearch_enabled():
        return

    old_status = getattr(instance, "_old_status", None)
    current_status = instance.status
    try:
        if old_status != current_status and current_status == Program.ACTIVE:
            rebuild_program_indexes(str(instance.pk))
    except Exception as e:  # noqa
        logger.error(f"Failed to manage indexes for program {instance.id}: {e}")
    instance.__dict__.pop("_old_status", None)


@receiver(pre_save, sender="household.Individual")
@receiver(pre_save, sender="household.Household")
def capture_old_is_removed(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_is_removed = sender.all_objects.get(pk=instance.pk).is_removed
        except sender.DoesNotExist:
            instance._old_is_removed = False
    else:
        instance._old_is_removed = False


@receiver(post_save, sender="household.Individual")
def sync_individual_to_elasticsearch(sender, instance, **kwargs):
    """Auto-sync Individual to Elasticsearch when saved."""
    if not _is_elasticsearch_enabled():
        return

    from hope.apps.household.documents import get_individual_doc
    from hope.models import Program

    if instance.program.status == Program.ACTIVE:
        try:
            removed_now = instance.is_removed and not getattr(instance, "_old_is_removed", True)
            if removed_now:
                get_individual_doc(str(instance.program_id))().update(instance, action="delete")
            elif not instance.is_removed:
                get_individual_doc(str(instance.program_id))().update(instance)
        except Exception as e:  # noqa
            logger.error(f"Failed to sync Individual {instance.id} to Elasticsearch: {e}")
    instance.__dict__.pop("_old_is_removed", None)


@receiver(post_delete, sender="household.Individual")
def remove_individual_from_elasticsearch(sender, instance, **kwargs):
    if not _is_elasticsearch_enabled():
        return

    from hope.apps.household.documents import get_individual_doc
    from hope.models import Program

    if instance.program.status == Program.ACTIVE:
        try:
            get_individual_doc(str(instance.program_id))().update(instance, action="delete")
        except Exception as e:  # noqa
            logger.error(f"Failed to remove Individual {instance.id} from Elasticsearch: {e}")


@receiver(post_save, sender="household.Household")
def sync_household_to_elasticsearch(sender, instance, **kwargs):
    """Auto-sync Household to Elasticsearch when saved."""
    if not _is_elasticsearch_enabled():
        return

    from hope.apps.household.documents import get_household_doc
    from hope.models import Program

    if instance.program.status == Program.ACTIVE:
        try:
            removed_now = instance.is_removed and not getattr(instance, "_old_is_removed", True)
            if removed_now:
                get_household_doc(str(instance.program_id))().update(instance, action="delete")
            elif not instance.is_removed:
                get_household_doc(str(instance.program_id))().update(instance)
        except Exception as e:  # noqa
            logger.error(f"Failed to sync Household {instance.id} to Elasticsearch: {e}")
    instance.__dict__.pop("_old_is_removed", None)


@receiver(post_delete, sender="household.Household")
def remove_household_from_elasticsearch(sender, instance, **kwargs):
    if not _is_elasticsearch_enabled():
        return

    from hope.apps.household.documents import get_household_doc
    from hope.models import Program

    if instance.program and instance.program.status == Program.ACTIVE:
        try:
            get_household_doc(str(instance.program_id))().update(instance, action="delete")
        except Exception as e:  # noqa
            logger.error(f"Failed to remove Household {instance.id} from Elasticsearch: {e}")
