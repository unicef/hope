import re
from random import randint
from typing import Dict, List, Optional

from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.core.models import DataCollectingType, FlexibleAttribute
from hct_mis_api.apps.geo.models import Area
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
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.models import Program, ProgramCycle, ProgramPartnerThrough
from hct_mis_api.apps.program.validators import validate_data_collecting_type
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index
from hct_mis_api.apps.utils.models import MergeStatusModel


def copy_program_object(copy_from_program_id: str, program_data: dict, user: User) -> Program:
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

    program.full_clean()
    program.save()
    program.admin_areas.set(admin_areas)
    program.refresh_from_db()

    # create default cycle
    ProgramCycle.objects.create(
        program_id=program.id,
        start_date=program.start_date,
        end_date=None,
        created_by=user,
    )
    return program


class CopyProgramPopulation:
    def __init__(
        self,
        copy_from_individuals: QuerySet[Individual],
        copy_from_households: QuerySet[Household],
        program: Program,
        rdi: RegistrationDataImport,
        rdi_merge_status: str = MergeStatusModel.MERGED,
        create_collection: bool = True,
    ):
        """
        copy_from_individuals: QuerySet of Individuals to copy
        copy_from_households: QuerySet of Households to copy
        program: Program to which the data will be copied
        rdi_merge_status: rdi_merge_status for new objects
        create_collection: if True, new common collection will be created for original and copied object
        rdi: RegistrationDataImport object to which new objects will be assigned
        """
        self.copy_from_individuals = copy_from_individuals
        self.copy_from_households = copy_from_households
        self.program = program
        self.rdi_merge_status = rdi_merge_status
        self.create_collection = create_collection
        self.rdi = rdi
        self.manager = "objects" if rdi_merge_status == MergeStatusModel.MERGED else "pending_objects"

    def copy_program_population(self) -> None:
        with transaction.atomic():
            if self.create_collection:
                individuals = self.copy_individuals_with_collections()
                households = self.copy_households_with_collections(individuals)
            else:
                individuals = self.copy_individuals_without_collections()
                households = self.copy_households_without_collections(individuals)

            self.copy_household_related_data(households, individuals)
            self.copy_individual_related_data(individuals)

    def copy_individual(self, individual: Individual) -> Individual:
        copied_from_pk = individual.pk
        individual.pk = None
        copied_flex_fields = get_flex_fields_without_pdu_values(individual)
        individual.flex_fields = populate_pdu_with_null_values(self.program, copied_flex_fields)
        individual.program = self.program
        individual.copied_from_id = copied_from_pk
        individual.registration_data_import = self.rdi
        individual.first_registration_date = timezone.now()
        individual.last_registration_date = timezone.now()
        individual.rdi_merge_status = self.rdi_merge_status
        return individual

    def copy_individuals_with_collections(self) -> List[Individual]:
        individuals_to_create = []
        for individual in self.copy_from_individuals:
            if not individual.individual_collection:
                individual.individual_collection = IndividualCollection.objects.create()
                individual.save()
            individuals_to_create.append(self.copy_individual(individual))
        return Individual.objects.bulk_create(individuals_to_create)

    def copy_individuals_without_collections(self) -> List[Individual]:
        individuals_to_create = []
        for individual in self.copy_from_individuals:
            copied_individual = self.copy_individual(individual)
            copied_individual.individual_collection = None
            individuals_to_create.append(copied_individual)
        return Individual.objects.bulk_create(individuals_to_create)

    def copy_household(self, household: Household, new_individuals: List[Individual]) -> Household:
        copy_from_household_id = household.pk
        household.pk = None
        household.program = self.program
        household.total_cash_received = None
        household.total_cash_received_usd = None
        household.first_registration_date = timezone.now()
        household.last_registration_date = timezone.now()
        household.copied_from_id = copy_from_household_id
        household.registration_data_import = self.rdi
        household.rdi_merge_status = self.rdi_merge_status
        household.head_of_household = (
            getattr(Individual, self.manager)
            .filter(id__in=[ind.pk for ind in new_individuals])
            .get(
                program=self.program,
                copied_from=household.head_of_household,
            )
        )

        return household

    def copy_households_without_collections(self, individuals: List[Individual]) -> List[Household]:
        households_to_create = []
        for household in self.copy_from_households:
            copied_household = self.copy_household(household, individuals)
            copied_household.household_collection = None
            households_to_create.append(copied_household)
        return Household.objects.bulk_create(households_to_create)

    def copy_households_with_collections(self, individuals: List[Individual]) -> List[Household]:
        households_to_create = []
        for household in self.copy_from_households:
            if not household.household_collection:
                household.household_collection = HouseholdCollection.objects.create()
                household.save()
            households_to_create.append(self.copy_household(household, individuals))
        return Household.objects.bulk_create(households_to_create)

    def copy_household_related_data(self, new_households: List[Household], new_individuals: List[Individual]) -> None:
        roles_to_create = []
        entitlement_cards_to_create = []
        for new_household in new_households:
            roles_to_create.extend(self.copy_roles_per_household(new_household, new_individuals))
            entitlement_cards_to_create.extend(self.copy_entitlement_cards_per_household(new_household))
        IndividualRoleInHousehold.objects.bulk_create(roles_to_create)
        EntitlementCard.objects.bulk_create(entitlement_cards_to_create)

    def copy_roles_per_household(
        self,
        new_household: Household,
        new_individuals: List[Individual],
    ) -> List[IndividualRoleInHousehold]:
        roles_in_household = []
        copied_from_roles = IndividualRoleInHousehold.objects.filter(household=new_household.copied_from)
        for role in copied_from_roles:
            role.pk = None
            role.household = new_household
            role.rdi_merge_status = self.rdi_merge_status
            role.individual = next(
                filter(lambda ind: ind.program == self.program and ind.copied_from == role.individual, new_individuals)
            )
            roles_in_household.append(role)
        return roles_in_household

    @staticmethod
    def copy_entitlement_cards_per_household(new_household: Household) -> List[EntitlementCard]:
        entitlement_cards_in_household = []
        old_entitlement_cards = new_household.copied_from.entitlement_cards.all()
        for entitlement_card in old_entitlement_cards:
            entitlement_card.pk = None
            entitlement_card.household = new_household
            entitlement_cards_in_household.append(entitlement_card)
        return entitlement_cards_in_household

    def copy_individual_related_data(self, new_individuals: List[Individual]) -> None:
        individuals_to_update = []
        documents_to_create = []
        individual_identities_to_create = []
        bank_account_infos_to_create = []

        for new_individual in new_individuals:
            new_individual = self.set_household_per_individual(new_individual)
            individuals_to_update.append(new_individual)
            documents_to_create.extend(
                self.copy_document_per_individual(
                    list(new_individual.copied_from.documents.all()),
                    new_individual,
                    self.rdi_merge_status,
                )
            )
            individual_identities_to_create.extend(
                self.copy_individual_identity_per_individual(
                    list(new_individual.copied_from.identities.all()),
                    new_individual,
                    self.rdi_merge_status,
                )
            )
            bank_account_infos_to_create.extend(
                self.copy_bank_account_info_per_individual(
                    list(new_individual.copied_from.bank_account_info.all()),
                    new_individual,
                    self.rdi_merge_status,
                )
            )
        getattr(Individual, self.manager).bulk_update(individuals_to_update, ["household"])
        Document.objects.bulk_create(documents_to_create)
        IndividualIdentity.objects.bulk_create(individual_identities_to_create)
        BankAccountInfo.objects.bulk_create(bank_account_infos_to_create)

    def set_household_per_individual(self, new_individual: Individual) -> Individual:
        new_individual.household = (
            getattr(Household, self.manager)
            .filter(
                program=self.program,
                copied_from_id=new_individual.household_id,
            )
            .first()
        )
        return new_individual

    @staticmethod
    def copy_document_per_individual(
        documents: List[Document],
        individual_representation: Individual,
        rdi_merge_status: str = MergeStatusModel.MERGED,
    ) -> List[Document]:
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
            document.rdi_merge_status = rdi_merge_status
            document.status = Document.STATUS_PENDING
            documents_list.append(document)
        return documents_list

    @staticmethod
    def copy_individual_identity_per_individual(
        identities: List[IndividualIdentity],
        individual_representation: Individual,
        rdi_merge_status: str = MergeStatusModel.MERGED,
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
            identity.rdi_merge_status = rdi_merge_status
            identities_list.append(identity)
        return identities_list

    @staticmethod
    def copy_bank_account_info_per_individual(
        bank_accounts_info: List[BankAccountInfo],
        individual_representation: Individual,
        rdi_merge_status: str = MergeStatusModel.MERGED,
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
            bank_account_info.rdi_merge_status = rdi_merge_status
            bank_accounts_info_list.append(bank_account_info)
        return bank_accounts_info_list


def copy_program_related_data(copy_from_program_id: str, new_program: Program, user_id: str) -> None:
    copy_from_individuals = Individual.objects.filter(program_id=copy_from_program_id, withdrawn=False, duplicate=False)
    copy_from_households = Household.objects.filter(
        program_id=copy_from_program_id,
        withdrawn=False,
    )
    rdi = RegistrationDataImport.objects.create(
        name=f"Default RDI for Programme: {new_program.name}",
        status=RegistrationDataImport.MERGED,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        if new_program.biometric_deduplication_enabled
        else None,
        imported_by=User.objects.get(id=user_id),
        data_source=RegistrationDataImport.PROGRAM_POPULATION,
        number_of_individuals=copy_from_individuals.count(),
        number_of_households=copy_from_households.count(),
        business_area=new_program.business_area,
        program_id=new_program.id,
        import_data=None,
    )
    CopyProgramPopulation(
        copy_from_individuals,
        copy_from_households,
        new_program,
        rdi,
    ).copy_program_population()

    populate_index(
        Individual.objects.filter(program=new_program),
        get_individual_doc(new_program.business_area.slug),
    )
    populate_index(Household.objects.filter(program=new_program), HouseholdDocument)


def create_roles_for_new_representation(
    new_household: Household, program: Program, rdi: RegistrationDataImport
) -> None:
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
            ) = copy_individual(role.individual, program, rdi)

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


def enroll_households_to_program(households: QuerySet, program: Program, user_id: str) -> None:
    households_to_exclude = Household.objects.filter(
        program=program,
        unicef_id__in=households.values_list("unicef_id", flat=True),
    ).values_list("unicef_id", flat=True)
    households = households.exclude(unicef_id__in=households_to_exclude).prefetch_related("entitlement_cards")
    error_messages = []
    rdi = RegistrationDataImport.objects.create(
        status=RegistrationDataImport.MERGED,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        if program.biometric_deduplication_enabled
        else None,
        imported_by=User.objects.get(id=user_id),
        data_source=RegistrationDataImport.ENROLL_FROM_PROGRAM,
        number_of_individuals=0,
        number_of_households=0,
        business_area=program.business_area,
        pull_pictures=False,
        program_id=program.id,
        name=generate_rdi_unique_name(program),
    )
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
                    ) = copy_individual(individual, program, rdi)
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
                household.registration_data_import = rdi
                household.total_cash_received = None
                household.total_cash_received_usd = None
                household.first_registration_date = timezone.now()
                household.last_registration_date = timezone.now()

                if original_head_of_household_unicef_id in individuals_dict:
                    household.head_of_household = individuals_dict[original_head_of_household_unicef_id]
                else:
                    copied_individual_id = individuals_to_exclude_dict[str(original_head_of_household_unicef_id)]
                    household.head_of_household_id = copied_individual_id

                household.save()
                entitlement_cards = CopyProgramPopulation.copy_entitlement_cards_per_household(household)
                EntitlementCard.objects.bulk_create(entitlement_cards)

                ids_to_update = [x.pk for x in individuals_to_create] + external_collectors_id_to_update
                Individual.objects.filter(id__in=ids_to_update).update(household=household)

                create_roles_for_new_representation(household, program, rdi)
        except Exception as e:
            error_message = str(e)
            if "unique_if_not_removed_and_valid_for_representations" in error_message:
                if document_data := re.search(r"\((.*?)\)=\((.*?)\)", error_message):
                    keys = document_data.group(1).split(", ")
                    values = document_data.group(2).split(", ")
                    document_dict = dict(zip(keys, values))
                    error_message = f"Document already exists: {document_dict.get('document_number')}"
            else:
                detail_index = error_message.find("DETAIL")
                if detail_index != -1:
                    error_message = error_message[:detail_index].strip()
            error_messages.append(f"{household.unicef_id}: {error_message}")
    rdi.refresh_population_statistics()
    rdi.bulk_update_household_size()
    if error_messages:
        raise Exception("Following households failed to be enrolled: \n" + "\n".join(error_messages))


