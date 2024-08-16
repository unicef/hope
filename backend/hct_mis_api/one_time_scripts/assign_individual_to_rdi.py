from django.db.models import Count

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


def assign_individual_to_rdi() -> None:
    for program in Program.objects.all():
        # create RDI only if exists any individual without RDI
        individual_qs = Individual.objects.filter(program=program, registration_data_import__isnull=True)

        # TODO: do we need assign HH.registration_data_import ???

        if individual_qs.exists():
            rdi = RegistrationDataImport.objects.create(
                name="RDI for Individuals [data migration]",
                status=RegistrationDataImport.MERGED,
                imported_by=None,
                data_source=RegistrationDataImport.XLS,
                number_of_individuals=individual_qs.count(),
                number_of_households=individual_qs.aggregate(household_count=Count("household", distinct=True))[
                    "household_count"
                ],
                business_area=program.business_area,
                program_id=program.id,
                import_data=None,
            )
            print("rdi_id ===  ", rdi.id)
            individual_qs.update(registration_data_import=rdi)
