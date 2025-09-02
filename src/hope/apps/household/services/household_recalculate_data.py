from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Count, Q

from hope.models.household import (
    DISABLED,
    FEMALE,
    MALE,
    NON_BENEFICIARY,
    NOT_COLLECTED,
    OTHER,
    Household,
)
from hope.models.individual import Individual

# Set of Individual fields which affects Household recalculation
RECALCULATION_INDIVIDUAL_FIELDS = {
    "relationship",
    "withdrawn",
    "duplicate",
    "sex",
    "disability",
    "birth_date",
    "pregnant",
}


@transaction.atomic
def recalculate_data(
    household: Household, save: bool = True, run_from_migration: bool = False
) -> tuple[Household, list[str]]:
    household = Household.objects.select_for_update().get(id=household.id)

    if not household.program.data_collecting_type.recalculate_composition:
        return household, []

    individuals_to_update = []
    individuals_fields_to_update = []

    if not run_from_migration:  # TODO remove after migration
        for individual in household.individuals.all().select_for_update().order_by("pk"):
            _individual, _fields_to_update = individual.recalculate_data(save=False)
            individuals_to_update.append(_individual)
            individuals_fields_to_update.extend(x for x in _fields_to_update if x not in individuals_fields_to_update)

        Individual.objects.bulk_update(individuals_to_update, individuals_fields_to_update)

    last_registration_date = household.last_registration_date
    date_6_years_ago = last_registration_date - relativedelta(years=+6)
    date_12_years_ago = last_registration_date - relativedelta(years=+12)
    date_18_years_ago = last_registration_date - relativedelta(years=+18)
    date_60_years_ago = last_registration_date - relativedelta(years=+60)

    is_beneficiary = ~Q(relationship=NON_BENEFICIARY)
    active_beneficiary = Q(withdrawn=False, duplicate=False)
    female_beneficiary = Q(Q(sex=FEMALE) & active_beneficiary & is_beneficiary)
    male_beneficiary = Q(Q(sex=MALE) & active_beneficiary & is_beneficiary)
    disabled_disability = Q(disability=DISABLED) & active_beneficiary & is_beneficiary
    female_disability_beneficiary = Q(disabled_disability & female_beneficiary)
    male_disability_beneficiary = Q(disabled_disability & male_beneficiary)

    to_6_years = Q(birth_date__gt=date_6_years_ago)
    from_6_to_12_years = Q(birth_date__lte=date_6_years_ago, birth_date__gt=date_12_years_ago)
    from_12_to_18_years = Q(birth_date__lte=date_12_years_ago, birth_date__gt=date_18_years_ago)
    from_18_to_60_years = Q(birth_date__lte=date_18_years_ago, birth_date__gt=date_60_years_ago)
    from_60_years = Q(birth_date__lte=date_60_years_ago)

    children_count = Q(birth_date__gt=date_18_years_ago) & active_beneficiary & is_beneficiary
    female_children_count = Q(birth_date__gt=date_18_years_ago) & female_beneficiary
    male_children_count = Q(birth_date__gt=date_18_years_ago) & male_beneficiary

    children_disabled_count = Q(birth_date__gt=date_18_years_ago) & disabled_disability
    female_children_disabled_count = Q(birth_date__gt=date_18_years_ago) & female_disability_beneficiary
    male_children_disabled_count = Q(birth_date__gt=date_18_years_ago) & male_disability_beneficiary
    other_sex_group_count = Q(sex=OTHER)
    unknown_sex_group_count = Q(sex=NOT_COLLECTED)

    age_groups = household.individuals.aggregate(
        female_age_group_0_5_count=Count("id", distinct=True, filter=Q(female_beneficiary & to_6_years)),
        female_age_group_6_11_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_6_to_12_years)),
        female_age_group_12_17_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_12_to_18_years)),
        female_age_group_18_59_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_18_to_60_years)),
        female_age_group_60_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_60_years)),
        male_age_group_0_5_count=Count("id", distinct=True, filter=Q(male_beneficiary & to_6_years)),
        male_age_group_6_11_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_6_to_12_years)),
        male_age_group_12_17_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_12_to_18_years)),
        male_age_group_18_59_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_18_to_60_years)),
        male_age_group_60_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_60_years)),
        female_age_group_0_5_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(female_disability_beneficiary & to_6_years),
        ),
        female_age_group_6_11_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(female_disability_beneficiary & from_6_to_12_years),
        ),
        female_age_group_12_17_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(female_disability_beneficiary & from_12_to_18_years),
        ),
        female_age_group_18_59_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(female_disability_beneficiary & from_18_to_60_years),
        ),
        female_age_group_60_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(female_disability_beneficiary & from_60_years),
        ),
        male_age_group_0_5_disabled_count=Count(
            "id", distinct=True, filter=Q(male_disability_beneficiary & to_6_years)
        ),
        male_age_group_6_11_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(male_disability_beneficiary & from_6_to_12_years),
        ),
        male_age_group_12_17_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(male_disability_beneficiary & from_12_to_18_years),
        ),
        male_age_group_18_59_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(male_disability_beneficiary & from_18_to_60_years),
        ),
        male_age_group_60_disabled_count=Count(
            "id",
            distinct=True,
            filter=Q(male_disability_beneficiary & from_60_years),
        ),
        size=Count("id", distinct=True, filter=Q(is_beneficiary & active_beneficiary)),
        pregnant_count=Count(
            "id",
            distinct=True,
            filter=Q(is_beneficiary & active_beneficiary & Q(pregnant=True)),
        ),
        children_count=Count(
            "id",
            distinct=True,
            filter=children_count,
        ),
        female_children_count=Count(
            "id",
            distinct=True,
            filter=female_children_count,
        ),
        male_children_count=Count(
            "id",
            distinct=True,
            filter=male_children_count,
        ),
        children_disabled_count=Count(
            "id",
            distinct=True,
            filter=children_disabled_count,
        ),
        female_children_disabled_count=Count(
            "id",
            distinct=True,
            filter=female_children_disabled_count,
        ),
        male_children_disabled_count=Count(
            "id",
            distinct=True,
            filter=male_children_disabled_count,
        ),
        other_sex_group_count=Count(
            "id",
            distinct=True,
            filter=other_sex_group_count,
        ),
        unknown_sex_group_count=Count(
            "id",
            distinct=True,
            filter=unknown_sex_group_count,
        ),
    )
    updated_fields = ["child_hoh", "fchild_hoh", "updated_at"]

    for key, value in age_groups.items():
        updated_fields.append(key)
        setattr(household, key, value)

    household.child_hoh = False
    household.fchild_hoh = False
    if household.head_of_household.age < 18:
        if household.head_of_household.sex == FEMALE:
            household.fchild_hoh = True
        household.child_hoh = True

    if save:
        household.save(update_fields=updated_fields)

    return household, updated_fields
