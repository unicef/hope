import csv
import logging
import os
from collections import defaultdict
from copy import deepcopy
from itertools import chain
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_NONE,
    COLLECT_TYPE_PARTIAL,
    COLLECT_TYPE_SIZE_ONLY,
    COLLECT_TYPE_UNKNOWN,
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
BATCH_SIZE_SMALL = 20

# 1. migrate_data_to_representations()/migrate_data_to_representations_per_business_area(ba) - handles if new household was created and/or added to TP of program/if new RDI was created and any of its households was added to TP of program
# 2. copy_individual_sync - if new individual was added to household/external collector was added
# 3. copy_roles_sync - if new role was created - new repr has to be created, also needs to be checked if representation for individual needs to be created; if role for hh repr has been assigned to external individual, it is possible that this ind representation does not exist yet in this program
# 4 - Documents: copy_document_per_individual_fast, Identity: copy_individual_identity_per_individual_fast, BankAccountInfo: copy_bank_account_info_per_individual_fast


def migrate_data_to_representations() -> None:
    for business_area in BusinessArea.objects.all():
        logger.info("----- NEW BUSINESS AREA -----")
        logger.info(f"Handling business area: {business_area}")
        migrate_data_to_representations_per_business_area(business_area=business_area)


def migrate_data_to_representations_per_business_area(business_area: BusinessArea) -> None:
    """
    This function is used to migrate data from old models to new representations per business_area.
    Take TargetPopulations:
    - all for programs in status ACTIVE
    - in status STATUS_READY_FOR_PAYMENT_MODULE and STATUS_READY_FOR_CASH_ASSIST for programs in status FINISHED,
    delete other TargetPopulations
    For all households and individuals in given TargetPopulations:
    - create new representations
    - copy all objects related to old households/individuals
    - handle RDI: if there is RDI for household copy all households in this RDI to current program
    For whole business_area:
    - for rdi that was not related to program: add rdi and copy its households to the biggest program in that ba
    - adjust payments and payment_records to corresponding representations

    """
    unknown_unassigned_dict = get_unknown_unassigned_dict()
    unknown_unassigned_program = unknown_unassigned_dict.get(business_area)

    hhs_to_ignore = get_ignored_hhs() if business_area.name == "Afghanistan" else None

    for program in Program.objects.filter(
        business_area=business_area, status__in=[Program.ACTIVE, Program.FINISHED]
    ).order_by("status"):
        logger.info("----- NEW PROGRAM -----")
        logger.info(f"Creating representations for program: {program}")
        target_populations_ids = TargetPopulation.objects.filter(
            program=program,
        ).values_list("id", flat=True)

        household_selections = HouseholdSelection.original_and_repr_objects.filter(
            Q(target_population_id__in=target_populations_ids)
            & Q(is_original=True)
            & Q(is_migration_handled=False)
            & (
                Q(
                    target_population__status__in=[
                        TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
                        TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                    ]
                )
                | Q(household__withdrawn=False)
            )
        )
        household_ids = household_selections.distinct("household").values_list("household_id", flat=True)

        households = Household.original_and_repr_objects.filter(id__in=household_ids, is_original=True).order_by(
            "id"
        )  # without is_migration_handled filter because there can be handled household but assigned to new TP; so filter for nothandled HHselection is only needed now
        households_filtered = households.exclude(copied_to__program=program)
        households_filtered_ids = list(households_filtered.values_list("id", flat=True))
        households_count = len(households_filtered_ids)

        logger.info(f"Handling households for program: {program}")

        for batch_start in range(0, households_count, BATCH_SIZE):
            batch_end = batch_start + BATCH_SIZE
            logger.info(f"Handling {batch_start} - {batch_end}/{households_count} households")
            individuals_per_household_dict = defaultdict(list)
            batched_household_ids = households_filtered_ids[batch_start:batch_end]
            batched_households = Household.original_and_repr_objects.filter(id__in=batched_household_ids)
            for individual in Individual.original_and_repr_objects.filter(household__in=batched_households):
                individuals_per_household_dict[individual.household_id].append(individual)

            with transaction.atomic():
                for household in batched_households:
                    copy_household_representation_for_programs_fast(
                        household, program, individuals_per_household_dict[household.id]
                    )

        rdi_ids = households.values_list("registration_data_import_id", flat=True).distinct()
        rdis = RegistrationDataImport.objects.filter(id__in=rdi_ids)
        if program.status == Program.ACTIVE:
            logger.info(f"Handling RDIs for program: {program}")
            handle_rdis(rdis, program, hhs_to_ignore)
        else:
            rdis.filter(program__isnull=True).update(program=program)

        logger.info(f"Copying roles for program: {program}")
        copy_roles(households, program=program)

        logger.info(f"Copying household selections for program: {program}")
        copy_household_selections(household_selections, program)
        logger.info(f"Finished creating representations for program: {program}")
    logger.info("Updating is_migration_handled for households")
    # mark programs households as migrated and exclude in rerun
    Household.original_and_repr_objects.filter(
        business_area=business_area, copied_to__isnull=False, is_original=True, is_migration_handled=False
    ).update(is_migration_handled=True)
    logger.info("Handling objects without any representations yet - enrolling to storage programs")
    handle_non_program_objects(business_area, hhs_to_ignore, unknown_unassigned_program)

    logger.info("Updating Households with migration date")
    Household.original_and_repr_objects.filter(
        business_area=business_area,
        copied_to__isnull=False,
        is_original=True,
        is_migration_handled=False,
    ).update(
        is_migration_handled=True,
        migrated_at=timezone.now(),
    )

    logger.info("Updating Individuals with migration date")
    Individual.original_and_repr_objects.filter(
        business_area=business_area, is_original=True, copied_to__isnull=False, is_migration_handled=False
    ).update(
        is_migration_handled=True,
        migrated_at=timezone.now(),
    )

    logger.info("Updating IndividualRoleInHouseholds with migration date")
    IndividualRoleInHousehold.original_and_repr_objects.filter(
        household__business_area=business_area, is_original=True, copied_to__isnull=False, is_migration_handled=False
    ).update(is_migration_handled=True, migrated_at=timezone.now())

    if business_area.name == "Democratic Republic of Congo":
        apply_congo_withdrawal()


