from typing import Any, List

from django.apps import apps
from django.db import transaction
from django.utils import timezone


def _get_model_list_is_original() -> List[Any]:
    all_models = apps.get_models()
    all_models_with_is_original_field = []

    for model in all_models:
        if hasattr(model, "is_original"):
            all_models_with_is_original_field.append(model)

    return all_models_with_is_original_field


def remove_migrated_data_is_original(batch_size: int = 1000) -> None:
    start_time = timezone.now()

    for model in _get_model_list_is_original():
        if model.__name__ == "GrievanceTicket":
            model_qs = model.default_for_migrations_fix
        elif model.__name__ in ["EntitlementCard", "Feedback", "Message"]:
            model_qs = model.original_and_repr_objects
        else:
            model_qs = model.all_objects

        queryset_is_original = model_qs.filter(is_original=True).only("id")
        print(f"Removing objects with 'is_original=True': {model.__name__}.")

        ids_to_delete = [
            str(obj_id) for obj_id in queryset_is_original.values_list("id", flat=True).iterator(chunk_size=batch_size)
        ]
        deleted_count = 0
        total_to_delete = len(ids_to_delete)

        for i in range(0, total_to_delete, batch_size):
            batch_ids = ids_to_delete[i : i + batch_size]
            # batch processing atomically
            with transaction.atomic():
                deleted, _ = queryset_is_original.filter(id__in=batch_ids).delete()
                deleted_count += deleted

            if i % (batch_size * 10) == 0:
                print(
                    f"Progress: Deleted {deleted_count:,} {model.__name__} and related objects. "
                    f"{model.__name__} list contains {total_to_delete:,} records."
                )
        print(f"Deleted {model.__name__} and related objects: {deleted_count:,}.\n")
    print(f"Completed in {timezone.now() - start_time}\n", "*" * 60)


def get_statistic_is_original() -> None:
    start_time = timezone.now()
    for model in _get_model_list_is_original():
        if model.__name__ == "GrievanceTicket":
            queryset_all = model.default_for_migrations_fix.all().only("is_original", "id")
            queryset_is_original = queryset_all.filter(is_original=True)
        elif model.__name__ in ["EntitlementCard", "Feedback", "Message"]:
            queryset_all = model.original_and_repr_objects.all().only("is_original", "id")
            queryset_is_original = queryset_all.filter(is_original=True)
        else:
            queryset_all = model.all_objects.all().only("is_original", "id")
            queryset_is_original = queryset_all.filter(is_original=True)
        print(
            f"*** {model.__name__} All objects: {queryset_all.count():,}. "
            f"Will remove objects with 'is_original=True': {queryset_is_original.count():,}"
        )
    print(f"Completed in {timezone.now() - start_time}\n", "*" * 55)
