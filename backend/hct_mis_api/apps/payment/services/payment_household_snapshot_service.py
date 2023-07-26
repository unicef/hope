import datetime
from uuid import UUID

from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from phonenumber_field.phonenumber import PhoneNumber

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import TicketNeedsAdjudicationDetails
from hct_mis_api.apps.payment.models import PaymentHouseholdSnapshot, Payment

excluded_individual_fields = ["_state", "_prefetched_objects_cache"]
excluded_household_fields = ["_state", "_prefetched_objects_cache"]
encode_typedict = {
    UUID: lambda x: str(x),
    PhoneNumber: lambda x: str(x),
    datetime.datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
    datetime.date: lambda x: x.strftime("%Y-%m-%d"),
    Country: lambda x: x.iso_code3,
    Point: lambda x: str(x),
}


def handle_type_mapping(value):
    value_type = type(value)
    if value_type in encode_typedict:
        value = encode_typedict[value_type](value)
    return value


def create_payment_plan_snapshot_data(payment_plan):
    payments_ids = list(
        Payment.objects.filter(parent=payment_plan, household_snapshot__isnull=True).values_list("id", flat=True)
    )
    payments_queryset = (
        Payment.objects.filter(id__in=payments_ids)
        .select_related("household")
        .prefetch_related(
            "household__individuals", "household__individuals__documents", "household__individuals_and_roles"
        )
    )
    page_size = 1000
    paginator = Paginator(payments_queryset, page_size)
    queryset_count = payments_queryset.count()
    for page_number in paginator.page_range:
        to_create = []
        print(f"Processing page {page_number}/{queryset_count / page_size}")
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
    all_household_data_dict["roles"] = []
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
            household_data["alternate_collector"] = get_individual_snapshot(household.alternate_collector)
            household_data["needs_adjudication_tickets_count"] += household_data["alternate_collector"][
                "needs_adjudication_tickets_count"
            ]
    for role in household.individuals_and_roles.all():
        all_household_data_dict["roles"].append(
            {"role": role.role, "individual": get_individual_snapshot(role.individual)}
        )
    print(household_data)
    print("-------------------" * 10)
    return PaymentHouseholdSnapshot(payment=payment, snapshot_data=household_data, household_id=household.id)


def get_individual_snapshot(individual):
    all_individual_data_dict = individual.__dict__
    keys = [key for key in all_individual_data_dict.keys() if key not in excluded_individual_fields]
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
        }
        individual_data["documents"].append(document_data)
    return individual_data


def get_needs_adjudication_tickets_count(individual):
    golden_records_count = TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual=individual).count()
    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
    possible_duplicates_count = (
        PossibleDuplicateThrough.objects.filter(individual=individual)
        .distinct("ticketneedsadjudicationdetails")
        .count()
    )
    return golden_records_count + possible_duplicates_count
