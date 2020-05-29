from django.db.models import Q, F

from core.utils import nested_getattr
from household.models import Individual
from targeting.models import TargetPopulation, HouseholdSelection
from mis_datahub import models as dh_mis_models


class SendTPToDatahub:
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

    def execute(self, tp_id):
        target_population = TargetPopulation.objects.get(id=tp_id)
        target_population_selections = HouseholdSelection.objects.filter(
            target_population__id=tp_id
        )
        households = target_population.households.filter(
            Q(last_sync_at_lte__is_null=True)
            | Q(last_sync_at_lte=F("updated_at"))
        )
        individuals = Individual.objects.filter(
            household__id__in=target_population.households.values_list(
                "id", flat=True
            )
        ).filter(
            Q(last_sync_at_lte__is_null=True)
            | Q(last_sync_at_lte=F("updated_at"))
        )
        program = target_population.program
        dh_program = self.send_program(program)
        dh_target = self.send_target_population(target_population, dh_program)

    def build_arg_dict(self, model_object, mapping_dict):
        args = {}
        for key in mapping_dict:
            args[key] = nested_getattr(model_object, mapping_dict[key], None)
        return args

    def send_program(self, program):
        dh_program_args = self.build_arg_dict(
            program, SendTPToDatahub.MAPPING_PROGRAM_DICT
        )
        dh_program = dh_mis_models.Program(dh_program_args)
        dh_program.save()
        return dh_program

    def send_target_population(self, target_population, dh_program):
        dh_tp_args = self.build_arg_dict(
            target_population, SendTPToDatahub.MAPPING_TP_DICT
        )

        dh_target = dh_mis_models.TargetPopulation(dh_tp_args)
        dh_target.program = dh_program
        dh_target.save()
        return dh_target

    def send_households(self,household):