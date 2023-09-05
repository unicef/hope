import logging
from collections import defaultdict
from typing import Optional, Dict, List

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, QuerySet

from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


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
    - copy all objects related to old households/individuals or adjust existing ones if they are related to program
    - handle RDI: if there is RDI for household copy all households in this RDI to current program
    For whole business_area:
    - for rdi that was not related to program: add rdi and copy its households to the biggest program in that ba
    - adjust payments and payment_records to corresponding representations

    """
    for program in Program.objects.filter(
        business_area=business_area, status__in=[Program.ACTIVE, Program.FINISHED]
    ).order_by("status"):
        logger.info("----- NEW PROGRAM -----")
        logger.info(f"Creating representations for program: {program}")
        if program.status == Program.ACTIVE:
            target_populations_ids = TargetPopulation.objects.filter(
                program=program,
            ).values_list("id", flat=True)
        elif program.status == Program.FINISHED:
            target_populations_ids = TargetPopulation.objects.filter(
                Q(
                    status__in=[
                        TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
                        TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                    ]
                )
                & Q(program=program)
            ).values_list("id", flat=True)
            delete_target_populations_in_wrong_statuses(program=program)

        household_selections = HouseholdSelection.objects.filter(
            target_population_id__in=target_populations_ids, is_original=True, is_migration_handled=False
        )
        household_ids = household_selections.distinct("household").values_list("household_id", flat=True)

        households = Household.objects.filter(id__in=household_ids, is_migration_handled=False, is_original=True)
        already_copied_households = list(
            Household.objects.filter(is_original=False, program=program, copied_from__in=households).values_list(
                "id", flat=True
            )
        )
        logger.info(f"Already copied households: {len(already_copied_households)}")
        households = households.exclude(id__in=already_copied_households)
        households_count = households.count()
        logger.info(f"Households to handle: {households_count}")
        household_ids = list(households.values_list("id", flat=True))
        logger.info(f"Handling households for program: {program}")
        full_households = (
            Household.objects.filter(id__in=household_ids)
            .select_related()
            .prefetch_related("individuals")
            .order_by("id")
        )
        paginator = Paginator(full_households, BATCH_SIZE)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            logger.info(f"Handling households {page.start_index()} - {page.end_index()}/{households_count}")
            batched_households = page.object_list
            individuals_per_household =get_all_individuals_per_household_batch(batched_households, program)
            for household in batched_households:
                with transaction.atomic():
                    copy_household_representation(household, program, individuals_per_household[str(household.id)])

        logger.info(f"Handling RDIs for program: {program}")
        handle_rdis(households, program)

        logger.info(f"Copying roles for program: {program}")
        copy_roles(households, program=program)

        logger.info(f"Copy household selections for program: {program}")
        copy_household_selections(household_selections, program)

        logger.info(f"Finished creating representations for program: {program}")

    Household.objects.filter(business_area=business_area, copied_to__isnull=False, is_original=True).update(
        is_migration_handled=True
    )
    logger.info("Handling objects without any representations yet - enrolling to biggest program")
    assign_non_program_objects_to_biggest_program(business_area)

    # logger.info("Adjusting payments and payment records")
    # adjust_payments(business_area)
    # adjust_payment_records(business_area)


def get_all_individuals_per_household_batch(batched_households, program) -> Dict[str, List[Individual]]:
    """
    returns dict with household_id as key and list of individuals as value
    excluding individuals that were already copied to current program
    better to use this function than get individuals per household in loop
    """
    all_individuals = Individual.objects.filter(household__in=batched_households)
    all_individuals_ids = list(all_individuals.values_list("id", flat=True))
    all_individuals_to_exclude = all_individuals.filter(
        is_original=False, program=program, copied_from__in=all_individuals_ids
    )
    all_individuals_to_copy = all_individuals.exclude(id__in=all_individuals_to_exclude)
    individuals_per_household = defaultdict(list)
    for individual in all_individuals_to_copy:
        individuals_per_household[str(individual.household_id)].append(individual)
    return individuals_per_household


def get_household_representation_per_program_by_old_household_id(
    program: Program,
    old_household_id: str,
) -> Optional[Household]:
    return Household.objects.filter(
        program=program,
        copied_from_id=old_household_id,
        is_original=False,
    ).first()


def get_individual_representation_per_program_by_old_individual_id(
    program: Program,
    old_individual_id: str,
) -> Optional[Individual]:
    return Individual.objects.filter(
        program=program,
        copied_from_id=old_individual_id,
        is_original=False,
    ).first()


def copy_household_representation(household: Household, program: Program, individuals: List[Individual]) -> None:
    """
    Copy household into representation for given program if it does not exist yet.
    """
    # copy representations only based on original households
    if not household.is_original:
        return
    copy_household(household, program, individuals)


def copy_household(household: Household, program: Program, individuals: List[Individual]) -> Household:
    original_household_id = household.id
    original_head_of_household_id = household.head_of_household_id
    original_individuals = individuals
    household.copied_from_id = original_household_id
    household.origin_unicef_id = household.unicef_id
    household.pk = None
    household.unicef_id = None
    household.program = program
    household.is_original = False
    new_individuals = []
    for individual in original_individuals:
        copied_individual = copy_individual(individual, program)
        new_individuals.append(copied_individual)
        if str(individual.id) == str(original_head_of_household_id):
            household.head_of_household = copied_individual
    household.save()
    for individual in new_individuals:
        individual.household = household

    Individual.objects.bulk_update(new_individuals, ["household"])
    return household


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
            old_individual_id=individual.copied_from.pk,
        )


def copy_individual(individual: Individual, program: Program) -> Individual:
    original_individual_id = individual.id
    individual.copied_from_id = original_individual_id
    individual.origin_unicef_id = individual.unicef_id
    individual.pk = None
    individual.unicef_id = None  # type: ignore
    individual.program = program
    individual.household = None
    individual.is_original = False
    individual.save()
    individual.refresh_from_db()

    original_individual = Individual.objects.get(pk=original_individual_id)

    copy_document_per_individual(original_individual, individual)
    copy_individual_identity_per_individual(original_individual, individual)
    copy_bank_account_info_per_individual(original_individual, individual)

    return individual


def adjust_individual_to_representation(
    individual: Individual,
    program: Program,
    household_representation: Optional[Household] = None,
) -> Individual:
    """
    Use this function when individual has no representations yet - original object is used as 1st representation
    for optimization purposes.
    """
    individual.program = program
    individual.copied_from_id = individual.id
    individual.origin_unicef_id = individual.unicef_id
    individual.household = household_representation
    individual.save()
    individual.documents.update(program=individual.program)
    return individual


def copy_roles(households: QuerySet, program: Program) -> None:
    # filter only original roles
    roles = (
        IndividualRoleInHousehold.objects.filter(
            household__in=households,
            individual__is_removed=False,
            household__is_removed=False,
            is_original=True,
        )
        .exclude(copied_to__household__program=program)
        .order_by("pk")
    )

    roles_count = roles.count()
    for batch_start in range(0, roles_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{roles_count} roles")
        roles_list = []
        for role in roles[0:BATCH_SIZE]:
            household_representation = get_household_representation_per_program_by_old_household_id(
                program=program,
                old_household_id=role.household_id,
            )
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program=program,
                old_individual_id=role.individual_id,
            )
            if not individual_representation:
                individual_representation = copy_individual_representation(program=program, individual=role.individual)

            original_role_id = role.id
            role.copied_from_id = original_role_id
            role.pk = None
            role.household = household_representation
            role.individual = individual_representation
            role.is_original = False
            roles_list.append(role)

        IndividualRoleInHousehold.objects.bulk_create(roles_list)
        del roles_list


def delete_target_populations_in_wrong_statuses(program: Program) -> None:
    TargetPopulation.objects.filter(
        ~Q(
            status__in=[
                TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
                TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            ]
        )
        & Q(program=program)
    ).delete()


def copy_entitlement_card_per_household(household: Household, household_representation: Household) -> None:
    entitlement_cards = household.entitlement_cards.all()
    entitlement_cards_list = []
    for entitlement_card in entitlement_cards:
        original_entitlement_card_id = entitlement_card.id
        entitlement_card.copied_from_id = original_entitlement_card_id
        entitlement_card.pk = None
        entitlement_card.household = household_representation
        entitlement_card.is_original = False
        entitlement_cards_list.append(entitlement_card)
    EntitlementCard.objects.bulk_create(entitlement_cards_list)
    del entitlement_cards_list


def copy_document_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone document for individual if new individual_representation has been created.
    """
    documents = individual.documents.all()
    documents_list = []
    for document in documents:
        original_document_id = document.id
        document.copied_from_id = original_document_id
        document.pk = None
        document.individual = individual_representation
        document.program = individual_representation.program
        document.is_original = False
        documents_list.append(document)
    Document.objects.bulk_create(documents_list)
    del documents_list