def get_household_representation_per_program_by_old_household_id(
    program: Program,
    old_household_id: str,
) -> Optional[Household]:
    return Household.original_and_repr_objects.filter(
        program=program,
        copied_from_id=old_household_id,
        is_original=False,
    ).first()


def get_individual_representation_per_program_by_old_individual_id(
    program: Program,
    old_individual_id: str,
) -> Optional[Individual]:
    return Individual.original_and_repr_objects.filter(
        program=program,
        copied_from_id=old_individual_id,
        is_original=False,
    ).first()


def copy_household_representation(
    household: Household,
    program: Program,
    individuals: list[Individual],
) -> Optional[Household]:
    """
    Copy household into representation for given program if it does not exist yet.
    """
    # copy representations only based on original households
    if household.is_original:
        # if there is no representation of this household in this program yet, copy the household
        if household_representation := Household.original_and_repr_objects.filter(
            program=program,
            copied_from=household,
            is_original=False,
        ).first():
            return household_representation
        else:
            return copy_household(household, program, individuals)
    return household


def copy_household_representation_for_programs_fast(
    household: Household,
    program: Program,
    individuals: list[Individual],
) -> Optional[Household]:
    """
    Copy household into representation for given program if it does not exist yet.
    """
    # copy representations only based on original households
    if household.is_original:
        return copy_household_fast(household, program, individuals)
    return household


