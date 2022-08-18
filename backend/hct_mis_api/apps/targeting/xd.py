

def optimized_household_query():
    from hct_mis_api.apps.household.models import Household, Individual
    from django.db.models import Q
    import time

    households = Household.objects.filter(business_area="7c1becc3-f092-42a9-b235-fc5033c5da1d")
    start = time.time()
    households1 = households.filter(withdrawn=False, size__gt=0, is_removed=False).filter(
        children_count__gte=3, first_registration_date__range=("2021-12-01 00:00:00+00:00", "2022-08-31 00:00:00+00:00")
    )

    household_ids_first_or = (
        Individual.objects.filter(Q(bank_account_info__isnull=False) & ~Q(bank_account_info__bank_account_number=""))
        .filter(
            duplicate=False,
            withdrawn=False,
            household__in=households1,
            households_and_roles__role="PRIMARY",
        )
        .values_list("household_id")
        .distinct("household_id")
    )

    # OR

    households2 = households.filter(withdrawn=False, size__gt=0, is_removed=False).filter(
        first_registration_date__gte="2022-05-10 00:00:00+00:00"
    )

    household_ids_second_or = (
        Individual.objects.filter(Q(bank_account_info__isnull=False) & ~Q(bank_account_info__bank_account_number=""))
        .filter(
            duplicate=False,
            withdrawn=False,
            household__in=households2,
            birth_date__gt="2004-08-11",
            households_and_roles__role="PRIMARY",
            disability="disabled",
        )
        .values_list("household_id")
        .distinct("household_id")
    )
    hhs = (
        households.filter(Q(id__in=household_ids_first_or) | Q(id__in=household_ids_second_or))
        .distinct()
        .values_list("id", flat=True)
    )
    list(hhs)
    print(time.time() - start)
    # print(len(hhs))
    return hhs


def not_optimized_household_query():
    from hct_mis_api.apps.targeting.models import TargetPopulation
    import time
    tp = TargetPopulation.objects.get(name="asd")
    start = time.time()
    hhs = tp.candidate_list.values_list("id", flat=True)
    list(hhs)
    print(time.time() - start)
    # print(len(hhs))
    return hhs


def track_time():
    import time
    iterations = 30
    total_time = 0
    for i in range(iterations):
        start = time.time()
        optimized_household_query()
        total_time+= time.time() - start
    print('optimize avg', total_time/iterations)

    total_time = 0
    for i in range(iterations):
        start = time.time()
        not_optimized_household_query()
        total_time+= time.time() - start

    print('not optimize avg', total_time/iterations)