from django.db.models import QuerySet

from typing import Any

from hope.apps.core.attributes_qet_queries import age_to_birth_date_query
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hope.apps.household.models import Individual
from hope.apps.payment.models import Payment
from hope.apps.program.models import Program


class PDUDataExtractionService:
    def __init__(self, program: Program, filters: dict):
        self.program = program
        self.filters = filters
        self.registration_data_import_id_filter = self.filters.get("registration_data_import_id")
        self.target_population_id_filter = self.filters.get("target_population_id")
        self.gender_filter = self.filters.get("gender")
        self.age_filter = self.filters.get("age")
        self.registration_date_filter = self.filters.get("registration_date")
        self.has_grievance_ticket_filter = self.filters.get("has_grievance_ticket")
        self.admin1_filter = self.filters.get("admin1")
        self.admin2_filter = self.filters.get("admin2")
        self.received_assistance_filter = self.filters.get("received_assistance")

    def _get_individuals_queryset(self) -> QuerySet[Individual]:
        queryset = Individual.objects.filter(program=self.program).order_by("unicef_id")
        if self.registration_data_import_id_filter:
            queryset = queryset.filter(registration_data_import_id=self.registration_data_import_id_filter)
        if self.target_population_id_filter:
            queryset = queryset.filter(household__payment__parent_id=self.target_population_id_filter)
        if self.gender_filter:
            queryset = queryset.filter(sex=self.gender_filter)
        if self.age_filter:
            age_from = self.age_filter.get("from")
            age_to = self.age_filter.get("to")
            queryset = queryset.filter(age_to_birth_date_query("RANGE", [age_from, age_to]))
        if self.registration_date_filter:
            registration_date_from = self.registration_date_filter.get("from")
            registration_date_to = self.registration_date_filter.get("to")
            if not registration_date_from and not registration_date_to:
                pass
            elif not registration_date_to:
                queryset = queryset.filter(first_registration_date__gte=registration_date_from)
            elif not registration_date_from:
                queryset = queryset.filter(first_registration_date__lte=registration_date_to)
            else:
                queryset = queryset.filter(
                    first_registration_date__range=[
                        registration_date_from,
                        registration_date_to,
                    ]
                )

        if self.admin1_filter:
            queryset = queryset.filter(household__admin1__in=self.admin1_filter)
        if self.admin2_filter:
            queryset = queryset.filter(household__admin2__in=self.admin2_filter)
        if self.has_grievance_ticket_filter:
            queryset = self._get_grievance_ticket_filter(queryset)
        elif self.has_grievance_ticket_filter is False:
            queryset = self._get_grievance_ticket_filter(queryset, exclude=True)
        if self.received_assistance_filter:
            queryset = self._get_received_assistance_filter(queryset)
        elif self.received_assistance_filter is False:
            queryset = self._get_received_assistance_filter(queryset, exclude=True)
        return queryset.distinct()

    def _get_grievance_ticket_filter(
        self, queryset: QuerySet[Individual], exclude: bool = False
    ) -> QuerySet[Individual]:
        ticket_details_individual_field = [
            (TicketReferralDetails, "individual_id"),
            (TicketNegativeFeedbackDetails, "individual_id"),
            (TicketPositiveFeedbackDetails, "individual_id"),
            (TicketNeedsAdjudicationDetails, "golden_records_individual_id"),
            (TicketSystemFlaggingDetails, "golden_records_individual_id"),
            (TicketDeleteIndividualDetails, "individual_id"),
            (TicketIndividualDataUpdateDetails, "individual_id"),
            (TicketSensitiveDetails, "individual_id"),
            (TicketComplaintDetails, "individual_id"),
        ]
        individuals_ids = queryset.values_list("id", flat=True)
        ticket_individual_ids = set()
        for ticket_model, individual_field_name in ticket_details_individual_field:
            ids = [
                str(x)
                for x in ticket_model.objects.filter(**{f"{individual_field_name}__in": individuals_ids})
                .exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
                .values_list(individual_field_name, flat=True)
            ]
            ticket_individual_ids.update(ids)
        PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through  # noqa
        ids = [
            str(x)
            for x in PossibleDuplicateThrough.objects.filter(individual__in=individuals_ids)
            .exclude(ticketneedsadjudicationdetails__ticket__status=GrievanceTicket.STATUS_CLOSED)
            .values_list("individual_id", flat=True)
        ]
        ticket_individual_ids.update(ids)
        if exclude:
            return queryset.exclude(id__in=ticket_individual_ids)
        return queryset.filter(id__in=ticket_individual_ids)

    def _get_received_assistance_filter(
        self, queryset: QuerySet[Individual], exclude: bool = False
    ) -> QuerySet[Individual]:
        individuals_ids = (
            Payment.objects.filter(household__in=queryset.values_list("household", flat=True))
            .filter(status__in=[Payment.STATUS_DISTRIBUTION_PARTIAL, Payment.STATUS_DISTRIBUTION_SUCCESS])
            .values_list("household_id", flat=True)
        )
        if exclude:
            return queryset.exclude(household_id__in=individuals_ids)
        return queryset.filter(household_id__in=individuals_ids)


class PDURoundValueMixin:
    @staticmethod
    def _get_round_value(
        individual: Individual, pdu_field_name: str, round_number: int
    ) -> str | int | float | bool | None:
        flex_fields_data = individual.flex_fields
        field_data = flex_fields_data.get(pdu_field_name)
        if field_data:
            round_data = field_data.get(str(round_number))
            if round_data:
                return round_data.get("value")
        return None

    @staticmethod
    def set_round_value(
        individual: Individual,
        pdu_field_name: str,
        round_number: int,
        value: Any,
        collection_date: Any,
    ) -> None:
        flex_fields_data = individual.flex_fields
        if pdu_field_name not in flex_fields_data:
            flex_fields_data[pdu_field_name] = {}
        field_data = flex_fields_data[pdu_field_name]
        if str(round_number) not in field_data:
            field_data[str(round_number)] = {}
        round_data = field_data.get(str(round_number))
        round_data["value"] = value
        round_data["collection_date"] = collection_date
