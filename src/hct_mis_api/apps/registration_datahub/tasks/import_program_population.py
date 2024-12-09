from django.db.models import Q
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.utils import CopyProgramPopulation
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.models import MergeStatusModel


def import_program_population(
    import_from_program_id: str, import_to_program_id: str, rdi: RegistrationDataImport
) -> None:
    # filter by IDs based on program DCT
    import_from_ids = rdi.import_from_ids or ""
    list_of_ids = [item.strip() for item in import_from_ids.split(",")]
    import_to_program = get_object_or_404(Program, pk=import_to_program_id)
    individual_ids_q = Q(id__in=list_of_ids) if import_to_program.is_social_worker_program else Q()
    household_ids_q = Q() if import_to_program.is_social_worker_program else Q(id__in=list_of_ids)

    copy_from_households = Household.objects.filter(
        household_ids_q,
        program=import_from_program_id,
        withdrawn=False,
    ).exclude(household_collection__households__program_id=import_to_program_id)
    copy_from_individuals = (
        Individual.objects.filter(
            individual_ids_q,
            program_id=import_from_program_id,
            withdrawn=False,
            duplicate=False,
        )
        .exclude(individual_collection__individuals__program_id=import_to_program_id)
        .order_by("first_registration_date")
    )

    CopyProgramPopulation(
        copy_from_individuals=copy_from_individuals,
        copy_from_households=copy_from_households,
        program=import_to_program,
        rdi_merge_status=MergeStatusModel.PENDING,
        create_collection=False,
        rdi=rdi,
    ).copy_program_population()
