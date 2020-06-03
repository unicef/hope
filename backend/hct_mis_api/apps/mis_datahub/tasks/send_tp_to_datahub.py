from django.db.models import Q, F

from core.utils import nested_getattr
from household.models import (
    Individual,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_ALTERNATE,
)
from targeting.models import TargetPopulation, HouseholdSelection
from mis_datahub import models as dh_mis_models


class SendTPToDatahubTask:
    MAPPING_TP_DICT = {
        "mis_id": "id",
        "name": "name",
        "active_households": "final_list_total_households",
    }
    MAPPING_PROGRAM_DICT = {
        "mis_id": "id",
        "programme_name": "name",
        "business_area": "business_area.slug",
        "scope": "scope",
        "start_date": "start_date",
        "end_date": "end_date",
        "description": "description",
    }

    MAPPING_HOUSEHOLD_DICT = {
        "mis_id": "id",
        "status": "status",
        "household_size": "size",
        "focal_point": "head_of_household.id",
        "address": "address",
        "admin1": "admin_area.title",
        "admin2": "admin_area.parent.title",
        "country": "country",
    }
    MAPPING_INDIVIDUAL_DICT = {
        "mis_id": "id",
        "status": "status",
        "full_name": "full_name",
        "family_name": "family_name",
        "given_name": "given_name",
        "middle_name": "middle_name",
        "sex": "sex",
        "date_of_birth": "date_of_birth",
        "estimated_date_of_birth": "estimated_date_of_birth",
        "relationship": "relationship",
        "role": "role",
        "marital_status": "marital_status",
        "phone_number": "phone_number",
    }

    def execute(self):
        target_populations = TargetPopulation.objects.filter(
            status=TargetPopulation.STATUS_FINALIZED, sent_to_datahub=False
        )
        for target_population in target_populations:
            self.send_target_population(target_population)

    def send_tp(self, target_population):
        households_to_bulk_create = []
        individuals_to_bulk_create = []
        tp_entries_to_bulk_create = []

        target_population_selections = HouseholdSelection.objects.filter(
            target_population__id=target_population.id, final=True
        )
        households = target_population.households.filter(
            Q(last_sync_at_lte__is_null=True)
            | Q(last_sync_at_lte=F("updated_at"))
        )
        # individuals = Individual.objects.filter(
        #     household__id__in=target_population.households.values_list(
        #         "id", flat=True
        #     )
        # ).filter(
        #     Q(last_sync_at_lte__is_null=True)
        #     | Q(last_sync_at_lte=F("updated_at"))
        # )
        program = target_population.program
        dh_program = self.send_program(program)
        dh_program.save()
        dh_target = self.send_target_population(target_population, dh_program)
        dh_target.save()
        for household in households:
            dh_household = self.send_household(household)
            households_to_bulk_create.append(dh_household)
            hoh = household.head_of_household
            hoh_dh = self.send_individual(hoh, dh_household)
            individuals_to_bulk_create.append(hoh_dh)
            alternative_collector = household.individuals.filter(
                role=ROLE_ALTERNATE
            ).first()
            if alternative_collector is not None:
                alternative_collector_dh = self.send_individual(
                    alternative_collector, dh_household
                )
                individuals_to_bulk_create.append(alternative_collector_dh)
        for selection in target_population_selections:
            dh_entry = self.send_target_entry(selection)
            tp_entries_to_bulk_create.append(dh_entry)
        dh_mis_models.Household.objects.bulk_create(households_to_bulk_create)
        dh_mis_models.Individual.objects.bulk_create(individuals_to_bulk_create)
        dh_mis_models.TargetPopulationEntry.objects.bulk_create(
            tp_entries_to_bulk_create
        )

    def build_arg_dict(self, model_object, mapping_dict):
        args = {}
        for key in mapping_dict:
            args[key] = nested_getattr(model_object, mapping_dict[key], None)
        return args

    def send_program(self, program):
        dh_program_args = self.build_arg_dict(
            program, SendTPToDatahub.MAPPING_PROGRAM_DICT
        )
        dh_program = dh_mis_models.Program(**dh_program_args)
        return dh_program

    def send_target_population(self, target_population, dh_program):
        dh_tp_args = self.build_arg_dict(
            target_population, SendTPToDatahub.MAPPING_TP_DICT
        )

        dh_target = dh_mis_models.TargetPopulation(**dh_tp_args)
        dh_target.program = dh_program
        return dh_target

    def send_individual(self, individual, dh_household):
        dh_individual_args = self.build_arg_dict(
            individual, SendTPToDatahub.MAPPING_INDIVIDUAL_DICT
        )
        dh_individual = dh_mis_models.Individual(**dh_individual_args)
        dh_individual.household = dh_household
        return dh_individual

    def send_household(self, household):
        dh_household_args = self.build_arg_dict(
            household, SendTPToDatahub.MAPPING_HOUSEHOLD_DICT
        )
        dh_household = dh_mis_models.Household(**dh_household_args)
        national_id_document = household.head_of_household.documents.filter(
            type__type=IDENTIFICATION_TYPE_NATIONAL_ID
        ).first()
        if national_id_document is not None:
            dh_household.government_form_number = (
                national_id_document.document_number
            )
        households_identity = household.households_identities.first()
        if households_identity is not None:
            dh_household.agency_id = households_identity.document_number
        dh_household.save()
        return dh_household

    def send_target_entry(self, target_population_selection):
        return dh_mis_models.TargetPopulationEntry(
            target_population=target_population_selection.target_population.id,
            household=target_population_selection.houshehold.id,
            vulnerability_score=target_population_selection.vulnerability_score,
        )