def copy_household(household: Household, program: Program, individuals: list[Individual]) -> Household:
    copy = deepcopy(household)
    original_household_id = household.id
    original_unicef_id = household.unicef_id
    original_head_of_household_id = household.head_of_household_id
    copy.copied_from_id = original_household_id
    copy.origin_unicef_id = original_unicef_id
    copy.pk = None
    copy.unicef_id = original_unicef_id
    copy.program = program
    copy.is_original = False

    individuals_to_create = []
    for individual in individuals:
        individuals_to_create.append(copy_individual_representation(program, individual))

    copy.head_of_household = get_individual_representation_per_program_by_old_individual_id(
        program=program,
        old_individual_id=original_head_of_household_id,
    )
    Household.objects.bulk_create([copy])
    for individual in individuals_to_create:  # type: ignore
        individual.household = copy

    Individual.original_and_repr_objects.bulk_update(individuals_to_create, ["household"])

    # copy_entitlement_card_per_household(household=original_household, household_representation=household)

    del individuals_to_create
    return copy


def copy_household_fast(household: Household, program: Program, individuals: list[Individual]) -> Household:
    copy = deepcopy(household)
    original_household_id = household.id
    original_head_of_household_id = household.head_of_household_id
    original_unicef_id = household.unicef_id
    copy.copied_from_id = original_household_id
    copy.origin_unicef_id = original_unicef_id
    copy.pk = None
    copy.unicef_id = original_unicef_id
    copy.program = program
    copy.is_original = False
    external_collectors_id_to_update = []
    individuals_to_create = []
    documents_to_create = []
    identities_to_create = []
    bank_account_info_to_create = []
    individuals_to_exclude_dict = {
        str(x["copied_from_id"]): str(x["pk"])
        for x in Individual.original_and_repr_objects.filter(
            copied_from_id__in=individuals, is_original=False, program=program
        ).values("copied_from_id", "pk")
    }

    for individual in individuals:
        if str(individual.id) in individuals_to_exclude_dict:
            external_collectors_id_to_update.append(individuals_to_exclude_dict[str(individual.id)])
            continue
        (
            individual_to_create,
            documents_to_create_batch,
            identities_to_create_batch,
            bank_account_info_to_create_batch,
        ) = copy_individual_representation_fast(program, individual)
        documents_to_create.extend(documents_to_create_batch)
        identities_to_create.extend(identities_to_create_batch)
        bank_account_info_to_create.extend(bank_account_info_to_create_batch)
        individuals_to_create.append(individual_to_create)
    individuals_dict = {i.copied_from_id: i for i in individuals_to_create}
    Individual.objects.bulk_create(individuals_to_create)
    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(identities_to_create)
    BankAccountInfo.objects.bulk_create(bank_account_info_to_create)
    if original_head_of_household_id in individuals_dict:
        copy.head_of_household = individuals_dict[original_head_of_household_id]
    else:
        copy.head_of_household = get_individual_representation_per_program_by_old_individual_id(
            program, original_head_of_household_id
        )
    Household.objects.bulk_create([copy])
    ids_to_update = [x.pk for x in individuals_to_create] + external_collectors_id_to_update
    Individual.original_and_repr_objects.filter(id__in=ids_to_update).update(household=copy)

    # copy_entitlement_card_per_household(household=original_household, household_representation=household)

    del individuals_to_create
    return copy


def copy_individual_representation(
    program: Program,
    individual: Individual,
) -> Optional[Individual]:
    """
    Copy individual into representation for given program if it does not exist yet.
    Return existing representation if it exists.
    """
    # copy representations only based on original individuals
    if individual.is_original:
        # if there is no representation of this individual in this program yet, copy the individual
        if individual_representation := get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=individual.pk,
        ):
            return individual_representation
        else:
            return copy_individual(individual, program)
    else:
        return get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=individual.copied_from_id,
        )


def copy_individual_representation_fast(
    program: Program,
    individual: Individual,
) -> tuple:
    """
    Copy individual into representation for given program if it does not exist yet.
    Return existing representation if it exists.
    """
    # copy representations only based on original individuals
    if individual.is_original:
        return copy_individual_fast(individual, program.id)
    else:
        raise Exception("Cannot copy representation of representation")


