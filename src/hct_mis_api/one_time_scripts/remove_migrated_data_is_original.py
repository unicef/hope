from django.apps import apps
from django.utils import timezone


def remove_migrated_data_is_original(batch_size: int = 1000) -> None:
    start_time = timezone.now()
    all_models = apps.get_models()

    for model in all_models:
        if hasattr(model, "is_original"):
            if model.__name__ == "GrievanceTicket":
                queryset_all = model.default_for_migrations_fix.all().only("is_original")
                queryset_is_original = queryset_all.filter(is_original=True)
            elif model.__name__ in ["HouseholdSelection", "EntitlementCard", "Feedback", "Message"]:
                queryset_all = model.original_and_repr_objects.all().only("is_original")
                queryset_is_original = queryset_all.filter(is_original=True)
            else:
                queryset_all = model.all_objects.all().only("is_original")
                queryset_is_original = queryset_all.filter(is_original=True)

            print(
                f"*** {model.__name__} All objects: {queryset_all.count()}. "
                f"Removing objects with 'is_original=True': {queryset_is_original.count()}"
            )

            deleted_count = 0
            ids_to_delete = list(queryset_is_original.values_list("id", flat=True).iterator(chunk_size=batch_size))

            for i in range(0, len(ids_to_delete), batch_size):
                batch_pks = ids_to_delete[i : i + batch_size]
                count, _ = queryset_all.filter(pk__in=batch_pks).delete()
                deleted_count += count

            print(f"Deleted {model.__name__} and related objects {deleted_count}.\n")

    print(f"Completed in {timezone.now() - start_time}\n", "*" * 55)
