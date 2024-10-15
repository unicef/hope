from django.apps import apps


def remove_migrated_data_is_original() -> None:
    all_models = apps.get_models()

    for model in all_models:
        if hasattr(model, "is_original"):
            if model.__name__ == "GrievanceTicket":
                # 'GrievanceTicket' has no attribute 'all_objects'
                queryset_all = model.default_for_migrations_fix.all()
                queryset_is_original = queryset_all.filter(is_original=True)
            elif model.__name__ in ["HouseholdSelection", "EntitlementCard", "Feedback", "Message"]:
                queryset_all = model.original_and_repr_objects.all()
                queryset_is_original = queryset_all.filter(is_original=True)
            else:
                queryset_all = model.all_objects.all()
                queryset_is_original = queryset_all.filter(is_original=True)

            print(
                f"*** {model.__name__} All objects: {queryset_all.count()}. "
                f"Removing objects with 'is_original=True': {queryset_is_original.count()}"
            )

            try:
                count, _ = queryset_is_original.delete(soft=False)
            #  TypeError: QuerySet.delete() got an unexpected keyword argument 'soft'
            except TypeError:
                count, _ = queryset_is_original.delete()

            print(f"Deleted {model.__name__} and related objects {count}.\n")
