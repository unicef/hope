"""
One-time script to fix RDI data for social worker programs where households were not imported
when importing by household IDs from another program.

This script:
1. Finds all RDIs for social worker programs that were imported using household IDs
3. Copies the missing households from the source program to the target program
"""

from hope.apps.program.utils import CopyProgramPopulation
from hope.models import RegistrationDataImport, Program, Household, Individual, DataCollectingType


def process_rdi(rdi: RegistrationDataImport, program: Program) -> bool:
    """
    Process a single RDI to fix missing households.
    Returns True if the RDI was fixed, False otherwise.
    """
    try:
        ids_list = [id.strip() for id in rdi.import_from_ids.split(",") if id.strip()]
        household_ids = [id for id in ids_list if id.startswith("HH-")]

        if not household_ids:
            return False

        print(f"RDI {rdi.id}: Found {len(household_ids)} household IDs")

        # Check if individuals were imported but households are missing
        imported_individuals = Individual.all_merge_status_objects.filter(
            program=program,
            registration_data_import=rdi,
        )
        imported_households = Household.all_merge_status_objects.filter(
            program=program,
            registration_data_import=rdi,
        )

        individuals_count = imported_individuals.count()
        households_count = imported_households.count()

        if individuals_count == 0 or households_count > 0:
            return False

        print(f"Households missing")

        if not (source_program := imported_individuals.first().copied_from.program):
            return False

        # Get households that are already in the target program to exclude them
        households_to_exclude = Household.all_merge_status_objects.filter(
            program=program,
        ).values_list("unicef_id", flat=True)

        source_households = Household.objects.filter(
            program=source_program,
            unicef_id__in=household_ids,
            withdrawn=False,
        ).exclude(unicef_id__in=households_to_exclude)

        if source_households.count() == 0:
            print(f"No source households to copy (IDs: {household_ids})")
            return False

        print(f"Found {source_households.count()} households to copy from source program")

        # Verify that individuals from these households exist in target program
        source_household_unicef_ids = list(source_households.values_list("unicef_id", flat=True))
        expected_individuals = Individual.objects.filter(
            program=source_program,
            household__unicef_id__in=source_household_unicef_ids,
            withdrawn=False,
            duplicate=False,
        )
        expected_individual_unicef_ids = set(expected_individuals.values_list("unicef_id", flat=True))

        existing_individuals_in_target = Individual.all_merge_status_objects.filter(
            program=program,
            unicef_id__in=expected_individual_unicef_ids,
        )
        existing_individual_unicef_ids = set(existing_individuals_in_target.values_list("unicef_id", flat=True))

        missing_individuals = expected_individual_unicef_ids - existing_individual_unicef_ids
        if missing_individuals:
            print(f"WARNING: Missing individual IDs: {list(missing_individuals)}")
            print(f"Skipping this RDI to avoid creating incomplete household data")
            return False

        # Copy households
        empty_individuals = Individual.objects.none()

        CopyProgramPopulation(
            copy_from_individuals=empty_individuals,
            copy_from_households=source_households,
            program=program,
            rdi_merge_status=imported_individuals.first().rdi_merge_status,
            create_collection=False,
            rdi=rdi,
        ).copy_program_population()

        # Update individuals to assign copied households
        newly_copied_households = Household.all_merge_status_objects.filter(
            program=program,
            registration_data_import=rdi,
        )

        household_mapping = {
            household.copied_from.unicef_id: household
            for household in newly_copied_households
        }

        individuals_to_update = []
        for individual in imported_individuals:
            if not individual.household and individual.copied_from:
                source_household_id = individual.copied_from.household.unicef_id
                new_household = household_mapping.get(source_household_id)
                if new_household:
                    individual.household = new_household
                    individuals_to_update.append(individual)

        if individuals_to_update:
            Individual.all_merge_status_objects.bulk_update(individuals_to_update, ["household"])
            print(f"Updated {len(individuals_to_update)} individuals to link to households")

        print(f"FIXED: Copied {source_households.count()} households")
        return True

    except Exception as e:
        print(f"ERROR processing RDI {rdi.id}: {str(e)}")
        return False


def fix_social_worker_rdi_missing_households():
    print("Starting to fix missing households...")
    social_programs = Program.objects.filter(
        data_collecting_type__type=DataCollectingType.Type.SOCIAL
    )
    fixed_count = 0

    for program in social_programs:
        rdis = RegistrationDataImport.objects.filter(
            program=program,
            data_source=RegistrationDataImport.PROGRAM_POPULATION,
            import_from_ids__isnull=False,
        ).exclude(import_from_ids="")

        for rdi in rdis:
            if process_rdi(rdi, program):
                fixed_count += 1

    print(f"Script finished. Fixed: {fixed_count} RDIs")
