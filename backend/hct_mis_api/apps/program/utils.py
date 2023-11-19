from typing import Tuple

from django.db import transaction

from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.household.models import (
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.program.validators import validate_data_collecting_type


def copy_program_object(copy_from_program_id: str, program_data: dict) -> Program:
    program = Program.objects.get(id=copy_from_program_id)
    admin_areas = program.admin_areas.all()
    program.pk = None
    program.status = Program.DRAFT

    data_collecting_type_code = program_data.pop("data_collecting_type_code", None)
    if data_collecting_type_code:
        data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)
    else:
        data_collecting_type = program.data_collecting_type

    validate_data_collecting_type(program.data_collecting_type, data_collecting_type, program.business_area)

    program_data["data_collecting_type_id"] = data_collecting_type.id

    for field_name, value in program_data.items():
        setattr(program, field_name, value)

    program.save()
    program.admin_areas.set(admin_areas)
    program.refresh_from_db()
    return program


def copy_program_related_data(copy_from_program_id: str, new_program: Program) -> None:
    copy_individuals_from_whole_program(copy_from_program_id, new_program)
    copy_households_from_whole_program(copy_from_program_id, new_program)
    copy_household_related_data(new_program)
    copy_individual_related_data(new_program)
    create_program_cycle(new_program)


def create_program_cycle(program: Program) -> None:
    ProgramCycle.objects.create(
        program=program,
        start_date=program.start_date,
        end_date=program.end_date,
        status=ProgramCycle.ACTIVE,
    )


def copy_individuals_from_whole_program(copy_from_program_id: str, program: Program) -> None:
    copied_from_individuals = Individual.objects.filter(
        program_id=copy_from_program_id, withdrawn=False, duplicate=False
    )
    for individual in copied_from_individuals:
        if not individual.individual_collection:
            individual.individual_collection = IndividualCollection.objects.create()
            individual.save()
        copied_from_pk = individual.pk
        individual.pk = None
        individual.program = program
        individual.copied_from_id = copied_from_pk
        individual.save()


def copy_households_from_whole_program(copy_from_program_id: str, program: Program) -> None:
    copy_from_households = Household.objects.filter(
        program_id=copy_from_program_id,
        withdrawn=False,
    )
    for household in copy_from_households:
        if not household.household_collection:
            household.household_collection = HouseholdCollection.objects.create()
            household.save()
        copy_from_household_id = household.pk
        household.pk = None
        household.program = program
        household.total_cash_received = None
        household.total_cash_received_usd = None
        household.copied_from_id = copy_from_household_id
        household.head_of_household = Individual.objects.get(
            program=program,
            copied_from=household.head_of_household,
        )
        household.save()
        return household


def copy_household_related_data(program: Program) -> None:
    new_households = Household.objects.filter(program=program).select_related("copied_from")
    for new_household in new_households:
        copy_roles_per_household(new_household, program)
        copy_entitlement_cards_per_household(new_household)


def copy_roles_per_household(new_household: Household, program: Program) -> None:
    copied_from_roles = IndividualRoleInHousehold.objects.filter(household=new_household.copied_from)

    for role in copied_from_roles:
        role.pk = None
        role.household = new_household
        role.individual = Individual.objects.get(
            program=program,
            copied_from=role.individual,
        )
        role.save()


def copy_entitlement_cards_per_household(new_household: Household) -> None:
    old_entitlement_cards = new_household.copied_from.entitlement_cards.all()
    for entitlement_card in old_entitlement_cards:
        entitlement_card.pk = None
        entitlement_card.household = new_household
        entitlement_card.save()


def copy_individual_related_data(program: Program) -> None:
    new_individuals = Individual.objects.filter(program=program)
    for new_individual in new_individuals:
        set_household_per_individual(new_individual, program)
        copy_documents_per_individual(new_individual)
        copy_individual_identities_per_individual(new_individual)
        copy_bank_account_info_per_individual(new_individual)


