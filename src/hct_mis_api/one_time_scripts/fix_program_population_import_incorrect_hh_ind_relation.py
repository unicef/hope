from django.db.models import F

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


def fix_program_population_import_incorrect_hh_ind_relation() -> None:
    individuals = Individual.all_objects.filter(
        registration_data_import__data_source=RegistrationDataImport.PROGRAM_POPULATION,
    ).exclude(household__registration_data_import=F("registration_data_import"))

    for individual in individuals:
        household = Household.all_objects.filter(
            registration_data_import=individual.registration_data_import,
            copied_from_id=individual.household.copied_from_id,
            copied_from__isnull=False,
            program=individual.program,
        ).first()
        if household and household.unicef_id == individual.household.unicef_id:
            individual.household = household
            individual.save(update_fields=["household"])