def copy_individual(individual: Individual, program: Program) -> Individual:
    (
        individual_to_create,
        documents_to_create,
        identities_to_create,
        bank_account_info_to_create,
    ) = copy_individual_fast(individual, program.id)
    (created_individual,) = Individual.objects.bulk_create([individual_to_create])
    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(identities_to_create)
    BankAccountInfo.objects.bulk_create(bank_account_info_to_create)
    return created_individual


def copy_individual_fast(individual: Individual, program_id: str) -> tuple:
    documents = list(individual.documents(manager="original_and_repr_objects").all())
    identities = list(individual.identities(manager="original_and_repr_objects").all())
    bank_accounts_info = list(individual.bank_account_info(manager="original_and_repr_objects").all())

    copy = deepcopy(individual)

    original_individual_id = individual.id
    original_unicef_id = individual.unicef_id
    copy.copied_from_id = original_individual_id
    copy.origin_unicef_id = original_unicef_id
    copy.pk = None
    copy.unicef_id = original_unicef_id
    copy.program_id = program_id
    copy.household = None
    copy.is_original = False
    documents_to_create = copy_document_per_individual_fast(documents, copy)
    identities_to_create = copy_individual_identity_per_individual_fast(identities, copy)
    bank_account_info_to_create = copy_bank_account_info_per_individual_fast(bank_accounts_info, copy)
    return copy, documents_to_create, identities_to_create, bank_account_info_to_create