def set_household_per_individual(new_individual: Individual, program: Program) -> None:
    new_individual.household = Household.objects.get(
        program=program,
        copied_from_id=new_individual.household_id,
    )
    new_individual.save()


def copy_documents_per_individual(new_individual: Individual) -> None:
    old_documents = new_individual.copied_from.documents.all()
    for document in old_documents:
        document.pk = None
        document.program = new_individual.program
        document.individual = new_individual
        document.save()


def copy_individual_identities_per_individual(new_individual: Individual) -> None:
    old_individual_identities = new_individual.copied_from.identities.all()
    for individual_identity in old_individual_identities:
        individual_identity.pk = None
        individual_identity.individual = new_individual
        individual_identity.save()


def copy_bank_account_info_per_individual(new_individual: Individual) -> None:
    old_bank_account_info = new_individual.copied_from.bank_account_info.all()
    for bank_account_info in old_bank_account_info:
        bank_account_info.pk = None
        bank_account_info.individual = new_individual
        bank_account_info.save()


def enrol_household_to_program(household: Household, program: Program) -> Tuple[Household, int]:
    if household.program == program:
        return household, 0
    elif household_representation_in_new_program := Household.original_and_repr_objects.filter(
        program=program,
        copied_from=household,
    ).first():
        return household_representation_in_new_program, 0
    with transaction.atomic():
        return create_new_household_representation(household, program), 1


def create_new_household_representation(household: Household, program: Program) -> Household:
    if not household.household_collection:
        household.household_collection = HouseholdCollection.objects.create()
        household.save()
    individuals_pk = [ind.pk for ind in household.individuals.all()]
    original_household_id = household.id
    original_head_of_household_id = household.head_of_household.pk
    household.copied_from_id = original_household_id
    household.pk = None
    household.unicef_id = None
    household.program = program
    household.total_cash_received = None
    household.total_cash_received_usd = None

    # create individuals
    individuals_to_create = []
    for individual in Individual.objects.filter(pk__in=individuals_pk):
        individuals_to_create.append(enrol_individual_to_program(individual, program))

    # assign head of household
    household.head_of_household = Individual.original_and_repr_objects.filter(
        program=program,
        copied_from_id=original_head_of_household_id,
    ).first()
    household.save()

    for individual in individuals_to_create:
        individual.household = household

    Individual.original_and_repr_objects.bulk_update(individuals_to_create, ["household"])

    # create roles for new household representation
    create_roles_for_new_representation(household, program)

    return household


def enrol_individual_to_program(
    individual: Individual,
    program: Program,
) -> Individual:
    if individual_representation_in_new_program := Individual.original_and_repr_objects.filter(
        program=program,
        copied_from=individual,
    ).first():
        return individual_representation_in_new_program
    else:
        return create_new_individual_representation(individual, program)


def create_new_individual_representation(
    individual: Individual,
    program: Program,
) -> Individual:
    if not individual.individual_collection:
        individual.individual_collection = IndividualCollection.objects.create()
        individual.save()
    original_individual_id = individual.id
    individual.copied_from_id = original_individual_id
    individual.pk = None
    individual.unicef_id = None
    individual.program = program
    individual.household = None
    individual.save()
    individual.refresh_from_db()
    # create individual related data
    copy_documents_per_individual(individual)
    copy_individual_identities_per_individual(individual)
    copy_bank_account_info_per_individual(individual)

    return individual


def create_roles_for_new_representation(new_household: Household, program: Program) -> None:
    old_roles = IndividualRoleInHousehold.objects.filter(
        household=new_household.copied_from,
    )
    for role in old_roles:
        individual_representation = Individual.original_and_repr_objects.filter(
            program=program,
            copied_from=role.individual,
        ).first()
        if not individual_representation:
            individual_representation = create_new_individual_representation(
                program=program, individual=role.individual
            )

        role.pk = None
        role.household = new_household
        role.individual = individual_representation
        role.save()
