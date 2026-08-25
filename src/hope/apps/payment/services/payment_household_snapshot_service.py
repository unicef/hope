from dataclasses import dataclass
import datetime
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from phonenumber_field.phonenumber import PhoneNumber

from hope.apps.grievance.models import TicketNeedsAdjudicationDetails
from hope.apps.household.const import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hope.models import (
    Country,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Payment,
    PaymentDataCollector,
    PaymentHouseholdSnapshot,
    PaymentPlan,
)
from hope.models.payment_data_collector import DeliveryDataByCollector


@dataclass(frozen=True)
class PaymentSnapshotContext:
    delivery_data_by_individual_id: DeliveryDataByCollector
    collector_ids: set[UUID]
    needs_adjudication_counts: dict[UUID, int]


excluded_individual_fields = ["_state", "_prefetched_objects_cache"]
excluded_household_fields = ["_state", "_prefetched_objects_cache"]

encode_typedict: dict[type, Callable[[Any], Any]] = {
    UUID: str,
    PhoneNumber: str,
    datetime.datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
    datetime.date: lambda x: x.strftime("%Y-%m-%d"),
    Country: lambda x: x.iso_code3,
    Decimal: str,
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
    base_queryset = Payment.objects.filter(id__in=payments_ids).order_by("id")
    paginator = Paginator(base_queryset, page_size)

    for page_number in paginator.page_range:
        # Slice without prefetch
        page_ids = list(paginator.page(page_number).object_list.values_list("id", flat=True))

        # Re-fetch with select/prefetch
        payments = list(
            Payment.objects.filter(id__in=page_ids)
            .select_related(
                "delivery_type__account_type",
                "financial_service_provider",
                "household",
            )
            .prefetch_related(
                Prefetch(
                    "household__individuals",
                    queryset=Individual.objects.select_related("household__country").prefetch_related(
                        Prefetch(
                            "documents",
                            queryset=Document.objects.select_related("type", "country", "cleared_by"),
                        ),
                        Prefetch(
                            "identities",
                            queryset=IndividualIdentity.objects.select_related("partner", "country"),
                        ),
                    ),
                ),
                Prefetch(
                    "household__individuals_and_roles",
                    queryset=IndividualRoleInHousehold.objects.select_related(
                        "individual__household__country"
                    ).prefetch_related(
                        Prefetch(
                            "individual__documents",
                            queryset=Document.objects.select_related("type", "country", "cleared_by"),
                        ),
                        Prefetch(
                            "individual__identities",
                            queryset=IndividualIdentity.objects.select_related("partner", "country"),
                        ),
                    ),
                ),
            )
            .order_by("id")
        )

        individuals_by_id: dict[UUID, Individual] = {}
        collector_ids: set[UUID] = set()
        collector_ids_by_household_id: dict[UUID, set[UUID]] = {}
        for payment in payments:
            for individual in payment.household.individuals.all():
                individuals_by_id[individual.id] = individual
            household_collector_ids = collector_ids_by_household_id.setdefault(payment.household_id, set())
            for role in payment.household.individuals_and_roles.all():
                individuals_by_id.setdefault(role.individual_id, role.individual)
                if role.role in [ROLE_PRIMARY, ROLE_ALTERNATE]:
                    collector_ids.add(role.individual_id)
                    household_collector_ids.add(role.individual_id)

        collectors = [
            individuals_by_id[collector_id] for collector_id in collector_ids if collector_id in individuals_by_id
        ]
        delivery_data_by_payment_key: dict[tuple[UUID, UUID], DeliveryDataByCollector] = {}
        for payment in payments:
            if payment.delivery_type and payment.financial_service_provider:
                payment_key = (payment.financial_service_provider_id, payment.delivery_type_id)
                if payment_key not in delivery_data_by_payment_key:
                    delivery_data_by_payment_key[payment_key] = PaymentDataCollector.delivery_data_for_collectors(
                        payment.financial_service_provider,
                        payment.delivery_type,
                        collectors,
                    )

        needs_adjudication_counts = get_needs_adjudication_tickets_counts(individuals_by_id)
        to_create = [
            create_payment_snapshot_data(
                payment,
                PaymentSnapshotContext(
                    delivery_data_by_individual_id=delivery_data_by_payment_key.get(
                        (payment.financial_service_provider_id, payment.delivery_type_id),
                        {},
                    ),
                    collector_ids=collector_ids_by_household_id.get(payment.household_id, set()),
                    needs_adjudication_counts=needs_adjudication_counts,
                ),
            )
            for payment in payments
        ]
        PaymentHouseholdSnapshot.objects.bulk_create(to_create)


def create_payment_snapshot_data(
    payment: Payment,
    context: PaymentSnapshotContext,
) -> PaymentHouseholdSnapshot:
    household = payment.household
    household_data = get_household_snapshot(household, payment, context)
    return PaymentHouseholdSnapshot(payment=payment, snapshot_data=household_data, household_id=household.id)


def get_household_snapshot(
    household: Household,
    payment: Payment | None = None,
    context: PaymentSnapshotContext | None = None,
) -> dict[Any, Any]:
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
        individual_data = get_individual_snapshot(
            individual,
            payment,
            context,
        )
        individuals_dict[str(individual.id)] = individual_data
        household_data["individuals"].append(individual_data)
        household_data["needs_adjudication_tickets_count"] += individual_data["needs_adjudication_tickets_count"]

    roles = list(household.individuals_and_roles.all())
    primary_collector = next((role.individual for role in roles if role.role == ROLE_PRIMARY), None)
    alternate_collector = next((role.individual for role in roles if role.role == ROLE_ALTERNATE), None)
    if primary_collector:
        if str(primary_collector.id) in individuals_dict:
            household_data["primary_collector"] = individuals_dict[str(primary_collector.id)]
        else:
            household_data["primary_collector"] = get_individual_snapshot(
                primary_collector,
                payment,
                context,
            )
            household_data["needs_adjudication_tickets_count"] += household_data["primary_collector"][
                "needs_adjudication_tickets_count"
            ]
    if alternate_collector:
        if str(alternate_collector.id) in individuals_dict:
            household_data["alternate_collector"] = individuals_dict[str(alternate_collector.id)]
        else:
            household_data["alternate_collector"] = get_individual_snapshot(
                alternate_collector,
                payment,
                context,
            )
            household_data["needs_adjudication_tickets_count"] += household_data["alternate_collector"][
                "needs_adjudication_tickets_count"
            ]
    for role in roles:
        household_data["roles"].append(
            {
                "role": role.role,
                "individual": individuals_dict.get(str(role.individual_id))
                or get_individual_snapshot(
                    role.individual,
                    payment,
                    context,
                ),
            }
        )
    return household_data


def get_individual_snapshot(
    individual: Individual,
    payment: Payment | None,
    context: PaymentSnapshotContext | None,
) -> dict:
    all_individual_data_dict = individual.__dict__
    keys = [key for key in all_individual_data_dict if key not in excluded_individual_fields]
    individual_data = {}
    for key in keys:
        value = all_individual_data_dict[key]
        individual_data[key] = handle_type_mapping(value)
    individual_data["documents"] = []
    individual_data["needs_adjudication_tickets_count"] = (
        context.needs_adjudication_counts.get(individual.id, 0)
        if context is not None
        else get_needs_adjudication_tickets_count(individual)
    )

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

    individual_data["identities"] = []
    for identity in individual.identities.all():
        identity_data = {
            "partner": identity.partner.name if identity.partner else "",
            "number": identity.number,
            "country": handle_type_mapping(identity.country),
        }
        individual_data["identities"].append(identity_data)

    if (
        payment
        and context
        and payment.delivery_type
        and payment.financial_service_provider
        and individual.id in context.collector_ids
    ):
        individual_data["account_data"] = context.delivery_data_by_individual_id.get(individual.id, {})

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


def get_needs_adjudication_tickets_counts(individuals_by_id: dict[UUID, Individual]) -> dict[UUID, int]:
    individual_ids = set(individuals_by_id)
    golden_records_counts: dict[UUID, int] = {
        row["golden_records_individual_id"]: row["count"]
        for row in TicketNeedsAdjudicationDetails.objects.filter(golden_records_individual_id__in=individual_ids)
        .values("golden_records_individual_id")
        .annotate(count=Count("id"))
    }
    PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through  # noqa
    possible_duplicates_counts: dict[UUID, int] = {
        row["individual_id"]: row["count"]
        for row in PossibleDuplicateThrough.objects.filter(individual_id__in=individual_ids)
        .values("individual_id")
        .annotate(count=Count("ticketneedsadjudicationdetails_id", distinct=True))
    }
    return {
        individual_id: golden_records_counts.get(individual_id, 0) + possible_duplicates_counts.get(individual_id, 0)
        for individual_id in individual_ids
    }
