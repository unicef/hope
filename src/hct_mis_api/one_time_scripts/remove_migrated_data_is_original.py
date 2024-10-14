from django.apps import apps


def remove_migrated_data_is_original() -> None:
    all_models = apps.get_models()

    for model in all_models:
        if hasattr(model, "is_original"):
            print(f"Removing objects from {model.__name__} that have the 'is_original' field.")
            if model.__name__ == "GrievanceTicket":
                # or maybe try except AttributeError:
                # 'GrievanceTicket' has no attribute 'all_objects'
                queryset = model.default_for_migrations_fix.filter(is_original=True)
            elif model.__name__ in ["HouseholdSelection", "EntitlementCard", "Feedback", "Message"]:
                queryset = model.original_and_repr_objects.filter(is_original=True)
            else:
                queryset = model.all_objects.filter(is_original=True)

            count, _ = queryset.delete()
            print(f"Deleted {count} {model.__name__} objects.\n")
