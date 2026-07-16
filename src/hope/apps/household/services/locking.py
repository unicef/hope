from hope.models import Household, Individual


def lock_household_then_individual(individual: Individual) -> tuple[Household | None, Individual]:
    """Lock the individual's household, then the individual.

    Every flow locking both rows must acquire them in this order (the same as
    recalculate_data) to avoid lock-ordering deadlocks. The household comes from
    the caller's snapshot of individual.household_id; a concurrent household
    reassignment is not re-checked.
    """
    household = None
    if individual.household_id:
        household = Household.objects.select_for_update().get(id=individual.household_id)
    return household, Individual.objects.select_for_update().get(id=individual.id)
