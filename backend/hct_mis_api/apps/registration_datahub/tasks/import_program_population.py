from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import CopyProgramPopulation
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.models import MergeStatusModel


def import_program_population(import_from_program_id: str, import_to_program_id: str, rdi: RegistrationDataImport):
    copy_from_households = Household.objects.filter(
        program=import_from_program_id,
        withdrawn=False,
    ).exclude(household_collection__households__program_id=import_to_program_id)
    copy_from_individuals = (
        Individual.objects.filter(
            program_id=import_from_program_id,
            withdrawn=False,
            duplicate=False,
        )
        .exclude(individual_collection__individuals__program_id=import_to_program_id)
        .order_by("first_registration_date")
    )
    import_to_program = Program.objects.get(id=import_to_program_id)

    CopyProgramPopulation(
        copy_from_individuals=copy_from_individuals,
        copy_from_households=copy_from_households,
        program=import_to_program,
        rdi_merge_status=MergeStatusModel.PENDING,
        create_collection=False,
        rdi=rdi,
    ).copy_program_population()
