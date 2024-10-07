import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, Optional
from uuid import UUID

from django.contrib.gis.geos import Point
from django.core.paginator import Paginator

from phonenumber_field.phonenumber import PhoneNumber

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import TicketNeedsAdjudicationDetails
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
)

excluded_individual_fields = ["_state", "_prefetched_objects_cache"]
excluded_household_fields = ["_state", "_prefetched_objects_cache"]

encode_typedict: Dict[type, Callable[[Any], Any]] = {
    UUID: lambda x: str(x),
    PhoneNumber: lambda x: str(x),
    datetime.datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
    datetime.date: lambda x: x.strftime("%Y-%m-%d"),
    Country: lambda x: x.iso_code3,
    Point: lambda x: str(x),
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
            "household__individuals__bank_account_info",
        )
        .order_by("id")
    )
    paginator = Paginator(payments_queryset, page_size)
    for page_number in paginator.page_range:
        to_create = []
        payments = paginator.page(page_number).object_list
        for payment in payments:
            to_create.append(create_payment_snapshot_data(payment))
        PaymentHouseholdSnapshot.objects.bulk_create(to_create)


def create_payment_snapshot_data(payment: Payment) -> PaymentHouseholdSnapshot:
    household = payment.household
    household_data = {}
    all_household_data_dict = household.__dict__
    keys = [key for key in all_household_data_dict.keys() if key not in excluded_household_fields]
    household_data["individuals"] = []
    household_data["roles"] = []
    for key in keys:
        value = all_household_data_dict[key]
        household_data[key] = handle_type_mapping(value)
    household_data["needs_adjudication_tickets_count"] = 0
    individuals_dict = {}
    for individual in household.individuals.all():
        individual_data = get_individual_snapshot(individual)
        individuals_dict[str(individual.id)] = individual_data
        household_data["individuals"].append(individual_data)
        household_data["needs_adjudication_tickets_count"] += individual_data["needs_adjudication_tickets_count"]

    if household.primary_collector:
        if str(household.primary_collector.id) in individuals_dict:
            household_data["primary_collector"] = individuals_dict[str(household.primary_collector.id)]
        else:
            household_data["primary_collector"] = get_individual_snapshot(household.primary_collector)
            household_data["needs_adjudication_tickets_count"] += household_data["primary_collector"][
                "needs_adjudication_tickets_count"
            ]
    if household.alternate_collector:
        if str(household.alternate_collector.id) in individuals_dict:
            household_data["alternate_collector"] = individuals_dict[str(household.alternate_collector.id)]
        else:
            household_data["alternate_collector"] = get_individual_snapshot(
                household.alternate_collector,
            )
            household_data["needs_adjudication_tickets_count"] += household_data["alternate_collector"][
                "needs_adjudication_tickets_count"
            ]
    for role in household.individuals_and_roles.all():
        household_data["roles"].append({"role": role.role, "individual": get_individual_snapshot(role.individual)})
    return PaymentHouseholdSnapshot(payment=payment, snapshot_data=household_data, household_id=household.id)


def get_individual_snapshot(individual: Individual) -> dict:
    all_individual_data_dict = individual.__dict__
    keys = [key for key in all_individual_data_dict.keys() if key not in excluded_individual_fields]
    individual_data = {}
    for key in keys:
        value = all_individual_data_dict[key]
        individual_data[key] = handle_type_mapping(value)
    individual_data["documents"] = []
    individual_data["needs_adjudication_tickets_count"] = get_needs_adjudication_tickets_count(individual)
    individual_data["bank_account_info"] = {}

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

    bank_account_info: Optional[BankAccountInfo] = individual.bank_account_info.first()
    if bank_account_info:
        individual_data["bank_account_info"] = {
            "bank_name": bank_account_info.bank_name,
            "bank_account_number": bank_account_info.bank_account_number,
            "debit_card_number": bank_account_info.debit_card_number,
            "bank_branch_name": bank_account_info.bank_branch_name,
            "account_holder_name": bank_account_info.account_holder_name,
        }

    is_hh_collector = IndividualRoleInHousehold.objects.filter(
        role__in=[ROLE_PRIMARY, ROLE_ALTERNATE], household=individual.household, individual=individual
    ).exists()

    if is_hh_collector:
        individual_data["delivery_mechanisms_data"] = {
            dmd.delivery_mechanism.code: dmd.delivery_data for dmd in individual.delivery_mechanisms_data.all()
        }

    return individual_data


def get_needs_adjudication_tickets_count(individual: Individual) -> int:
    golden_records_count = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual=individual).count()
    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
    possible_duplicates_count = (
        PossibleDuplicateThrough.objects.filter(individual=individual)
        .distinct("ticketneedsadjudicationdetails")
        .count()
    )
    return golden_records_count + possible_duplicates_count
