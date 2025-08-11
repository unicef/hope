from django.shortcuts import get_object_or_404

from hope.apps.program.models import Program
from hope.apps.program.utils import CopyProgramPopulation
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.registration_datahub.utils import get_rdi_program_population
from hope.apps.utils.models import MergeStatusModel


def import_program_population(
    import_from_program_id: str, import_to_program_id: str, rdi: RegistrationDataImport
) -> None:
    copy_from_households, copy_from_individuals = get_rdi_program_population(
        import_from_program_id, import_to_program_id, rdi.import_from_ids, rdi.exclude_external_collectors
    )
    import_to_program = get_object_or_404(Program, pk=import_to_program_id)

    CopyProgramPopulation(
        copy_from_individuals=copy_from_individuals,
        copy_from_households=copy_from_households,
        program=import_to_program,
        rdi_merge_status=MergeStatusModel.PENDING,
        create_collection=False,
        rdi=rdi,
    ).copy_program_population()