def copy_roles(households: QuerySet, program: Program) -> None:
    # filter only original roles
    roles_ids = list(
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            household__in=households,
            individual__is_removed=False,
            household__is_removed=False,
            is_original=True,
        )
        .exclude(copied_to__household__program=program)
        .distinct("individual", "household")
        .order_by("individual", "household")
        .values_list("id", flat=True)
    )

    roles_count = len(roles_ids)
    for batch_start in range(0, roles_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{roles_count} roles")
        roles_list = []
        roles_batch = IndividualRoleInHousehold.original_and_repr_objects.filter(
            id__in=roles_ids[batch_start:batch_end]
        ).select_related("individual", "household")
        original_individual_ids = [role.individual_id for role in roles_batch]
        original_household_ids = [role.household_id for role in roles_batch]
        household_representations = Household.original_and_repr_objects.filter(
            program=program,
            copied_from_id__in=original_household_ids,
        ).only("copied_from_id", "id")
        individual_representations = Individual.original_and_repr_objects.filter(
            program=program,
            copied_from_id__in=original_individual_ids,
        ).only("copied_from_id", "id")
        household_representations_dict = {
            household.copied_from_id: household for household in household_representations
        }
        individual_representation_dict = {
            individual.copied_from_id: individual for individual in individual_representations
        }
        individuals_to_create_batch = []
        documents_to_create_batch = []
        identities_to_create_batch = []
        bank_account_info_to_create_batch = []
        for role in roles_batch:
            household_representation = household_representations_dict[role.household_id]
            individual_representation = individual_representation_dict.get(role.individual_id)
            if not individual_representation:
                (
                    individual_representation,
                    documents_to_create_individual_batch,
                    identities_to_create_individual_batch,
                    bank_account_info_to_create_individual_batch,
                ) = copy_individual_representation_fast(program=program, individual=role.individual)
                individual_representation_dict[individual_representation.copied_from_id] = individual_representation
                individuals_to_create_batch.append(individual_representation)
                documents_to_create_batch.extend(documents_to_create_individual_batch)
                identities_to_create_batch.extend(identities_to_create_individual_batch)
                bank_account_info_to_create_batch.extend(bank_account_info_to_create_individual_batch)

            copy = deepcopy(role)
            original_role_id = role.id
            copy.copied_from_id = original_role_id
            copy.pk = None
            copy.household = household_representation
            copy.individual = individual_representation
            copy.is_original = False
            roles_list.append(copy)
        with transaction.atomic():
            Individual.objects.bulk_create(individuals_to_create_batch)
            Document.objects.bulk_create(documents_to_create_batch)
            IndividualIdentity.objects.bulk_create(identities_to_create_batch)
            BankAccountInfo.objects.bulk_create(bank_account_info_to_create_batch)
            IndividualRoleInHousehold.original_and_repr_objects.bulk_create(roles_list)
        del roles_list


def copy_entitlement_card_per_household(household: Household, household_representation: Household) -> None:
    entitlement_cards = household.entitlement_cards.all()
    entitlement_cards_list = []
    for entitlement_card in entitlement_cards:
        copy = deepcopy(entitlement_card)
        original_entitlement_card_id = entitlement_card.id
        copy.copied_from_id = original_entitlement_card_id
        copy.pk = None
        copy.household = household_representation
        copy.is_original = False
        entitlement_cards_list.append(copy)
    EntitlementCard.original_and_repr_objects.bulk_create(entitlement_cards_list)
    del entitlement_cards_list


def copy_document_per_individual_fast(
    documents: List[Document], individual_representation: Individual
) -> List[Document]:
    """
    Clone document for individual if new individual_representation has been created.
    """
    documents_list = []
    for document in documents:
        copy = deepcopy(document)
        original_document_id = document.id
        copy.copied_from_id = original_document_id
        copy.pk = None
        copy.individual = individual_representation
        copy.program_id = individual_representation.program_id
        copy.is_original = False
        documents_list.append(copy)
    return documents_list


def copy_individual_identity_per_individual_fast(
    identities: List[IndividualIdentity], individual_representation: Individual
) -> List[IndividualIdentity]:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    identities_list = []
    for identity in identities:
        copy = deepcopy(identity)
        original_identity_id = identity.id
        copy.copied_from_id = original_identity_id
        copy.pk = None
        copy.individual = individual_representation
        copy.is_original = False
        identities_list.append(copy)
    return identities_list


def copy_bank_account_info_per_individual_fast(
    bank_accounts_info: List[BankAccountInfo], individual_representation: Individual
) -> List[BankAccountInfo]:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    bank_accounts_info_list = []
    for bank_account_info in bank_accounts_info:
        copy = deepcopy(bank_account_info)
        copy.copied_from_id = bank_account_info.id
        copy.pk = None
        copy.individual = individual_representation
        copy.is_original = False
        bank_accounts_info_list.append(copy)
    return bank_accounts_info_list


def copy_document_per_individual(documents: List[Document], individual_representation: Individual) -> None:
    """
    Clone document for individual if new individual_representation has been created.
    """

    Document.original_and_repr_objects.bulk_create(
        copy_document_per_individual_fast(documents, individual_representation)
    )


def copy_individual_identity_per_individual(
    identities: List[IndividualIdentity], individual_representation: Individual
) -> None:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    IndividualIdentity.original_and_repr_objects.bulk_create(
        copy_individual_identity_per_individual_fast(identities, individual_representation)
    )


def copy_bank_account_info_per_individual(
    bank_accounts_info: List[BankAccountInfo], individual_representation: Individual
) -> None:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    BankAccountInfo.original_and_repr_objects.bulk_create(
        copy_bank_account_info_per_individual_fast(bank_accounts_info, individual_representation)
    )


def copy_household_selections(household_selections: QuerySet, program: Program) -> None:
    """
    Copy HouseholdSelections to new households representations. By this TargetPopulations are adjusted.
    Because TargetPopulation is per program, HouseholdSelections are per program.
    """
    household_selections_ids = list(
        household_selections.filter(household__is_removed=False).values_list("id", flat=True)
    )

    for batch_start in range(0, len(household_selections_ids), BATCH_SIZE):
        batched_ids = household_selections_ids[batch_start : batch_start + BATCH_SIZE]
        batched_household_selections = HouseholdSelection.original_and_repr_objects.filter(id__in=batched_ids)
        logger.info(f"Copying household selections {batch_start} of {len(household_selections_ids)}")
        household_selections_to_create = []
        household_ids = [x.household_id for x in batched_household_selections]
        household_representations = Household.original_and_repr_objects.filter(
            program=program, copied_from__in=household_ids
        ).values("id", "copied_from")
        household_representations_dict = {x["copied_from"]: x["id"] for x in household_representations}
        for household_selection in batched_household_selections:
            copy = deepcopy(household_selection)
            copy.pk = None
            copy.household_id = household_representations_dict[household_selection.household_id]
            copy.is_original = False
            household_selections_to_create.append(copy)

        with transaction.atomic():
            HouseholdSelection.original_and_repr_objects.bulk_create(household_selections_to_create)
            HouseholdSelection.original_and_repr_objects.filter(
                id__in=batched_household_selections.values_list("id", flat=True)
            ).update(is_migration_handled=True)


def handle_rdis(rdis: QuerySet, program: Program, hhs_to_ignore: Optional[QuerySet] = None) -> None:
    rdis_count = rdis.count()
    for i, rdi in enumerate(rdis):
        if i % 100 == 0:
            logger.info(f"Handling {i} - {i + 99}/{rdis_count} RDIs")
        rdi_households = (
            rdi.households(manager="original_and_repr_objects")
            .filter(is_original=True, withdrawn=False)
            .exclude(copied_to__program=program)
        )
        if hhs_to_ignore:
            rdi_households = rdi_households.exclude(id__in=hhs_to_ignore)
        rdi_households_ids = list(rdi_households.values_list("id", flat=True))
        households_count = len(rdi_households_ids)
        for batch_start in range(0, households_count, BATCH_SIZE_SMALL):
            batch_end = batch_start + BATCH_SIZE_SMALL
            logger.info(f"Copying {batch_start} - {batch_end}/{households_count} households for RDI")
            household_dict = {}
            batched_household_ids = rdi_households_ids[batch_start:batch_end]
            batched_households = Household.original_and_repr_objects.filter(id__in=batched_household_ids)
            with transaction.atomic():
                individuals_per_household_dict = defaultdict(list)
                for individual in Individual.original_and_repr_objects.filter(household__in=batched_households):
                    individuals_per_household_dict[individual.household_id].append(individual)
                for household in batched_households:
                    household_original_id = household.pk
                    household_representation = copy_household_representation_for_programs_fast(
                        household,
                        program,
                        individuals_per_household_dict[household_original_id],
                    )
                    household_dict[household_original_id] = household_representation

                copy_roles_from_dict(household_dict, program)  # type: ignore

    rdis.filter(program__isnull=True).update(program=program)


def handle_non_program_objects(
    business_area: BusinessArea,
    hhs_to_ignore: Optional[QuerySet] = None,
    unknown_unassigned_program: Optional[Program] = None,
) -> None:
    households = Household.original_and_repr_objects.filter(
        business_area=business_area, copied_to__isnull=True, is_original=True
    ).order_by("pk")
    if hhs_to_ignore:
        households = households.exclude(id__in=hhs_to_ignore)
    collecting_types_from_charfield = (
        households.values_list("collect_individual_data", flat=True).distinct().order_by("pk")
    )

    for collecting_type in collecting_types_from_charfield:
        program = create_program_with_matching_collecting_type(
            business_area, collecting_type, unknown_unassigned_program
        )
        households_with_collecting_type = households.filter(collect_individual_data=collecting_type)

        # Handle rdis before copying households so households query is not changed yet
        RegistrationDataImport.objects.filter(
            households__in=households_with_collecting_type,
            program__isnull=True,
        ).update(program=program)

        logger.info(f"Handling households with collecting type {collecting_type}")
        households_with_collecting_type_ids = list(households_with_collecting_type.values_list("id", flat=True))
        household_count = len(households_with_collecting_type_ids)
        logger.info(f"Households with collecting type {collecting_type}: {household_count}")
        for batch_start in range(0, household_count, BATCH_SIZE):
            batch_end = batch_start + BATCH_SIZE
            logger.info(
                f"Copying {batch_start} - {batch_end}/{household_count} "
                f"households to program with collect_individual_data {collecting_type}"
            )
            household_dict = {}
            with transaction.atomic():
                individuals_per_household_dict = defaultdict(list)
                households_ids_batch = households_with_collecting_type_ids[batch_start:batch_end]
                batched_households = Household.original_and_repr_objects.filter(id__in=households_ids_batch)
                for individual in Individual.original_and_repr_objects.filter(household_id__in=households_ids_batch):
                    individuals_per_household_dict[individual.household_id].append(individual)
                for household in batched_households:
                    household_original_id = household.pk
                    household_representation = copy_household_fast(
                        household,
                        program,
                        individuals_per_household_dict[household_original_id],
                    )
                    household_dict[household_original_id] = household_representation

                copy_roles_from_dict(household_dict, program)


def create_program_with_matching_collecting_type(
    business_area: BusinessArea,
    collecting_type: DataCollectingType,
    unknown_unassigned_program: Optional[Program] = None,
) -> Program:
    if collecting_type == COLLECT_TYPE_FULL:
        program_collecting_type = DataCollectingType.objects.get(code="full_collection")
    elif collecting_type == COLLECT_TYPE_PARTIAL:
        program_collecting_type = DataCollectingType.objects.get(code="partial_individuals")
    elif collecting_type == COLLECT_TYPE_SIZE_ONLY:
        program_collecting_type = DataCollectingType.objects.get(code="size_only")
    elif collecting_type == COLLECT_TYPE_NONE:
        program_collecting_type = DataCollectingType.objects.get(code="size_age_gender_disaggregated")
    elif collecting_type == COLLECT_TYPE_UNKNOWN:
        if unknown_unassigned_program:
            return unknown_unassigned_program
        program_collecting_type, _ = DataCollectingType.objects.get_or_create(
            code="unknown",
            label="Unknown",
            defaults={"description": "Unknown", "deprecated": True},
        )
    else:  # in case there are some deprecated collecting types
        program_collecting_type = None
    return create_storage_program_for_collecting_type(business_area, program_collecting_type)


def copy_roles_from_dict(household_dict: dict[Any, Household], program: Program) -> None:
    roles = (
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            household__id__in=household_dict.keys(),
            individual__is_removed=False,
            household__is_removed=False,
            is_original=True,
        )
        .exclude(copied_to__household__program=program)
        .order_by("pk")
    )

    roles_to_create = []
    for role in roles:
        household_representation = household_dict[role.household_id]
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=role.individual_id,
        )
        if not individual_representation:
            individual_representation = copy_individual_representation(program=program, individual=role.individual)
        copy = deepcopy(role)
        copy.copied_from_id = role.id
        copy.pk = None
        copy.household = household_representation
        copy.individual = individual_representation
        copy.is_original = False
        roles_to_create.append(copy)

    IndividualRoleInHousehold.original_and_repr_objects.bulk_create(roles_to_create)


