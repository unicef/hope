from django.db.models import Prefetch, QuerySet

from hope.models import Individual, IndividualRoleInHousehold, Payment


def with_payment_related_data(queryset: QuerySet[Payment]) -> QuerySet[Payment]:
    """Preload the relations PaymentListSerializer reads."""
    role_prefetch = Prefetch(
        "households_and_roles",
        queryset=IndividualRoleInHousehold.all_objects.only("id", "role", "individual_id", "household_id"),
        to_attr="prefetched_roles",
    )
    individual_prefetch = Prefetch(
        "household__individuals",
        queryset=Individual.objects.only("id", "household_id", "full_name").prefetch_related(role_prefetch),
        to_attr="prefetched_individuals",
    )
    return (
        queryset.select_related(
            "currency",
            "household__admin2",
            "head_of_household",
            "collector",
            "household_snapshot",
            "financial_service_provider",
            "business_area",
            "program__business_area",
            "parent__program_cycle__program__data_collecting_type",
            "parent__delivery_mechanism",
            "parent__financial_service_provider",
            "parent__payment_plan_group",
        )
        .prefetch_related(
            individual_prefetch,
            "parent__payment_verification_plans",
            "payment_verifications",
            "parent__payment_plan_purposes",
        )
        .all()
    )