def copy_individual_identity_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    identities = individual.identities.all()
    identities_list = []
    for identity in identities:
        original_identity_id = identity.id
        identity.copied_from_id = original_identity_id
        identity.pk = None
        identity.individual = individual_representation
        identity.is_original = False
        identities_list.append(identity)
    IndividualIdentity.objects.bulk_create(identities_list)
    del identities_list


def copy_bank_account_info_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    bank_accounts_info = individual.bank_account_info.all()
    bank_accounts_info_list = []
    for bank_account_info in bank_accounts_info:
        original_bank_account_info_id = bank_account_info.id
        bank_account_info.copied_from_id = original_bank_account_info_id
        bank_account_info.pk = None
        bank_account_info.individual = individual_representation
        bank_account_info.is_original = False
        bank_accounts_info_list.append(bank_account_info)
    BankAccountInfo.objects.bulk_create(bank_accounts_info_list)
    del bank_accounts_info_list


def copy_household_selections(household_selections: QuerySet, program: Program) -> None:
    """
    Adjust HouseholdSelections to new households representations. By this TargetPopulations are adjusted.
    Because TargetPopulation is per program, HouseholdSelections are per program. It requires only to change
    household in this relation to corresponding representation for this program.
    """
    household_selections = household_selections.order_by("id")

    household_selections_to_create = []
    for household_selection in household_selections:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program.pk, household_selection.household_id
        )
        household_selection.pk = None
        household_selection.household = household_representation
        household_selection.is_original = False
        household_selections_to_create.append(household_selection)

    HouseholdSelection.objects.bulk_create(household_selections_to_create)
    household_selections.update(is_migration_handled=True)


