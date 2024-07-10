from django.db.models import Q

from hct_mis_api.apps.core.attributes_qet_queries import age_to_birth_date_query
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketReferralDetails,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
    TicketNeedsAdjudicationDetails,
    TicketSystemFlaggingDetails,
    TicketIndividualDataUpdateDetails,
    TicketSensitiveDetails,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
)
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate


class PeriodicDataUpdateExportTemplateService:
    def __init__(self, periodic_data_update_template: PeriodicDataUpdateTemplate):
        self.periodic_data_update_template = periodic_data_update_template
        self.program = periodic_data_update_template.program
        self.registration_data_import_id_filter = periodic_data_update_template.filters.get(
            "registration_data_import_id"
        )
        self.target_population_id_filter = periodic_data_update_template.filters.get("target_population_id")
        self.gender_filter = periodic_data_update_template.filters.get("gender")
        self.age_filter = periodic_data_update_template.filters.get("age")
        self.registration_date_filter = periodic_data_update_template.filters.get("registration_date")
        self.has_grievance_ticket_filter = periodic_data_update_template.filters.get("has_grievance_ticket")
        self.admin1_filter = periodic_data_update_template.filters.get("admin1")
        self.admin2_filter = periodic_data_update_template.filters.get("admin2")
        self.received_assistance_filter = periodic_data_update_template.filters.get("received_assistance")

    def _get_individuals_queryset(self):
        queryset = Individual.objects
        queryset = queryset.filter(program=self.program)
        if self.registration_data_import_id_filter:
            queryset = queryset.filter(registration_data_import_id=self.registration_data_import_id_filter)
        if self.target_population_id_filter:
            queryset = queryset.filter(target_population_id=self.target_population_id_filter)
        if self.gender_filter:
            queryset = queryset.filter(sex=self.gender_filter)
        if self.age_filter:
            age_from = self.age_filter.get("from")
            age_to = self.age_filter.get("to")
            q = age_to_birth_date_query("RANGE", [age_from, age_to])
            queryset = queryset.filter(q)
        if self.registration_date_filter:
            registration_date_from = self.registration_date_filter.get("from")
            registration_date_to = self.registration_date_filter.get("to")
            queryset = queryset.filter(first_registration_date__range=[registration_date_from, registration_date_to])

        if self.admin1_filter:
            queryset = queryset.filter(admin1__in=self.admin1_filter)
        if self.admin2_filter:
            queryset = queryset.filter(admin2__in=self.admin2_filter)
        if self.has_grievance_ticket_filter:
            queryset = self._get_grievance_ticket_filter(queryset)

    def _get_grievance_ticket_filter(self, queryset):
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
        ticket_individual_ids = {}
        for ticket_model, individual_field_name in ticket_details_individual_field:
            ticket_individual_ids.update(
                ticket_model.objects.filter({f"{individual_field_name}__in": individuals_ids})
                .exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
                .values_list(individual_field_name, flat=True)
            )
        PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
        ticket_individual_ids.update(
            PossibleDuplicateThrough.objects.filter(individual__in=individuals_ids)
            .exclude(ticket_needs_adjudication_details__ticket__status=GrievanceTicket.STATUS_CLOSED)
            .values_list("individual_id", flat=True)
        )

        return queryset.filter(id__in=ticket_individual_ids)

    def _get_received_assistance_filter(self, queryset):
        individuals_ids = (
            Payment.objects.filter(individual__in=queryset)
            .filter(Q(status=Payment.STATUS_DISTRIBUTION_PARTIAL) | Q(status=Payment.STATUS_DISTRIBUTION_SUCCESS))
            .values_list("individual_id", flat=True)
        )
        return queryset.filter(id__in=individuals_ids)
