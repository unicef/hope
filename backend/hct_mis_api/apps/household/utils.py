from typing import Optional

from django.db.models import Count, Q, QuerySet

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

BATCH_SIZE = 500


def migrate_data_to_representations(business_area: BusinessArea) -> None:
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

        household_selections = HouseholdSelection.objects.filter(target_population_id__in=target_populations_ids)
        household_ids = household_selections.distinct("household").values_list("household_id", flat=True)

        households = Household.objects.filter(id__in=household_ids)

        for household in households:
            copy_household_representation(household, program)

        handle_rdis(households, program)

        copy_roles(households, program=program)

        adjust_household_selections(household_selections, program)

    assign_non_program_objects_to_biggest_program(business_area)

    adjust_payments(business_area)
    adjust_payment_records(business_area)


def get_household_representation_per_program_by_old_household_id(
    program: Program,
    old_household_id: str,
) -> Optional[Household]:
    return Household.objects.filter(
        program=program,
        copied_from_id=old_household_id,
    ).first()


def get_individual_representation_per_program_by_old_individual_id(
    program: Program,
    old_individual_id: str,
) -> Optional[Individual]:
    return Individual.objects.filter(
        program=program,
        copied_from_id=old_individual_id,
    ).first()


def copy_household_representation(household: Household, program: Program) -> Optional[Household]:
    """
    Copy household into representation for given program.
    If representation in this program already exists, return it, so that it is not copied again.
    For the first representation, adjust household and all related objects to it, instead of copying.
    """
    household.refresh_from_db()
    if household.copied_from and not household.copied_to.exists():
        # this is already household representation, not original household
        return household
    # check if household already has any representation
    if household.copied_to.exists():
        # if representation of this household already exists in this program, return it
        if Household.objects.filter(
            program=program,
            copied_from=household.copied_from,
        ).exists():
            household_representation = get_household_representation_per_program_by_old_household_id(
                program.pk,
                household.copied_from.pk,
            )
        else:
            household_representation = copy_household(household, program)
    else:
        # for the first representation, adjust household and all related objects to it,
        # instead of copying and assign "copied_to"
        household_representation = adjust_household_to_representation(household, program)

    household_representation.refresh_from_db()
    return household_representation


def copy_household(household: Household, program: Program) -> Household:
    original_household_id = household.id
    household.copied_from_id = household.id
    household.origin_unicef_id = household.unicef_id
    household.pk = None
    household.unicef_id = None
    household.program = program

    original_household = Household.objects.get(pk=original_household_id)

    individuals = []
    for individual in original_household.individuals.all():
        individuals.append(copy_individual_representation(program, individual))

    head_of_household = get_individual_representation_per_program_by_old_individual_id(
        program=program,
        old_individual_id=original_household.head_of_household.pk,
    )
    if head_of_household:
        household.head_of_household = head_of_household
    else:
        household.head_of_household = copy_individual_representation(program, original_household.head_of_household)

    household.save()
    for individual in individuals:
        individual.household = household

    Individual.objects.bulk_update(individuals, ["household"])

    copy_entitlement_card_per_household(household=original_household, household_representation=household)

    return household


def adjust_household_to_representation(household: Household, program: Program) -> Household:
    """
    Use this function when household has no representations yet - original object is used as first representation
    for optimization purposes. Corresponding representations of individuals need to be adjusted as well.
    """
    household.program = program
    # assign original household as copied_from
    # in this case the same household, so we know it is already a representation
    household.copied_from_id = household.id
    household.origin_unicef_id = household.unicef_id

    for individual in household.individuals.all():
        copy_individual_representation(program, individual, household)
    head_of_household = get_individual_representation_per_program_by_old_individual_id(
        program=program,
        old_individual_id=household.head_of_household.pk,
    )
    if head_of_household:
        household.head_of_household_id = head_of_household.id
    else:
        copy_individual_representation(program, household.head_of_household, household)

    household.save()

    return household


