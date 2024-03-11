import re
from typing import Dict, List, Sequence, Union

from django.db import transaction
from django.db.models import QuerySet

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.program.validators import validate_data_collecting_type
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index


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

    validate_data_collecting_type(program.business_area, program.data_collecting_type, data_collecting_type)

    program_data["data_collecting_type_id"] = data_collecting_type.id

    for field_name, value in program_data.items():
        setattr(program, field_name, value)

    program.save()
    program.admin_areas.set(admin_areas)
    program.refresh_from_db()
    return program


def copy_program_related_data(copy_from_program_id: str, new_program: Program) -> None:
    with transaction.atomic():
        copy_individuals_from_whole_program(copy_from_program_id, new_program)
        copy_households_from_whole_program(copy_from_program_id, new_program)
        copy_household_related_data(new_program)
        copy_individual_related_data(new_program)
        populate_index(
            Individual.objects.filter(program=new_program),
            get_individual_doc(new_program.business_area.slug),
        )
        populate_index(Household.objects.filter(program=new_program), HouseholdDocument)

        create_program_cycle(new_program)


def create_program_cycle(program: Program) -> None:
    ProgramCycle.objects.create(
        program=program,
        start_date=program.start_date,
        end_date=program.end_date,
        status=ProgramCycle.ACTIVE,
    )


def copy_individuals_from_whole_program(copy_from_program_id: str, program: Program) -> None:
    individuals_to_create = []
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
        individual.registration_data_import = None
        individuals_to_create.append(individual)
    Individual.objects.bulk_create(individuals_to_create)


def copy_households_from_whole_program(copy_from_program_id: str, program: Program) -> None:
    households_to_create = []
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
        household.registration_data_import = None
        household.head_of_household = Individual.objects.get(
            program=program,
            copied_from=household.head_of_household,
        )
        households_to_create.append(household)
    Household.objects.bulk_create(households_to_create)


def copy_household_related_data(program: Program) -> None:
    roles_to_create = []
    entitlement_cards_to_create = []
    new_households = Household.objects.filter(program=program).select_related("copied_from")
    for new_household in new_households:
        roles_to_create.extend(copy_roles_per_household(new_household, program))
        entitlement_cards_to_create.extend(copy_entitlement_cards_per_household(new_household))
    IndividualRoleInHousehold.objects.bulk_create(roles_to_create)
    EntitlementCard.objects.bulk_create(entitlement_cards_to_create)


def copy_roles_per_household(new_household: Household, program: Program) -> List[IndividualRoleInHousehold]:
    roles_in_household = []
    copied_from_roles = IndividualRoleInHousehold.objects.filter(household=new_household.copied_from)
    for role in copied_from_roles:
        role.pk = None
        role.household = new_household
        role.individual = Individual.objects.get(
            program=program,
            copied_from=role.individual,
        )
        roles_in_household.append(role)
    return roles_in_household


def copy_entitlement_cards_per_household(new_household: Household) -> List[EntitlementCard]:
    entitlement_cards_in_household = []
    old_entitlement_cards = new_household.copied_from.entitlement_cards.all()
    for entitlement_card in old_entitlement_cards:
        entitlement_card.pk = None
        entitlement_card.household = new_household
        entitlement_cards_in_household.append(entitlement_card)
    return entitlement_cards_in_household


def copy_individual_related_data(program: Program) -> None:
    individuals_to_update = []
    documents_to_create = []
    individual_identities_to_create = []
    bank_account_infos_to_create = []
    new_individuals = Individual.objects.filter(program=program)
    for new_individual in new_individuals:
        individuals_to_update.append(set_household_per_individual(new_individual, program))
        documents_to_create.extend(
            copy_document_per_individual(
                list(new_individual.copied_from.documents.all()),
                new_individual,
            )
        )
        individual_identities_to_create.extend(
            copy_individual_identity_per_individual(
                list(new_individual.copied_from.identities.all()),
                new_individual,
            )
        )
        bank_account_infos_to_create.extend(
            copy_bank_account_info_per_individual(
                list(new_individual.copied_from.bank_account_info.all()),
                new_individual,
            )
        )
    Individual.objects.bulk_update(individuals_to_update, ["household"])
    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(individual_identities_to_create)
    BankAccountInfo.objects.bulk_create(bank_account_infos_to_create)