def create_storage_program_for_collecting_type(
    business_area: BusinessArea, collecting_type: Optional[DataCollectingType] = None
) -> Program:
    return Program.all_objects.get_or_create(
        name=(f"Storage program - COLLECTION TYPE {collecting_type.label}" if collecting_type else "Storage program"),
        data_collecting_type=collecting_type,
        business_area=business_area,
        defaults={
            "status": Program.DRAFT,
            "start_date": timezone.now(),
            "end_date": timezone.datetime.max,
            "budget": 0,
            "frequency_of_payments": Program.ONE_OFF,
            "sector": Program.CHILD_PROTECTION,
            "scope": Program.SCOPE_FOR_PARTNERS,
            "cash_plus": True,
            "population_goal": 1,
            "is_visible": False,
        },
    )[0]


def apply_congo_withdrawal() -> None:
    logger.info("Applying Congo custom withdrawal rules")
    business_area_congo = BusinessArea.objects.get(name="Democratic Republic of Congo")
    csv_congo_withdraw = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "congo_to_withdraw.csv",
    )
    rdis_names = []
    with open(csv_congo_withdraw, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            rdis_names.append(row[0])
    untargetted_hhs = (
        Household.original_and_repr_objects.filter(
            is_original=True,
            selections__isnull=True,
            registration_data_import__name__in=rdis_names,
            registration_data_import__business_area=business_area_congo,
        )
        .only("id")
        .distinct()
    )
    Household.original_and_repr_objects.filter(copied_from__id__in=untargetted_hhs).update(withdrawn=True)


def get_ignored_hhs() -> QuerySet:
    business_area_afg = BusinessArea.objects.get(name="Afghanistan")
    csv_afg_ignore = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "afg_to_ignore.csv",
    )
    rdis_names = []
    with open(csv_afg_ignore, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            rdis_names.append(row[0])

    return Household.original_and_repr_objects.filter(
        is_original=True,
        selections__isnull=True,
        registration_data_import__name__in=rdis_names,
        registration_data_import__business_area=business_area_afg,
    ).values_list("id", flat=True)


def get_unknown_unassigned_dict() -> Dict:
    unknown_unassigned_dict = {}
    unknown_unassigned_program = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "unknown_unassigned_program.csv",
    )
    with open(unknown_unassigned_program, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        next(reader)  # skip header
        for row in reader:
            business_area = BusinessArea.objects.get(name=row[0])
            program = Program.objects.filter(name=row[1], business_area=business_area).first()
            if program:
                unknown_unassigned_dict[business_area] = program
    return unknown_unassigned_dict


def copy_individual_sync(individuals_ids: List) -> None:
    individuals_to_create = []
    documents_to_create = []
    identities_to_create = []
    bank_account_info_to_create = []
    for individual in (
        Individual.original_and_repr_objects.filter(id__in=individuals_ids)
        .select_related("household")
        .iterator(chunk_size=10000)
    ):
        programs = (
            individual.represented_households(manager="original_and_repr_objects")
            .all()
            .values_list("program", flat=True)
        )
        if individual.household:
            programs = chain(
                individual.household.copied_to(manager="original_and_repr_objects")
                .all()
                .values_list("program", flat=True),
                programs,
            )
        household = individual.household
        for program_id in programs:
            (
                individual_to_create,
                documents_to_create_batch,
                identities_to_create_batch,
                bank_account_info_to_create_batch,
            ) = copy_individual_fast(individual, program_id)
            if household:
                household_representation = (
                    household.copied_to(manager="original_and_repr_objects").filter(program_id=program_id).first()
                )
                individual_to_create.household = household_representation
            documents_to_create.extend(documents_to_create_batch)
            identities_to_create.extend(identities_to_create_batch)
            bank_account_info_to_create.extend(bank_account_info_to_create_batch)
            individuals_to_create.append(individual_to_create)

    Individual.objects.bulk_create(individuals_to_create)
    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(identities_to_create)
    BankAccountInfo.objects.bulk_create(bank_account_info_to_create)


def copy_roles_sync(roles_ids: List) -> None:
    roles_to_create = []
    for role in IndividualRoleInHousehold.original_and_repr_objects.filter(id__in=roles_ids):
        programs = role.household.copied_to(manager="original_and_repr_objects").values_list("program", flat=True)
        for program in programs:
            household_representation = role.household.copied_to
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program=program,
                old_individual_id=role.individual_id,
            )
            if not individual_representation:
                individual_representation = copy_individual(individual=role.individual, program=program)

            copy = deepcopy(role)
            copy.copied_from_id = role.id
            copy.pk = None
            copy.household = household_representation
            copy.individual = individual_representation
            copy.is_original = False
            roles_to_create.append(copy)

    IndividualRoleInHousehold.original_and_repr_objects.bulk_create(roles_to_create)
