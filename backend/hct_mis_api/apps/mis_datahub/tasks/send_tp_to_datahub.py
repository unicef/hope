from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone

from core.utils import nested_getattr
from household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from mis_datahub import models as dh_mis_models
from targeting.models import TargetPopulation, HouseholdSelection


class SendTPToDatahubTask:
    MAPPING_TP_DICT = {
        "mis_id": "id",
        "name": "name",
        "active_households": "final_list_total_households",
        "program_mis_id": "program.id",
    }
    MAPPING_PROGRAM_DICT = {
        "mis_id": "id",
        "name": "name",
        "business_area": "business_area.code",
        "scope": "scope",
        "start_date": "start_date",
        "end_date": "end_date",
        "description": "description",
    }

    MAPPING_HOUSEHOLD_DICT = {
        "mis_id": "id",
        "status": "status",
        "household_size": "size",
        "address": "address",
        "admin1": "admin_area.title",
        "admin2": "admin_area.parent.title",
        "residence_status": "residence_status",
        "registration_date": "registration_date",
    }
    MAPPING_INDIVIDUAL_DICT = {
        "mis_id": "id",
        "status": "status",
        "full_name": "full_name",
        "family_name": "family_name",
        "given_name": "given_name",
        "middle_name": "middle_name",
        "sex": "sex",
        "date_of_birth": "birth_date",
        "estimated_date_of_birth": "estimated_birth_date",
        "relationship": "relationship",
        "role": "role",
        "marital_status": "marital_status",
        "phone_number": "phone_number",
        "household_mis_id": "household.id",
    }

    def execute(self):
        target_populations = TargetPopulation.objects.filter(
            status=TargetPopulation.STATUS_FINALIZED, sent_to_datahub=False
        )
        for target_population in target_populations:
            self.send_tp(target_population)

    @transaction.atomic(using="default")
    @transaction.atomic(using="cash_assist_datahub_mis")
    def send_tp(self, target_population):
        households_to_bulk_create = []
        individuals_to_bulk_create = []
        tp_entries_to_bulk_create = []
        dh_session = dh_mis_models.Session(
            source=dh_mis_models.Session.SOURCE_MIS,
            status=dh_mis_models.Session.STATUS_READY,
        )
        dh_session.save()
        target_population_selections = HouseholdSelection.objects.filter(
            target_population__id=target_population.id, final=True
        )
        households = target_population.households.filter(
            Q(last_sync_at__isnull=True) | Q(last_sync_at__lte=F("updated_at"))
        )
        # individuals = Individual.objects.filter(
        #     household__id__in=target_population.households.values_list(
        #         "id", flat=True
        #     )
        # ).filter(
        #     Q(last_sync_at__isnull=True)
        #     | Q(last_sync_at__lte=F("updated_at"))
        # )

        program = target_population.program
        if (
            program.last_sync_at is None
            or program.last_sync_at < program.updated_at
        ):
            dh_program = self.send_program(program)
            dh_program.session = dh_session
            dh_program.save()
            program.last_sync_at = timezone.now()
            program.save(update_fields=["last_sync_at"])
        dh_target = self.send_target_population(target_population)
        dh_target.session = dh_session
        dh_target.save()
        for household in households:
            (dh_household, dh_individuals) = self.send_household(
                household, dh_session
            )
            dh_household.session = dh_session
            households_to_bulk_create.append(dh_household)
            individuals_to_bulk_create.extend(dh_individuals)

        for selection in target_population_selections:
            dh_entry = self.send_target_entry(selection)
            dh_entry.session = dh_session
            tp_entries_to_bulk_create.append(dh_entry)
        dh_mis_models.Household.objects.bulk_create(households_to_bulk_create)
        dh_mis_models.Individual.objects.bulk_create(individuals_to_bulk_create)
        dh_mis_models.TargetPopulationEntry.objects.bulk_create(
            tp_entries_to_bulk_create
        )
        target_population.sent_to_datahub = True
        target_population.save()
        households.update(last_sync_at=timezone.now())

    def build_arg_dict(self, model_object, mapping_dict):
        args = {}
        for key in mapping_dict:
            args[key] = nested_getattr(model_object, mapping_dict[key], None)
        return args

    def send_program(self, program):
        dh_program_args = self.build_arg_dict(
            program, SendTPToDatahubTask.MAPPING_PROGRAM_DICT
        )

        dh_program = dh_mis_models.Program(**dh_program_args)
        return dh_program

    def send_target_population(self, target_population):
        dh_tp_args = self.build_arg_dict(
            target_population, SendTPToDatahubTask.MAPPING_TP_DICT
        )
        dh_target = dh_mis_models.TargetPopulation(**dh_tp_args)
        return dh_target

    def send_individual(self, individual, dh_household):
        dh_individual_args = self.build_arg_dict(
            individual, SendTPToDatahubTask.MAPPING_INDIVIDUAL_DICT
        )
        dh_individual = dh_mis_models.Individual(**dh_individual_args)
        dh_individual.household = dh_household

        national_id_document = individual.documents.filter(
            type__type=IDENTIFICATION_TYPE_NATIONAL_ID
        ).first()
        if national_id_document:
            dh_individual.national_id_number = (
                national_id_document.document_number
            )
        dh_individual.unchr_id = self.get_unhcr_individual_id(individual)
        return dh_individual

    def send_household(self, household, dh_session):
        dh_household_args = self.build_arg_dict(
            household, SendTPToDatahubTask.MAPPING_HOUSEHOLD_DICT
        )
        dh_household = dh_mis_models.Household(**dh_household_args)
        dh_household.country = household.country.alpha3
        households_identity = household.identities.filter(
            agency__type="unhcr"
        ).first()
        if households_identity is not None:
            dh_household.agency_id = households_identity.document_number

        head_of_household = household.head_of_household
        individuals_to_create = []
        dh_hoh = self.send_individual(head_of_household, dh_household)
        dh_hoh.session = dh_session
        individuals_to_create.append(dh_hoh)
        primary_collector = household.individuals.filter(
            role=ROLE_PRIMARY
        ).first()
        if (
            primary_collector is not None
            and primary_collector.id != head_of_household.id
        ):
            dh_primary_collector = self.send_individual(
                primary_collector, dh_household
            )
            dh_primary_collector.session = dh_session
            individuals_to_create.append(dh_primary_collector)
        alternative_collector = household.individuals.filter(
            role=ROLE_ALTERNATE
        ).first()
        if (
            alternative_collector is not None
            and alternative_collector.id != head_of_household.id
        ):
            dh_alternative_collector = self.send_individual(
                primary_collector, dh_household
            )
            dh_alternative_collector.session = dh_session
            individuals_to_create.append(dh_alternative_collector)
        return dh_household, individuals_to_create

    def send_target_entry(self, target_population_selection):
        households_identity = target_population_selection.household.identities.filter(
            agency__type="unhcr"
        ).first()
        household_unhcr_id = None
        if households_identity is not None:
            household_unhcr_id = households_identity.document_number
        return dh_mis_models.TargetPopulationEntry(
            target_population_mis_id=target_population_selection.target_population.id,
            household_mis_id=target_population_selection.household.id,
            household_unhcr_id=household_unhcr_id,
            vulnerability_score=target_population_selection.vulnerability_score,
        )

    def get_unhcr_individual_id(self, individual):
        identity = individual.identities.filter(agency__type="unhcr").first()
        if identity is not None:
            return identity.number
        return None
