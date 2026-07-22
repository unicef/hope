from collections.abc import Callable
from typing import Any

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.db.models import Count, DateTimeField, F, Func, Q

from hope.apps.household.const import (
    DISABLED,
    FEMALE,
    MALE,
    NON_BENEFICIARY,
    NOT_COLLECTED,
    OTHER,
)
from hope.models import Household, Individual

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


# Composition counters computed from linked individuals (keys returned by _aggregate_composition).
# Mirrored one-to-one onto the household as `kab_<name>` fields.
KAB_SOURCE_FIELDS: tuple[str, ...] = (
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
    "other_sex_group_count",
    "unknown_sex_group_count",
)
# "Composition present" is decided on the age/gender disaggregation only — `size` is often entered
# manually and must not count as composition being present.
AGE_GROUP_FIELDS: tuple[str, ...] = tuple(f for f in KAB_SOURCE_FIELDS if "_age_group_" in f)


@transaction.atomic
def recalculate_data(
    household: Household, save: bool = True, run_from_migration: bool = False
) -> tuple[Household, list[str]]:
    household = (
        Household.objects.select_for_update(of=("self",))
        .select_related("program__data_collecting_type")
        .get(id=household.id)
    )

    updated_fields: list[str] = []
    if household.program.data_collecting_type.recalculate_composition:
        updated_fields += _recalculate_composition(household, run_from_migration)
    # KAB always runs and always yields fields, so there is always something to persist.
    updated_fields += _recalculate_kab(household)
    updated_fields.append("updated_at")

    if save:
        household.save(update_fields=updated_fields)

    return household, updated_fields


def _recalculate_kab(household: Household) -> list[str]:
    if any(getattr(household, field) is not None for field in AGE_GROUP_FIELDS):
        values: dict[str, int | None] = {field: getattr(household, field) for field in KAB_SOURCE_FIELDS}
    elif household.program.data_collecting_type.collects_individual_data:
        values = _aggregate_composition(household)
    else:
        values = dict.fromkeys(KAB_SOURCE_FIELDS)
    for field, value in values.items():
        setattr(household, f"kab_{field}", value)
    return [f"kab_{field}" for field in KAB_SOURCE_FIELDS]


def _recalculate_composition(household: Household, run_from_migration: bool) -> list[str]:
    individuals_to_update = []
    individuals_fields_to_update: list[str] = []

    if not run_from_migration:  # TODO remove after migration
        for individual in household.individuals.all().select_for_update().order_by("pk"):
            _individual, _fields_to_update = individual.recalculate_data(save=False)
            individuals_to_update.append(_individual)
            individuals_fields_to_update.extend(x for x in _fields_to_update if x not in individuals_fields_to_update)

        Individual.objects.bulk_update(individuals_to_update, individuals_fields_to_update)

    age_groups = _aggregate_composition(household)
    updated_fields = ["child_hoh", "fchild_hoh"]
    for key, value in age_groups.items():
        updated_fields.append(key)
        setattr(household, key, value)

    household.child_hoh = False
    household.fchild_hoh = False
    if household.head_of_household.age < 18:
        if household.head_of_household.sex == FEMALE:
            household.fchild_hoh = True
        household.child_hoh = True

    return updated_fields