def adjust_payments(business_area: BusinessArea) -> None:
    """
    Adjust payment individuals and households to their representations.
    Payment is already related to program through PaymentPlan (parent), and then TargetPopulation.
    """

    payments = Payment.objects.filter(parent__target_population__program__business_area=business_area).order_by("pk")
    payments_count = payments.count()

    for batch_start in range(0, payments_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Adjusting payments {batch_start} - {batch_end}/{payments_count}")
        payment_updates = []

        for payment in payments[batch_start:batch_end]:
            payment_program = payment.parent.target_population.program
            representation_collector = get_individual_representation_per_program_by_old_individual_id(
                program=payment_program,
                old_individual_id=payment.collector.pk,
            )
            if not representation_collector:
                representation_collector = copy_individual_representation(
                    program=payment_program, individual=payment.collector
                )
            # payment.head_of_household can be None
            if payment.head_of_household:
                representation_head_of_household = get_individual_representation_per_program_by_old_individual_id(
                    program=payment_program,
                    old_individual_id=payment.head_of_household.pk,
                )
            else:
                representation_head_of_household = None
            representation_household = get_household_representation_per_program_by_old_household_id(
                program=payment_program,
                old_household_id=payment.household_id,
            )
            payment.refresh_from_db()
            if (
                not (
                    representation_collector == payment.collector
                    and representation_head_of_household == payment.head_of_household
                    and representation_household == payment.household
                )
                and representation_collector
                and representation_household
            ):
                payment.collector = representation_collector
                payment.head_of_household = representation_head_of_household
                payment.household = representation_household
                payment_updates.append(payment)

        Payment.objects.bulk_update(payment_updates, fields=["collector_id", "head_of_household_id", "household_id"])
        del payment_updates


def adjust_payment_records(business_area: BusinessArea) -> None:
    """
    Adjust PaymentRecord individuals and households to their representations.
    PaymentRecord is already related to program through TargetPopulation.
    """
    payment_records = PaymentRecord.objects.filter(target_population__program__business_area=business_area).order_by(
        "pk"
    )
    payment_records_count = payment_records.count()
    for batch_start in range(0, payment_records_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Adjusting payment records {batch_start} - {batch_end}/{payment_records_count}")
        payment_record_updates = []

        for payment_record in payment_records[batch_start:batch_end]:
            payment_record_program = payment_record.target_population.program
            if payment_record.head_of_household:
                representation_head_of_household = get_individual_representation_per_program_by_old_individual_id(
                    program=payment_record_program,
                    old_individual_id=payment_record.head_of_household.pk,
                )
            else:
                representation_head_of_household = None
            representation_household = get_household_representation_per_program_by_old_household_id(
                program=payment_record_program,
                old_household_id=payment_record.household_id,
            )
            payment_record.refresh_from_db()
            if (
                not (
                    representation_head_of_household == payment_record.head_of_household
                    and representation_household == payment_record.household
                )
                and representation_household
            ):
                payment_record.head_of_household = representation_head_of_household
                payment_record.household = representation_household
                payment_record_updates.append(payment_record)

        PaymentRecord.objects.bulk_update(payment_record_updates, fields=["head_of_household_id", "household_id"])
        del payment_record_updates


def handle_rdis(households: QuerySet, program: Program) -> None:
    rdi_ids = households.values_list("registration_data_import_id", flat=True).distinct()
    rdis = RegistrationDataImport.objects.filter(id__in=rdi_ids)
    rdis_count = rdis.count()
    for i, rdi in enumerate(rdis):
        if i % 100 == 0:
            logger.info(f"Handling {i} - {i+99}/{rdis_count} RDIs")
        rdi_households = rdi.households.filter(is_original=True)
        for rdi_household in rdi_households:
            copy_household_representation(rdi_household, program)

        copy_roles(rdi_households, program)

        rdi.programs.add(program)


def get_biggest_program(business_area: BusinessArea) -> Optional[Program]:
    """
    Get the program with most households.
    Household has 2 foreign keys to program, reversed relation for ForeignKey is called household.
    The 2nd (households) will be deleted after this migration, and names adjusted.
    """
    return (
        Program.objects.filter(business_area=business_area, status=Program.ACTIVE)
        .annotate(household_count=Count("household"))
        .order_by("-household_count")
        .only("id")
        .first()
    )


def assign_non_program_objects_to_biggest_program(business_area: BusinessArea) -> None:
    biggest_program = get_biggest_program(business_area)
    if not biggest_program:
        return
    copy_individuals_to_biggest_program(biggest_program, business_area)
    copy_households_to_biggest_program(biggest_program, business_area)
    rdis = RegistrationDataImport.objects.filter(programs=None, business_area=business_area).only("id")
    rdi_through = RegistrationDataImport.programs.through
    rdi_through.objects.bulk_create(
        [rdi_through(registrationdataimport_id=rdi.id, program_id=biggest_program.id) for rdi in rdis]
    )


def copy_households_to_biggest_program(program: Program, business_area: BusinessArea) -> None:
    households = Household.objects.filter(business_area=business_area, copied_to__isnull=True, is_original=True)
    for household in households:
        copy_household(household, program)
    copy_roles(households, program=program)


def copy_individuals_to_biggest_program(program: Program, business_area: BusinessArea) -> None:
    individuals = Individual.objects.filter(
        business_area=business_area,
        is_original=True,
        copied_to__isnull=True,
    )
    for individual in individuals:
        copy_individual(individual, program)