def copy_individual(individual: Individual, program: Program, rdi: RegistrationDataImport) -> tuple:
    documents = list(individual.documents.all())
    identities = list(individual.identities.all())
    bank_accounts_info = list(individual.bank_account_info.all())
    if not individual.individual_collection:
        individual.individual_collection = IndividualCollection.objects.create()
        individual.save()

    original_individual_id = individual.id
    individual.copied_from_id = original_individual_id
    individual.pk = None
    individual.flex_fields = get_flex_fields_without_pdu_values(individual)
    populate_pdu_with_null_values(program, individual.flex_fields)
    individual.program = program
    individual.household = None
    individual.registration_data_import = rdi
    individual.first_registration_date = timezone.now()
    individual.last_registration_date = timezone.now()

    documents_to_create = CopyProgramPopulation.copy_document_per_individual(documents, individual)
    identities_to_create = CopyProgramPopulation.copy_individual_identity_per_individual(identities, individual)
    bank_account_info_to_create = CopyProgramPopulation.copy_bank_account_info_per_individual(
        bank_accounts_info, individual
    )
    return individual, documents_to_create, identities_to_create, bank_account_info_to_create


def create_program_partner_access(
    partners_data: List, program: Program, partner_access: Optional[str] = None
) -> List[Dict]:
    if partner_access == Program.ALL_PARTNERS_ACCESS:
        partners = Partner.objects.filter(business_areas=program.business_area).exclude(
            name=settings.DEFAULT_EMPTY_PARTNER
        )
        partners_data = [{"partner": partner.id, "areas": []} for partner in partners]

    for partner_data in partners_data:
        program_partner, _ = ProgramPartnerThrough.objects.get_or_create(
            program=program,
            partner_id=partner_data["partner"],
        )
        if areas := partner_data.get("areas"):
            program_partner.areas.set(Area.objects.filter(id__in=areas))
            program_partner.full_area_access = False
            program_partner.save(update_fields=["full_area_access"])
        else:
            # full area access
            program_partner.full_area_access = True
            program_partner.save(update_fields=["full_area_access"])
    return partners_data


def remove_program_partner_access(partners_data: List, program: Program) -> None:
    partner_ids = [partner_data["partner"] for partner_data in partners_data]
    existing_program_partner_access = ProgramPartnerThrough.objects.filter(
        program=program,
    )
    removed_partner_access = existing_program_partner_access.exclude(
        Q(partner_id__in=partner_ids) | Q(partner__name="UNICEF")
    )
    removed_partner_access.delete()


def get_flex_fields_without_pdu_values(individual: Individual) -> dict:
    flex_fields = individual.flex_fields
    flex_fields_without_pdu = {}
    for flex_field in flex_fields:
        if FlexibleAttribute.objects.filter(
            name=flex_field, program=individual.program, type=FlexibleAttribute.PDU
        ).exists():
            continue
        else:
            flex_fields_without_pdu[flex_field] = flex_fields[flex_field]
    return flex_fields_without_pdu


def generate_rdi_unique_name(program: Program) -> str:
    # add random 4 digits if needed and check if exists RDI name
    default_name = f"RDI for enroll households to Programme: {program.name}"
    while RegistrationDataImport.objects.filter(business_area=program.business_area, name=default_name).exists():
        default_name = f"{default_name} ({randint(1000, 9999)})"
    return default_name