def _composition_count_filters(cutoff: Callable[[int], Any]) -> dict[str, Q]:
    """Single source of truth for composition counters.

    `cutoff(years)` returns the birth-date boundary "years ago relative to the household's
    last_registration_date" — a Python datetime on the per-household path, a SQL expression
    on the batch path. Everything else is shared, so both paths count identically.
    """
    is_beneficiary = ~Q(relationship=NON_BENEFICIARY)
    active_beneficiary = Q(withdrawn=False, duplicate=False)
    female_beneficiary = Q(sex=FEMALE) & active_beneficiary & is_beneficiary
    male_beneficiary = Q(sex=MALE) & active_beneficiary & is_beneficiary
    disabled_beneficiary = Q(disability=DISABLED) & active_beneficiary & is_beneficiary
    female_disabled_beneficiary = disabled_beneficiary & female_beneficiary
    male_disabled_beneficiary = disabled_beneficiary & male_beneficiary

    to_6_years = Q(birth_date__gt=cutoff(6))
    from_6_to_12_years = Q(birth_date__lte=cutoff(6), birth_date__gt=cutoff(12))
    from_12_to_18_years = Q(birth_date__lte=cutoff(12), birth_date__gt=cutoff(18))
    from_18_to_60_years = Q(birth_date__lte=cutoff(18), birth_date__gt=cutoff(60))
    from_60_years = Q(birth_date__lte=cutoff(60))
    is_child = Q(birth_date__gt=cutoff(18))

    return {
        "female_age_group_0_5_count": female_beneficiary & to_6_years,
        "female_age_group_6_11_count": female_beneficiary & from_6_to_12_years,
        "female_age_group_12_17_count": female_beneficiary & from_12_to_18_years,
        "female_age_group_18_59_count": female_beneficiary & from_18_to_60_years,
        "female_age_group_60_count": female_beneficiary & from_60_years,
        "male_age_group_0_5_count": male_beneficiary & to_6_years,
        "male_age_group_6_11_count": male_beneficiary & from_6_to_12_years,
        "male_age_group_12_17_count": male_beneficiary & from_12_to_18_years,
        "male_age_group_18_59_count": male_beneficiary & from_18_to_60_years,
        "male_age_group_60_count": male_beneficiary & from_60_years,
        "female_age_group_0_5_disabled_count": female_disabled_beneficiary & to_6_years,
        "female_age_group_6_11_disabled_count": female_disabled_beneficiary & from_6_to_12_years,
        "female_age_group_12_17_disabled_count": female_disabled_beneficiary & from_12_to_18_years,
        "female_age_group_18_59_disabled_count": female_disabled_beneficiary & from_18_to_60_years,
        "female_age_group_60_disabled_count": female_disabled_beneficiary & from_60_years,
        "male_age_group_0_5_disabled_count": male_disabled_beneficiary & to_6_years,
        "male_age_group_6_11_disabled_count": male_disabled_beneficiary & from_6_to_12_years,
        "male_age_group_12_17_disabled_count": male_disabled_beneficiary & from_12_to_18_years,
        "male_age_group_18_59_disabled_count": male_disabled_beneficiary & from_18_to_60_years,
        "male_age_group_60_disabled_count": male_disabled_beneficiary & from_60_years,
        "size": is_beneficiary & active_beneficiary,
        "pregnant_count": is_beneficiary & active_beneficiary & Q(pregnant=True),
        "children_count": is_child & active_beneficiary & is_beneficiary,
        "female_children_count": is_child & female_beneficiary,
        "male_children_count": is_child & male_beneficiary,
        "children_disabled_count": is_child & disabled_beneficiary,
        "female_children_disabled_count": is_child & female_disabled_beneficiary,
        "male_children_disabled_count": is_child & male_disabled_beneficiary,
        "other_sex_group_count": Q(sex=OTHER) & active_beneficiary & is_beneficiary,
        "unknown_sex_group_count": Q(sex=NOT_COLLECTED) & active_beneficiary & is_beneficiary,
    }


def _composition_counts(cutoff: Callable[[int], Any]) -> dict[str, Count]:
    return {name: Count("id", distinct=True, filter=q) for name, q in _composition_count_filters(cutoff).items()}


def _years_ago_sql(years: int) -> Func:
    # Postgres calendar interval arithmetic matches relativedelta(years=...) subtraction
    # (including the Feb 29 clamp), so the batch path counts exactly like the Python path.
    return Func(
        F("household__last_registration_date"),
        template=f"(%(expressions)s - interval '{years} years')",
        output_field=DateTimeField(),
    )


def _aggregate_composition(household: Household) -> dict:
    """Return the composition counters computed from the household's linked individuals."""
    last_registration_date = household.last_registration_date
    return household.individuals.aggregate(
        **_composition_counts(lambda years: last_registration_date - relativedelta(years=years))
    )


def aggregate_composition_by_household_id(household_ids: list) -> dict:
    """Compute the same counters as `_aggregate_composition` in one grouped query for many households.

    Households without any individuals are absent from the result. Used by the KAB backfill.
    """
    rows = (
        Individual.objects.filter(household_id__in=household_ids)
        .values("household_id")
        .order_by()  # clear default ordering so GROUP BY stays on household_id only
        .annotate(**_composition_counts(_years_ago_sql))
    )
    return {row.pop("household_id"): row for row in rows}