def copy_individual_representation(
    program: Program,
    individual: Individual,
    household_representation: Optional[Household] = None,
) -> Optional[Individual]:
    # ignore if this is already individual representation - we want to copy only original individual
    if individual.copied_from and not individual.copied_to.exists():
        return individual

    # check if this is not the first representation of this individual
    if individual.copied_to.exists():
        # if representation of this individual already exists in this program, return it
        if Individual.objects.filter(
            program=program,
            copied_from=individual,
        ).exists():
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program.pk,
                individual.pk,
            )
        else:
            individual_representation = copy_individual(individual, program, household_representation)
    else:
        individual_representation = adjust_individual_to_representation(individual, program, household_representation)

    return individual_representation


def copy_individual(
    individual: Individual, program: Program, household_representation: Optional[Household] = None
) -> Individual:
    copied_from_id = individual.id
    individual.copied_from_id = copied_from_id
    individual.origin_unicef_id = individual.unicef_id
    individual.pk = None
    individual.unicef_id = None  # type: ignore
    individual.program = program
    individual.household = household_representation
    individual.save()
    individual.refresh_from_db()

    original_individual = Individual.objects.get(pk=copied_from_id)

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
    return individual


def copy_roles(households: QuerySet, program: Program) -> None:
    # filter roles for original households (exclude roles in household representations as we don't want to copy them)
    roles = IndividualRoleInHousehold.objects.filter(
        household__in=households,
        individual__is_removed=False,
        household__is_removed=False,
    ).exclude(Q(household__copied_to=None) & Q(household__copied_from__isnull=False))

    roles_count = roles.count()
    for batch_start in range(0, roles_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        roles_list = []
        for role in roles[batch_start:batch_end]:
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
            # check if representation existing in this program is not an original
            # if it is, we don't need to copy the role
            if household_representation != role.household or individual_representation != role.individual:
                # wider query inside to limit number of queries - the condition above will pass only for non-originals
                # check if there already is a role for this individual representation in this household representation
                if IndividualRoleInHousehold.objects.filter(
                    household=household_representation,
                    individual=individual_representation,
                ).exists():
                    continue
                role.pk = None
                role.household = household_representation
                role.individual = individual_representation
                roles_list.append(role)

        IndividualRoleInHousehold.objects.bulk_create(roles_list)


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
    if household != household_representation:
        entitlement_cards = household.entitlement_cards.all()
        entitlement_cards_list = []
        for entitlement_card in entitlement_cards:
            entitlement_card.pk = None
            entitlement_card.household = household_representation
            entitlement_cards_list.append(entitlement_card)
        EntitlementCard.objects.bulk_create(entitlement_cards_list)


def copy_document_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone document for individual if new individual_representation has been created.
    """
    if individual != individual_representation:
        documents = individual.documents.all()
        documents_list = []
        for document in documents:
            document.pk = None
            document.individual = individual_representation
            document.program = individual_representation.program
            documents_list.append(document)
        Document.objects.bulk_create(documents_list)


def copy_individual_identity_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    if individual != individual_representation:
        identities = individual.identities.all()
        identities_list = []
        for identity in identities:
            identity.pk = None
            identity.individual = individual_representation
            identities_list.append(identity)
        IndividualIdentity.objects.bulk_create(identities_list)


def copy_bank_account_info_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    if individual != individual_representation:
        bank_accounts_info = individual.bank_account_info.all()
        bank_accounts_info_list = []
        for bank_account_info in bank_accounts_info:
            bank_account_info.pk = None
            bank_account_info.individual = individual_representation
            bank_accounts_info_list.append(bank_account_info)
        BankAccountInfo.objects.bulk_create(bank_accounts_info_list)


def adjust_household_selections(household_selections: QuerySet, program: Program) -> None:
    """
    Adjust HouseholdSelections to new households representations. By this TargetPopulations are adjusted.
    Because TargetPopulation is per program, HouseholdSelections are per program. It requires only to change
    household in this relation to corresponding representation for this program.
    """
    household_selections_count = household_selections.count()
    for batch_start in range(0, household_selections_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        household_selection_updates = []

        for household_selection in household_selections[batch_start:batch_end]:
            household_representation = get_household_representation_per_program_by_old_household_id(
                program.pk, household_selection.household_id
            )

            if household_representation and household_representation != household_selection.household:
                household_selection_updates.append(
                    HouseholdSelection(
                        id=household_selection.id,
                        household=household_representation,
                    )
                )
        HouseholdSelection.objects.bulk_update(household_selection_updates, ["household_id"])


def adjust_payments(business_area: BusinessArea) -> None:
    """
    Adjust payment individuals and households to their representations.
    Payment is already related to program through PaymentPlan (parent), and then TargetPopulation.
    """

    payments = Payment.objects.filter(parent__target_population__program__business_area=business_area)
    payments_count = payments.count()

    for batch_start in range(0, payments_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
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


def adjust_payment_records(business_area: BusinessArea) -> None:
    """
    Adjust PaymentRecord individuals and households to their representations.
    PaymentRecord is already related to program through TargetPopulation.
    """
    payment_records = PaymentRecord.objects.filter(target_population__program__business_area=business_area)
    payment_records_count = payment_records.count()
    for batch_start in range(0, payment_records_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
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


def handle_rdis(households: QuerySet, program: Program) -> None:
    rdi_ids = households.values_list("registration_data_import_id", flat=True).distinct()
    rdis = RegistrationDataImport.objects.filter(id__in=rdi_ids)
    for rdi in rdis:
        rdi_households = rdi.households.exclude(Q(copied_to=None) & Q(copied_from__isnull=False))
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
        .first()
    )


def assign_non_program_objects_to_biggest_program(business_area: BusinessArea) -> None:
    biggest_program = get_biggest_program(business_area)
    if not biggest_program:
        return
    update_non_program_individuals_program(biggest_program, business_area)
    update_non_program_households_program(biggest_program, business_area)
    update_non_program_document_program(biggest_program, business_area)
    rdis = RegistrationDataImport.objects.filter(programs=None, business_area=business_area)
    rdi_through = RegistrationDataImport.programs.through
    rdi_through.objects.bulk_create(
        [rdi_through(registrationdataimport_id=rdi.id, program_id=biggest_program.id) for rdi in rdis]
    )


def update_non_program_households_program(program: Program, business_area: BusinessArea) -> None:
    households = Household.objects.filter(program__isnull=True, business_area=business_area)
    households_count = households.count()

    for batch_start in range(0, households_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        households_updates = []

        for household in households[batch_start:batch_end]:
            households_updates.append(
                Household(
                    id=household.id,
                    program=program,
                    copied_from_id=household.id,
                    origin_unicef_id=household.unicef_id,
                )
            )

        Household.objects.bulk_update(households_updates, ["program", "copied_from", "origin_unicef_id"])


def update_non_program_individuals_program(program: Program, business_area: BusinessArea) -> None:
    individuals = Individual.objects.filter(program__isnull=True, business_area=business_area)
    individuals_count = individuals.count()
    for batch_start in range(0, individuals_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        individuals_updates = []

        for individual in individuals[batch_start:batch_end]:
            individuals_updates.append(
                Individual(
                    id=individual.id,
                    program=program,
                    copied_from_id=individual.id,
                    origin_unicef_id=individual.unicef_id,
                )
            )
        Individual.objects.bulk_update(individuals_updates, ["program", "copied_from", "origin_unicef_id"])


def update_non_program_document_program(program: Program, business_area: BusinessArea) -> None:
    documents = Document.objects.filter(program__isnull=True, individual__business_area=business_area)
    documents_count = documents.count()
    for batch_start in range(0, documents_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        documents_updates = []

        for document in documents[batch_start:batch_end]:
            documents_updates.append(
                Document(
                    id=document.id,
                    program=program,
                )
            )
        Document.objects.bulk_update(documents_updates, ["program"])