def set_household_per_individual(new_individual: Individual, program: Program) -> Individual:
    new_individual.household = Household.objects.filter(
        program=program,
        copied_from_id=new_individual.household_id,
    ).first()
    return new_individual


def create_roles_for_new_representation(new_household: Household, program: Program) -> None:
    old_roles = IndividualRoleInHousehold.objects.filter(
        household=new_household.copied_from,
    )
    individuals_to_create = []
    documents_to_create = []
    identities_to_create = []
    bank_account_info_to_create = []
    roles_to_create = []
    for role in old_roles:
        individual_representation = Individual.objects.filter(
            program=program,
            unicef_id=role.individual.unicef_id,
        ).first()
        if not individual_representation:
            (
                individual_representation,
                documents_to_create_batch,
                identities_to_create_batch,
                bank_account_info_to_create_batch,
            ) = copy_individual(role.individual, program)

            individuals_to_create.append(individual_representation)
            documents_to_create.extend(documents_to_create_batch)
            identities_to_create.extend(identities_to_create_batch)
            bank_account_info_to_create.extend(bank_account_info_to_create_batch)

        role.pk = None
        role.household = new_household
        role.individual = individual_representation
        roles_to_create.append(role)

    Individual.objects.bulk_create(individuals_to_create)
    Document.objects.bulk_create(documents_to_create)
    IndividualIdentity.objects.bulk_create(identities_to_create)
    BankAccountInfo.objects.bulk_create(bank_account_info_to_create)
    IndividualRoleInHousehold.objects.bulk_create(roles_to_create)


def enroll_households_to_program(households: QuerySet, program: Program) -> None:
    households_to_exclude = Household.objects.filter(
        program=program,
        unicef_id__in=households.values_list("unicef_id", flat=True),
    ).values_list("unicef_id", flat=True)
    households = households.exclude(unicef_id__in=households_to_exclude).prefetch_related("entitlement_cards")
    error_messages = []
    for household in households:
        try:
            with transaction.atomic():
                if not household.household_collection:
                    household.household_collection = HouseholdCollection.objects.create()
                    household.save()

                individuals = household.individuals.prefetch_related("documents", "identities", "bank_account_info")
                individuals_to_exclude_dict = {
                    str(x["unicef_id"]): str(x["pk"])
                    for x in Individual.objects.filter(
                        program=program,
                        unicef_id__in=individuals.values_list("unicef_id", flat=True),
                    ).values("unicef_id", "pk")
                }

                documents_to_create = []
                identities_to_create = []
                bank_account_info_to_create = []
                individuals_to_create = []
                external_collectors_id_to_update = []

                for individual in individuals:
                    if str(individual.unicef_id) in individuals_to_exclude_dict:
                        external_collectors_id_to_update.append(individuals_to_exclude_dict[str(individual.unicef_id)])
                        continue
                    (
                        individual_to_create,
                        documents_to_create_batch,
                        identities_to_create_batch,
                        bank_account_info_to_create_batch,
                    ) = copy_individual(individual, program)
                    documents_to_create.extend(documents_to_create_batch)
                    identities_to_create.extend(identities_to_create_batch)
                    bank_account_info_to_create.extend(bank_account_info_to_create_batch)
                    individuals_to_create.append(individual_to_create)

                individuals_dict = {i.unicef_id: i for i in individuals_to_create}
                Individual.objects.bulk_create(individuals_to_create)
                Document.objects.bulk_create(documents_to_create)
                IndividualIdentity.objects.bulk_create(identities_to_create)
                BankAccountInfo.objects.bulk_create(bank_account_info_to_create)

                original_household_id = household.id
                original_head_of_household_unicef_id = household.head_of_household.unicef_id
                household.copied_from_id = original_household_id
                household.pk = None
                household.program = program
                household.is_original = False
                household.registration_data_import = None
                household.total_cash_received = None
                household.total_cash_received_usd = None

                if original_head_of_household_unicef_id in individuals_dict:
                    household.head_of_household = individuals_dict[original_head_of_household_unicef_id]
                else:
                    copied_individual_id = individuals_to_exclude_dict[str(original_head_of_household_unicef_id)]
                    household.head_of_household_id = copied_individual_id

                household.save()
                entitlement_cards = copy_entitlement_cards_per_household(household)
                EntitlementCard.objects.bulk_create(entitlement_cards)

                ids_to_update = [x.pk for x in individuals_to_create] + external_collectors_id_to_update
                Individual.objects.filter(id__in=ids_to_update).update(household=household)

                create_roles_for_new_representation(household, program)
        except Exception as e:
            error_message = str(e)
            if "unique_if_not_removed_and_valid_for_representations" in error_message:
                if document_data := re.search(r"\((.*?)\)=\((.*?)\)", error_message):
                    keys = document_data.group(1).split(", ")
                    values = document_data.group(2).split(", ")
                    document_dict = dict(zip(keys, values))
                    error_message = f"Document already exists: {document_dict.get('document_number')}"
            error_messages.append(f"{household.unicef_id}: {error_message}")
    if error_messages:
        raise Exception("Following households failed to be enrolled: \n" + "\n".join(error_messages))


