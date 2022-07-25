import logging

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from hct_mis_api.apps.core.models import CountryCodeMap
from hct_mis_api.apps.core.utils import nested_getattr, build_arg_dict
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    IndividualRoleInHousehold,
    Document,
    IndividualIdentity,
)
from hct_mis_api.apps.mis_datahub import models as dh_mis_models
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)


class SendTPToDatahubTask:
    MAPPING_TP_DICT = {
        "mis_id": "id",
        "name": "name",
        "active_households": "final_list_total_households",
        "program_mis_id": "program_id",
        "targeting_criteria": "targeting_criteria_string",
    }
    MAPPING_PROGRAM_DICT = {
        "mis_id": "id",
        "name": "name",
        "business_area": "business_area.cash_assist_code",
        "scope": "scope",
        "start_date": "start_date",
        "end_date": "end_date",
        "description": "description",
        "individual_data_needed": "individual_data_needed",
        "ca_id": "ca_id",
        "ca_hash_id": "ca_hash_id",
    }

    MAPPING_HOUSEHOLD_DICT = {
        "mis_id": "id",
        "unicef_id": "unicef_id",
        "status": "status",
        "household_size": "size",
        "address": "address",
        "admin1": "admin1.title",
        "admin2": "admin2.title",
        "residence_status": "residence_status",
        "registration_date": "last_registration_date",
        "village": "village",
    }
    MAPPING_INDIVIDUAL_DICT = {
        "mis_id": "id",
        "unicef_id": "unicef_id",
        "status": "cash_assist_status",
        "full_name": "full_name",
        "family_name": "family_name",
        "given_name": "given_name",
        "middle_name": "middle_name",
        "sex": "sex",
        "date_of_birth": "birth_date",
        "estimated_date_of_birth": "estimated_birth_date",
        "relationship": "relationship",
        "marital_status": "marital_status",
        "phone_number": "phone_no",
        "household_mis_id": "household_id",
        "pregnant": "pregnant",
        "sanction_list_confirmed_match": "sanction_list_confirmed_match",
    }
    MAPPING_DOCUMENT_DICT = {
        "mis_id": "id",
        "number": "document_number",
        "individual_mis_id": "individual_id",
        "type": "type.type",
    }

    def execute(self, target_population):
        return self.send_target_population(target_population)

    @transaction.atomic(using="default")
    @transaction.atomic(using="cash_assist_datahub_mis")
    def send_target_population(self, target_population):
        households_to_bulk_create = []
        individuals_to_bulk_create = []
        documents_to_bulk_create = []
        tp_entries_to_bulk_create = []
        roles_to_bulk_create = []

        try:
            with transaction.atomic(using="default"):
                with transaction.atomic(using="cash_assist_datahub_mis"):
                    program = target_population.program
                    self.dh_session = dh_mis_models.Session(
                        source=dh_mis_models.Session.SOURCE_MIS,
                        status=dh_mis_models.Session.STATUS_READY,
                        business_area=program.business_area.cash_assist_code,
                    )
                    self.dh_session.save()

                    (
                        documents_to_sync,
                        households_to_sync,
                        individuals_to_sync,
                        roles_to_sync,
                        target_population_selections,
                    ) = self._prepare_data_to_send(program, target_population)
                    self._send_program(program)
                    self._send_target_population_object(target_population)
                    for household in households_to_sync:
                        dh_household = self._prepare_datahub_object_household(household)
                        households_to_bulk_create.append(dh_household)

                    for individual in individuals_to_sync:
                        dh_individual = self._prepare_datahub_object_individual(individual)
                        individuals_to_bulk_create.append(dh_individual)

                    for role in roles_to_sync:
                        dh_role = self._prepare_datahub_object_role(role)
                        roles_to_bulk_create.append(dh_role)

                    for document in documents_to_sync:
                        dh_document = self._prepare_datahub_object_document(document)
                        documents_to_bulk_create.append(dh_document)

                    for selection in target_population_selections:
                        dh_target_population_selection = self._prepare_datahub_object_target_entry(selection)
                        tp_entries_to_bulk_create.append(dh_target_population_selection)

                    dh_mis_models.Household.objects.bulk_create(households_to_bulk_create)
                    dh_mis_models.Individual.objects.bulk_create(individuals_to_bulk_create)
                    dh_mis_models.IndividualRoleInHousehold.objects.bulk_create(roles_to_bulk_create)
                    dh_mis_models.Document.objects.bulk_create(documents_to_bulk_create)
                    dh_mis_models.TargetPopulationEntry.objects.bulk_create(tp_entries_to_bulk_create)
                    target_population.set_to_ready_for_cash_assist()
                    target_population.save()

                    households_to_sync.update(last_sync_at=timezone.now())
                    individuals_to_sync.update(last_sync_at=timezone.now())
                    return {
                        "session": self.dh_session.id,
                        "program": str(program),
                        "target_population": str(target_population),
                        "households_count": len(households_to_bulk_create),
                        "individuals_count": len(individuals_to_bulk_create),
                        "roles_count": len(roles_to_bulk_create),
                        "tp_entries_count": len(tp_entries_to_bulk_create),
                    }
        except Exception as e:
            logger.exception(e)
            raise

    def _prepare_data_to_send(self, program, target_population):
        (
            all_targeted_households_ids,
            households_to_sync,
            individuals_to_sync,
        ) = self._get_individuals_and_hauseholds(program, target_population)
        self._prepare_unhcr_dict(individuals_to_sync)
        documents = self._get_documents(individuals_to_sync)
        # household_id__in - to filter also by vulnerability_score score
        target_population_selections = (
            HouseholdSelection.objects.filter(
                target_population__id=target_population.id,
                final=True,
                household_id__in=all_targeted_households_ids,
            )
            .select_related("household")
            .distinct()
        )
        roles_to_sync = IndividualRoleInHousehold.objects.filter(
            Q(household__last_sync_at__isnull=True) | Q(household__last_sync_at__lte=F("household__updated_at")),
            household_id__in=all_targeted_households_ids,
        ).distinct()
        return documents, households_to_sync, individuals_to_sync, roles_to_sync, target_population_selections

    def _prepare_unhcr_dict(self, individuals_to_sync):
        individual_identities = IndividualIdentity.objects.filter(
            agency__type="UNHCR", individual__in=individuals_to_sync
        ).distinct()
        self.unhcr_id_dict = {identity.individual_id: identity.number for identity in individual_identities}

    def _get_individuals_and_hauseholds(self, program, target_population):
        all_targeted_households_ids = target_population.final_list.values_list("id", flat=True)
        if program.individual_data_needed:
            # all targeted individuals + collectors (primary_collector,alternate_collector)
            all_individuals = Individual.objects.filter(
                Q(household__id__in=all_targeted_households_ids)
                | Q(represented_households__in=all_targeted_households_ids)
            ).distinct()
        else:
            # only head of households + collectors (primary_collector,alternate_collector)
            all_individuals = Individual.objects.filter(
                (Q(heading_household__in=all_targeted_households_ids))
                | Q(represented_households__in=all_targeted_households_ids)
            ).distinct()
        all_households = Household.objects.filter(
            id__in=all_individuals.values_list("household_id", flat=True)
        ).distinct()
        households_to_sync = all_households.filter(
            Q(last_sync_at__isnull=True) | Q(last_sync_at__lte=F("updated_at"))
        ).distinct()
        individuals_to_sync = all_individuals.filter(
            Q(last_sync_at__isnull=True) | Q(last_sync_at__lte=F("updated_at"))
        ).distinct()
        return all_targeted_households_ids, households_to_sync, individuals_to_sync

    def _get_documents(self, individuals):
        return Document.objects.filter(individual__in=individuals).distinct()

    def _send_program(self, program):
        if not (program.last_sync_at is None or program.last_sync_at < program.updated_at):
            return
        dh_program_args = build_arg_dict(program, SendTPToDatahubTask.MAPPING_PROGRAM_DICT)
        dh_program = dh_mis_models.Program(**dh_program_args)
        dh_program.session = self.dh_session
        dh_program.save()

        program.last_sync_at = timezone.now()
        program.save(update_fields=["last_sync_at"])
        return dh_program

    def _send_target_population_object(self, target_population):
        dh_tp_args = build_arg_dict(target_population, SendTPToDatahubTask.MAPPING_TP_DICT)
        dh_target = dh_mis_models.TargetPopulation(**dh_tp_args)
        dh_target.session = self.dh_session
        dh_target.save()
        return dh_target

    def _prepare_datahub_object_household(self, household):
        dh_household_args = build_arg_dict(household, SendTPToDatahubTask.MAPPING_HOUSEHOLD_DICT)
        dh_household_args["country"] = CountryCodeMap.objects.get_code(household.country.code)
        dh_household = dh_mis_models.Household(**dh_household_args)
        dh_household.unhcr_id = self._get_unhcr_household_id(household)
        dh_household.session = self.dh_session
        return dh_household

    def _prepare_datahub_object_individual(self, individual):
        dh_individual_args = build_arg_dict(individual, SendTPToDatahubTask.MAPPING_INDIVIDUAL_DICT)
        dh_individual = dh_mis_models.Individual(**dh_individual_args)
        dh_individual.unhcr_id = self._get_unhcr_individual_id(individual)
        dh_individual.session = self.dh_session
        return dh_individual

    def _prepare_datahub_object_role(self, role):
        return dh_mis_models.IndividualRoleInHousehold(
            role=role.role,
            household_mis_id=role.household.id,
            individual_mis_id=role.individual.id,
            session=self.dh_session,
        )

    def _prepare_datahub_object_document(self, document):
        dh_document_args = build_arg_dict(document, SendTPToDatahubTask.MAPPING_DOCUMENT_DICT)
        dh_document = dh_mis_models.Document(
            **dh_document_args,
            session=self.dh_session,
        )
        return dh_document

    def _prepare_datahub_object_target_entry(self, target_population_selection):
        household_unhcr_id = self._get_unhcr_household_id(target_population_selection.household)
        return dh_mis_models.TargetPopulationEntry(
            target_population_mis_id=target_population_selection.target_population.id,
            household_mis_id=target_population_selection.household.id,
            household_unhcr_id=household_unhcr_id,
            vulnerability_score=target_population_selection.vulnerability_score,
            session=self.dh_session,
        )

    def _get_unhcr_individual_id(self, individual):
        return self.unhcr_id_dict.get(individual.id)

    def _get_unhcr_household_id(self, household):
        if household.unhcr_id == "":
            return None
        return household.unhcr_id

