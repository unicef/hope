import datetime
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from django.core.paginator import Paginator
from phonenumber_field.phonenumber import PhoneNumber

from hope.apps.grievance.models import TicketNeedsAdjudicationDetails
from hope.models.country import Country
from hope.models.household import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
)
from hope.models.individual import Individual
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.payment import Payment
from hope.models.payment_data_collector import PaymentDataCollector
from hope.models.payment_household_snapshot import PaymentHouseholdSnapshot
from hope.models.payment_plan import PaymentPlan

excluded_individual_fields = ["_state", "_prefetched_objects_cache"]
excluded_household_fields = ["_state", "_prefetched_objects_cache"]

encode_typedict: dict[type, Callable[[Any], Any]] = {
    UUID: lambda x: str(x),
    PhoneNumber: lambda x: str(x),
    datetime.datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
    datetime.date: lambda x: x.strftime("%Y-%m-%d"),
    Country: lambda x: x.iso_code3,
    Decimal: lambda x: str(x),
}

page_size = 100


def handle_type_mapping(value: Any) -> Any:
    value_type = type(value)
    if value_type in encode_typedict:
        value = encode_typedict[value_type](value)
    return value


def create_payment_plan_snapshot_data(payment_plan: PaymentPlan) -> None:
    payments_ids = list(
        payment_plan.eligible_payments.filter(household_snapshot__isnull=True)
        .values_list("id", flat=True)
        .order_by("id")
    )
    bulk_create_payment_snapshot_data(payments_ids)


def bulk_create_payment_snapshot_data(payments_ids: list[str]) -> None:
    payments_queryset = (
        Payment.objects.filter(id__in=payments_ids)
        .select_related("household")
        .prefetch_related(
            "household__individuals",
            "household__individuals__documents",
            "household__individuals_and_roles",
        )
        .order_by("id")
    )
    paginator = Paginator(payments_queryset, page_size)
    for page_number in paginator.page_range:
        payments = paginator.page(page_number).object_list
        to_create = [create_payment_snapshot_data(payment) for payment in payments]
        PaymentHouseholdSnapshot.objects.bulk_create(to_create)


def create_payment_snapshot_data(payment: Payment) -> PaymentHouseholdSnapshot:
    household = payment.household
    household_data = get_household_snapshot(household, payment)
    return PaymentHouseholdSnapshot(payment=payment, snapshot_data=household_data, household_id=household.id)


def get_household_snapshot(household: Household, payment: Payment | None = None) -> dict[Any, Any]:
    household_data = {}
    all_household_data_dict = household.__dict__
    keys = [key for key in all_household_data_dict if key not in excluded_household_fields]
    household_data["individuals"] = []
    household_data["roles"] = []
    for key in keys:
        value = all_household_data_dict[key]
        household_data[key] = handle_type_mapping(value)
    household_data["needs_adjudication_tickets_count"] = 0
    individuals_dict = {}
    for individual in household.individuals.all():
        individual_data = get_individual_snapshot(individual, payment)
        individuals_dict[str(individual.id)] = individual_data
        household_data["individuals"].append(individual_data)
        household_data["needs_adjudication_tickets_count"] += individual_data["needs_adjudication_tickets_count"]
    if household.primary_collector:
        if str(household.primary_collector.id) in individuals_dict:
            household_data["primary_collector"] = individuals_dict[str(household.primary_collector.id)]
        else:
            household_data["primary_collector"] = get_individual_snapshot(household.primary_collector, payment)
            household_data["needs_adjudication_tickets_count"] += household_data["primary_collector"][
                "needs_adjudication_tickets_count"
            ]
    if household.alternate_collector:
        if str(household.alternate_collector.id) in individuals_dict:
            household_data["alternate_collector"] = individuals_dict[str(household.alternate_collector.id)]
        else:
            household_data["alternate_collector"] = get_individual_snapshot(household.alternate_collector, payment)
            household_data["needs_adjudication_tickets_count"] += household_data["alternate_collector"][
                "needs_adjudication_tickets_count"
            ]
    for role in household.individuals_and_roles.all():
        household_data["roles"].append(
            {
                "role": role.role,
                "individual": get_individual_snapshot(role.individual, payment),
            }
        )
    return household_data


def get_individual_snapshot(individual: Individual, payment: Payment | None = None) -> dict:
    all_individual_data_dict = individual.__dict__
    keys = [key for key in all_individual_data_dict if key not in excluded_individual_fields]
    individual_data = {}
    for key in keys:
        value = all_individual_data_dict[key]
        individual_data[key] = handle_type_mapping(value)
    individual_data["documents"] = []
    individual_data["needs_adjudication_tickets_count"] = get_needs_adjudication_tickets_count(individual)

    for document in individual.documents.all():
        document_data = {
            "type": document.type.key,
            "document_number": document.document_number,
            "expiry_date": handle_type_mapping(document.expiry_date),
            "issuance_date": handle_type_mapping(document.issuance_date),
            "country": handle_type_mapping(document.country),
            "status": document.status,
            "cleared": document.cleared,
            "cleared_by": handle_type_mapping(document.cleared_by),
            "cleared_date": handle_type_mapping(document.cleared_date),
            "photo": document.photo.name if document.photo else "",
        }
        individual_data["documents"].append(document_data)

    is_hh_collector = IndividualRoleInHousehold.objects.filter(
        role__in=[ROLE_PRIMARY, ROLE_ALTERNATE],
        household=individual.household,
        individual=individual,
    ).exists()

    if is_hh_collector and payment and payment.delivery_type:
        individual_data["account_data"] = PaymentDataCollector.delivery_data(
            payment.financial_service_provider,
            payment.delivery_type,
            individual,
        )

    return individual_data


def get_needs_adjudication_tickets_count(individual: Individual) -> int:
    golden_records_count = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual=individual).count()
    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through  # noqa
    possible_duplicates_count = (
        PossibleDuplicateThrough.objects.filter(individual=individual)
        .distinct("ticketneedsadjudicationdetails")
        .count()
    )
    return golden_records_count + possible_duplicates_count
