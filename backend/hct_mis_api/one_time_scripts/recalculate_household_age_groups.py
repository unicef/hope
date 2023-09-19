from django.core.paginator import Paginator

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.services.household_recalculate_data import recalculate_data

updated_fields = [
    "female_age_group_0_5_count",
    "female_age_group_6_11_count",
    "female_age_group_12_17_count",
    "female_age_group_18_59_count",
    "female_age_group_60_count",
    "male_age_group_0_5_count",
    "male_age_group_6_11_count",
    "male_age_group_12_17_count",
    "male_age_group_18_59_count",
    "male_age_group_60_count",
    "female_age_group_0_5_disabled_count",
    "female_age_group_6_11_disabled_count",
    "female_age_group_12_17_disabled_count",
    "female_age_group_18_59_disabled_count",
    "female_age_group_60_disabled_count",
    "male_age_group_0_5_disabled_count",
    "male_age_group_6_11_disabled_count",
    "male_age_group_12_17_disabled_count",
    "male_age_group_18_59_disabled_count",
    "male_age_group_60_disabled_count",
    "size",
    "pregnant_count",
    "children_count",
    "female_children_count",
    "male_children_count",
    "children_disabled_count",
    "female_children_disabled_count",
    "male_children_disabled_count",
    "child_hoh",
    "fchild_hoh",
    "updated_at",
    "is_recalculated_group_ages"
]


def recalculate_household_age_groups(size: int = 250) -> None:
    queryset = Household.objects.filter(last_registration_date__isnull=False).only("pk")
    paginator = Paginator(queryset, size)
    queryset_count = queryset.count()

    for page_number in paginator.page_range:
        households_to_update = []
        print(f"Processing page {page_number}/{queryset_count / size}")
        household_page_list = paginator.page(page_number)
        for household in (
            Household.objects.filter(pk__in=household_page_list)
            .only("id", "collect_individual_data")
            .prefetch_related("individuals")
            .select_for_update(of=("self",), skip_locked=True)
            .order_by("pk")
        ):
            recalculated_household, _ = recalculate_data(household, save=False, run_from_migration=True)
            households_to_update.append(recalculated_household)
        Household.objects.bulk_update(households_to_update, updated_fields)