def copy_individual(individual: Individual, program: Program) -> tuple:
    documents = list(individual.documents.all())
    identities = list(individual.identities.all())
    bank_accounts_info = list(individual.bank_account_info.all())
    if not individual.individual_collection:
        individual.individual_collection = IndividualCollection.objects.create()
        individual.save()

    original_individual_id = individual.id
    individual.copied_from_id = original_individual_id
    individual.pk = None
    individual.program = program
    individual.household = None
    individual.registration_data_import = None

    documents_to_create = copy_document_per_individual(documents, individual)
    identities_to_create = copy_individual_identity_per_individual(identities, individual)
    bank_account_info_to_create = copy_bank_account_info_per_individual(bank_accounts_info, individual)
    return individual, documents_to_create, identities_to_create, bank_account_info_to_create


def copy_document_per_individual(documents: List[Document], individual_representation: Individual) -> List[Document]:
    """
    Clone document for individual if new individual_representation has been created.
    """
    documents_list = []
    for document in documents:
        original_document_id = document.id
        document.copied_from_id = original_document_id
        document.pk = None
        document.individual = individual_representation
        document.program_id = individual_representation.program_id
        documents_list.append(document)
    return documents_list


def copy_individual_identity_per_individual(
    identities: List[IndividualIdentity], individual_representation: Individual
) -> List[IndividualIdentity]:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    identities_list = []
    for identity in identities:
        original_identity_id = identity.id
        identity.copied_from_id = original_identity_id
        identity.pk = None
        identity.individual = individual_representation
        identities_list.append(identity)
    return identities_list


def copy_bank_account_info_per_individual(
    bank_accounts_info: List[BankAccountInfo], individual_representation: Individual
) -> List[BankAccountInfo]:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    bank_accounts_info_list = []
    for bank_account_info in bank_accounts_info:
        original_bank_account_info_id = bank_account_info.id
        bank_account_info.copied_from_id = original_bank_account_info_id
        bank_account_info.pk = None
        bank_account_info.individual = individual_representation
        bank_accounts_info_list.append(bank_account_info)
    return bank_accounts_info_list


def update_partner_permissions_for_program(partner_data: Dict, business_area_pk: str, program_pk: str) -> None:
    admin_areas = [area_id for area_id in partner_data.get("admin_areas", [])]
    partner = Partner.objects.get(id=partner_data["id"])
    partner_perms = partner.get_permissions()
    partner_perms.set_program_areas(business_area_pk, program_pk, admin_areas)
    partner.set_permissions(partner_perms)
    partner.save()


def remove_program_permissions_for_exists_partners(
    partner_exclude_ids: Sequence[Union[str, int]], business_area_pk: str, program_pk: str
) -> None:
    for partner in Partner.objects.exclude(id__in=partner_exclude_ids):
        partner.get_permissions().remove_program_areas(business_area_pk, program_pk)
        partner.save()
