from django.db import transaction

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import copy_individual_related_data2, copy_household_related_data2, \
    copy_households_from_whole_program2, copy_individuals_from_whole_program2
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.models import MergeStatusModel


def import_program_population(import_from_program_id: str, import_to_program: Program, rdi: RegistrationDataImport):
    copy_from_households = Household.objects.filter(
        program=import_from_program_id,
        withdrawn=False,
    ).exclude(household_collection__households__program=import_to_program)
    copy_from_individuals = (
        Individual.objects.filter(
            program_id=import_from_program_id,
            withdrawn=False,
            duplicate=False,
        )
        .exclude(individual_collection__individuals__program=import_to_program)
        .order_by("first_registration_date")
    )
    with transaction.atomic():
        copy_individuals_from_whole_program2(
            copy_from_individuals,
            import_to_program,
            rdi_merge_status=MergeStatusModel.PENDING,
            create_collection=False,
            rdi=rdi,
        )

        copy_households_from_whole_program2(
            copy_from_households,
            import_to_program,
            rdi_merge_status=MergeStatusModel.PENDING,
            create_collection=False,
            rdi=rdi,
        )

        new_households = Household.pending_objects.filter(program=import_to_program).select_related("copied_from")
        copy_household_related_data2(
            import_to_program,
            new_households,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        new_individuals = Individual.pending_objects.filter(program=import_to_program).select_related("copied_from")
        copy_individual_related_data2(
            import_to_program,
            new_individuals,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
