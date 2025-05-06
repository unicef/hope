from typing import Any

from django.apps import apps
from django.db import transaction
from django.utils import timezone


def _get_model_list_is_original() -> list[Any]:
    all_models = apps.get_models()
    all_models_with_is_original_field = []

    for model in all_models:
        if hasattr(model, "is_original"):
            all_models_with_is_original_field.append(model)

    return all_models_with_is_original_field


def remove_migrated_data_is_original(batch_size: int = 1000) -> None:
    timezone.now()

    for model in _get_model_list_is_original():
        if model.__name__ == "GrievanceTicket":
            model_qs = model.default_for_migrations_fix
        elif model.__name__ in ["EntitlementCard", "Feedback", "Message"]:
            model_qs = model.original_and_repr_objects
        else:
            model_qs = model.all_objects

        queryset_is_original = model_qs.filter(is_original=True).only("id")

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
                pass


def get_statistic_is_original() -> None:
    timezone.now()
    for model in _get_model_list_is_original():
        if model.__name__ == "GrievanceTicket":
            queryset_all = model.default_for_migrations_fix.all().only("is_original", "id")
            queryset_all.filter(is_original=True)
        elif model.__name__ in ["EntitlementCard", "Feedback", "Message"]:
            queryset_all = model.original_and_repr_objects.all().only("is_original", "id")
            queryset_all.filter(is_original=True)
        else:
            queryset_all = model.all_objects.all().only("is_original", "id")
            queryset_all.filter(is_original=True)
