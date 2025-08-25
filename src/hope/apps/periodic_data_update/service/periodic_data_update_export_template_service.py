from tempfile import NamedTemporaryFile

import openpyxl
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction
from django.db.models import Q, QuerySet
from openpyxl.packaging.custom import StringProperty

from hope.apps.core.attributes_qet_queries import age_to_birth_date_query
from hope.apps.core.models import FileTemp
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
from hope.apps.periodic_data_update.models import PeriodicDataUpdateTemplate


class PeriodicDataUpdateExportTemplateService:
    PDU_SHEET = "Periodic Data Update"
    META_SHEET = "Meta"
    META_ID_ADDRESS = "B1"
    PROPERTY_ID_NAME = "pdu_template_id"

    def __init__(self, periodic_data_update_template: PeriodicDataUpdateTemplate):
        self.periodic_data_update_template = periodic_data_update_template
        self.rounds_data = periodic_data_update_template.rounds_data
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

    def generate_workbook(self) -> openpyxl.Workbook:
        try:
            with transaction.atomic():
                self._create_workbook()
                self._add_meta()
                self.ws_pdu.append(self._generate_header())
                for round_info_data in self.rounds_data:
                    round_info_data["number_of_records"] = 0
                self.periodic_data_update_template.number_of_records = 0
                queryset = self._get_individuals_queryset()
                for individual in queryset:
                    row = self._generate_row(individual)
                    if row:
                        self.periodic_data_update_template.number_of_records += 1
                        self.ws_pdu.append(row)
                return self.wb
        except Exception:
            self.periodic_data_update_template.status = PeriodicDataUpdateTemplate.Status.FAILED
            self.periodic_data_update_template.save()
            raise

    def save_xlsx_file(self) -> None:
        filename = f"Periodic Data Update Template {self.periodic_data_update_template.pk}.xlsx"
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.periodic_data_update_template.pk,
                content_type=get_content_type_for_model(self.periodic_data_update_template),
                created_by=self.periodic_data_update_template.created_by,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.periodic_data_update_template.file = xlsx_obj
            self.periodic_data_update_template.status = PeriodicDataUpdateTemplate.Status.EXPORTED
            self.periodic_data_update_template.save()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_pdu = wb.active
        ws_pdu.title = PeriodicDataUpdateExportTemplateService.PDU_SHEET
        self.wb = wb
        self.ws_pdu = ws_pdu
        self.ws_meta = wb.create_sheet(PeriodicDataUpdateExportTemplateService.META_SHEET)
        return wb

    def _add_meta(self) -> None:
        self.ws_meta["A1"] = "Periodic Data Update Template ID"
        self.ws_meta[self.META_ID_ADDRESS] = self.periodic_data_update_template.pk
        self.wb.custom_doc_props.append(
            StringProperty(
                name=self.PROPERTY_ID_NAME,
                value=str(self.periodic_data_update_template.pk),
            )
        )

    def _generate_header(self) -> list[str]:
        header = [
            "individual__uuid",
            "individual_unicef_id",
            "first_name",
            "last_name",
        ]
        for round_info_data in self.rounds_data:
            header.extend(
                [
                    f"{round_info_data['field']}__round_number",
                    f"{round_info_data['field']}__round_name",
                    f"{round_info_data['field']}__round_value",
                    f"{round_info_data['field']}__collection_date",
                ]
            )
        return header

    def _generate_row(self, individual: Individual) -> list[str] | None:
        individual_uuid = individual.pk
        individual_unicef_id = individual.unicef_id
        first_name = individual.given_name
        last_name = individual.family_name
        row = [str(individual_uuid), individual_unicef_id, first_name, last_name]
        is_individual_allowed = False
        for round_info_data in self.rounds_data:
            pdu_field_name = round_info_data["field"]
            round_number = round_info_data["round"]
            round_name = round_info_data["round_name"]
            round_value = self._get_round_value(individual, pdu_field_name, round_number)
            if round_value is None:
                round_info_data["number_of_records"] = round_info_data["number_of_records"] + 1
                row.extend([round_number, round_name, "", ""])
            else:
                row.extend([round_number, round_name, "-", "-"])
            is_individual_allowed = is_individual_allowed or round_value is None
        if not is_individual_allowed:
            return None
        return row

    def _get_round_value(
        self, individual: Individual, pdu_field_name: str, round_number: int
    ) -> str | int | float | bool | None:
        flex_fields_data = individual.flex_fields
        field_data = flex_fields_data.get(pdu_field_name)
        if field_data:
            round_data = field_data.get(str(round_number))
            if round_data:
                return round_data.get("value")
        return None

    def _get_individuals_queryset(self) -> QuerySet[Individual]:
        queryset = Individual.objects.all()
        queryset = queryset.filter(program=self.program)
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
            .filter(Q(status=Payment.STATUS_DISTRIBUTION_PARTIAL) | Q(status=Payment.STATUS_DISTRIBUTION_SUCCESS))
            .values_list("household_id", flat=True)
        )
        if exclude:
            return queryset.exclude(household_id__in=individuals_ids)
        return queryset.filter(household_id__in=individuals_ids)
