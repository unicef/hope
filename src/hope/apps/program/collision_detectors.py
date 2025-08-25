from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.transaction import atomic
from django.forms.models import model_to_dict
from strategy_field.registry import Registry

from models.household import Household, Individual, IndividualRoleInHousehold

# only for typing purposes
if TYPE_CHECKING:
    pass


class AbstractCollisionDetector:
    def __init__(self, context: "Program"):
        self.program = context
        if not self.program.collision_detection_enabled:
            raise ValueError("Collision detection is not enabled for this program")  # pragma: no cover

    def detect_collision(self, household: Household) -> str | None:
        raise NotImplementedError("Subclasses should implement this method")  # pragma: no cover

    def _update_roles_in_household(self, household_id_destination: str, roles_by_id: dict[int, str]) -> None:
        """Clean Roles.

        1. Deletes all roles in destination household
        2. Reassigns roles from source household to destination household
        """
        IndividualRoleInHousehold.all_objects.filter(household_id=household_id_destination).delete()
        for individual_id, role in roles_by_id.items():
            IndividualRoleInHousehold.all_objects.create(
                individual_id=individual_id,
                role=role,
                household_id=household_id_destination,
                rdi_merge_status=Individual.MERGED,
            )

    def _update_individual_identities(
        self, individual_destination: Individual, individual_source: Individual
    ) -> Individual:
        """Update individual identities.

        1. Remove all identities from destination individual
        2. Reassign identities from source individual to destination individual
        :return: The updated destination individual
        """
        identities_destination = individual_destination.identities(manager="all_objects").all()
        identities_source = individual_source.identities(manager="all_objects").all()
        # 1. Remove all identities from destination individual
        identities_destination.delete()
        # 2. Reassign identities from source individual to destination individual
        for identity in identities_source:
            identity.individual = individual_destination
            identity.rdi_merge_status = Individual.MERGED
            identity.save()

        return individual_destination

    def _update_documents(self, individual_destination: Individual, individual_source: Individual) -> Individual:
        """Update documents.

        1. Saves statuses in dict by number+type_id
        2. Deletes all documents in destination
        4. Reassigns documents from source individual to destination individual
        5. Updates statuses in destination (for unchanged documents)
        """
        documents_source = individual_source.documents(manager="all_objects").all()
        documents_destination = individual_destination.documents(manager="all_objects").all()

        # 1. Save statuses in dict by number+type_id
        destination_statuses = {}
        for doc in documents_destination:
            key = f"{doc.document_number}_{doc.type_id}"
            destination_statuses[key] = doc.status

        # 2. Delete all documents in destination
        documents_destination.delete()

        # 4. Reassign documents from source individual to destination individual
        for doc in documents_source:
            # Assign it to the destination individual
            doc.individual = individual_destination
            doc.rdi_merge_status = Individual.MERGED
            # 5. Update statuses in destination (for unchanged documents)
            key = f"{doc.document_number}_{doc.type_id}"
            if key in destination_statuses:
                doc.status = destination_statuses[key]
            doc.save()

        return individual_destination

    def _update_accounts(self, individual_destination: Individual, individual_source: Individual) -> Individual:
        """Clean accounts.

        1. Deletes all accounts in destination individual
        2. Reassigns accounts from source individual to destination individual
        """
        accounts_destination = individual_destination.accounts(manager="all_objects").all()
        accounts_source = individual_source.accounts(manager="all_objects").all()

        # 1. Deletes all accounts in destination individual
        accounts_destination.delete()

        # 2. Reassigns accounts from source individual to destination individual
        for account in accounts_source:
            account.individual = individual_destination
            account.rdi_merge_status = Individual.MERGED
            account.save()

        return individual_destination

    def _update_individual(self, individual_destination: Individual, individual_source: Individual) -> None:
        exclude = {
            "id",
            "pk",
            "unicef_id",
            "collection_id",
            "collection",
            "created_at",
            "program_id",
            "individual_collection_id",
            "individual_collection",
            "rdi_merge_status",
            "registration_data_import",
            "registration_data_import_id",
            "household",
            "household_id",
        }
        self._update_db_instance(individual_source, individual_destination, exclude)

    def _update_household(
        self,
        household_destination: Household,
        household_source: Household,
        head_of_household: Individual,
    ) -> None:
        exclude = {
            "id",
            "pk",
            "unicef_id",
            "created_at",
            "program_id",
            "updated_at",
            "household_collection_id",
            "household_collection",
            "rdi_merge_status",
            "extra_rdis",
            "representatives",
            "registration_data_import",
            "registration_data_import_id",
            "head_of_household",
            "head_of_household_id",
        }
        self._update_db_instance(household_source, household_destination, exclude, extra_fields={})
        household_source.delete(soft=False)
        Household.objects.filter(id=household_destination.id).update(head_of_household=head_of_household)

    def _update_db_instance(
        self,
        source: models.Model,
        destination: models.Model,
        exclude: set[str],
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Update a database instance by copying data from a source model to a destination model.

        This function performs the following steps:
        1. Converts the source model to a dictionary, excluding specified fields
        2. Removes many-to-many fields from the data dictionary
        3. Adds any extra fields provided to the data dictionary
        4. Updates the destination instance in the database with the prepared data

        Args:
            source: The source Django model instance to copy data from
            destination: The destination Django model instance to update
            exclude: A set/list of field names to exclude from the update
            extra_fields: Optional dictionary of additional fields to set on the destination

        """
        data = model_to_dict(source, exclude=list(exclude))
        for name, field in source._meta.fields_map.items():
            if field.many_to_many:
                data.pop(name, None)
        for key, value in (extra_fields or {}).items():
            data[key] = value
        destination.__class__.objects.filter(pk=destination.id).update(**data)


class IdentificationKeyCollisionDetector(AbstractCollisionDetector):
    def __init__(self, context: "Program"):
        super().__init__(context)
        self.unique_identification_keys_dict: dict[str, str] | None = None

    def initialize(self) -> None:
        if self.unique_identification_keys_dict is not None:
            return
        self.unique_identification_keys_dict = {}
        ids_with_uniquekey_list = list(
            Household.objects.filter(program=self.program, identification_key__isnull=False)
            .values_list("id", "identification_key")
            .distinct("id")
        )
        for hh_id, key in ids_with_uniquekey_list:
            self.unique_identification_keys_dict[key] = str(hh_id)

    def detect_collision(self, household: Household) -> str | None:
        self.initialize()
        return self.unique_identification_keys_dict.get(household.identification_key, None)

    @atomic
    def update_household(self, household_to_merge: Household) -> None:
        """Update an existing household with data from another household based on matching identification keys.

        This method performs the following steps:
        1. Sanity check - household_to_merge must have an identification key
        2. Get the old household id that has the same identification key. If there is no such household, return
        3. Sanity check - All individuals in both households must have an identification key
        4. Prepare the lists of individuals to add, update and remove.
        By comparing if the identification keys exist in both households
        5. Store the new roles (by identification_keys), because it will be deleted when we delete individuals
        6. Store the head of household identification key, we will have no access to it when we delete individuals
        7. Update the individuals in the old household with the new ones
        8. Delete the individuals that are in the old household but not in the new household
        9. Add the new individuals to the old household
        10. Get the fresh list of individuals in the old household
        11. Update the roles in the old household, based on the dict of roles by identification key
        12. Update the household with the new data

        Args:
            household_to_merge: The household containing the updated data to merge

        Raises:
            ValueError: If any individual in either household lacks an identification key

        """
        # 1. Sanity check - household_to_merge must have an identification key
        if not household_to_merge.identification_key:
            return
        # 2. Get the old household id that has the same identification key. If there is no such household, return
        old_household_id = self.detect_collision(household_to_merge)
        if old_household_id is None:
            return
        old_household = Household.objects.get(id=old_household_id)
        old_individuals = Household.objects.get(id=old_household_id).individuals.all()
        individuals_to_merge = household_to_merge.individuals(manager="all_objects").all()
        # 3. Sanity check - All individuals in both households must have an identification key
        if any(x for x in old_individuals if x.identification_key is None):
            raise ValueError(
                f"Cannot merge households with individuals with no identification key household {old_household_id}"
            )
        if any(x for x in individuals_to_merge if x.identification_key is None):
            raise ValueError(
                f"Cannot merge households with individuals with no identification key {household_to_merge.id}"
            )
        # 4. Prepare the lists of individuals to add, update and remove.
        # By comparing if the identification keys exist in both households
        old_individuals_by_identification_key = {
            ind.identification_key: ind for ind in old_individuals if ind.identification_key
        }
        individuals_to_merge_by_identification_key = {
            ind.identification_key: ind for ind in individuals_to_merge if ind.identification_key
        }
        identification_keys_to_remove = set(old_individuals_by_identification_key.keys()) - set(
            individuals_to_merge_by_identification_key.keys()
        )
        individuals_to_remove = [
            old_individuals_by_identification_key[key] for key in identification_keys_to_remove
        ]  # don't exist in the new household
        identification_keys_to_add = set(individuals_to_merge_by_identification_key.keys()) - set(
            old_individuals_by_identification_key.keys()
        )
        individuals_to_add = [individuals_to_merge_by_identification_key[key] for key in identification_keys_to_add]
        identification_keys_to_update = set(individuals_to_merge_by_identification_key.keys()) & set(
            old_individuals_by_identification_key.keys()
        )

        # 5. Store the new roles (by identification_keys), because it will be deleted when we delete individuals
        role_by_identification_key = {
            role.individual.identification_key: role.role
            for role in household_to_merge.individuals_and_roles(manager="all_objects").all()
        }
        # 6. Store the head of household identification key, we will have no access to it when we delete individuals
        head_of_household_identification_key = household_to_merge.head_of_household.identification_key
        old_household.head_of_household = None
        old_household.save()
        # 7. Update the individuals in the old household with the new ones
        for key in identification_keys_to_update:
            individual_original = old_individuals_by_identification_key[key]
            individual_source = individuals_to_merge_by_identification_key[key]
            self._update_documents(individual_original, individual_source)
            self._update_individual_identities(individual_original, individual_source)
            self._update_accounts(individual_original, individual_source)
            self._update_individual(individual_original, individual_source)
        # 8. Delete the individuals that are in the old household but not in the new household
        Individual.all_objects.filter(id__in=[ind.id for ind in individuals_to_remove]).delete()
        # 9. Add the new individuals to the old household
        Individual.all_objects.filter(id__in=[ind.id for ind in individuals_to_add]).update(
            household=old_household_id,
            rdi_merge_status=Individual.MERGED,
        )
        # 10. Get the fresh list of individuals in the old household
        updated_individuals_in_household = Household.all_objects.get(id=old_household_id).individuals.all()
        updated_individuals_in_household_by_identification_key = {
            ind.identification_key: ind for ind in updated_individuals_in_household if ind.identification_key
        }
        updated_head_of_household = updated_individuals_in_household_by_identification_key[
            head_of_household_identification_key
        ]
        # 11. Update the roles in the old household, based on the dict of roles by identification key
        roles_list = [
            (updated_individuals_in_household_by_identification_key[key], role)
            for key, role in role_by_identification_key.items()
        ]
        self._update_roles_in_household(
            household_id_destination=old_household_id,
            roles_by_id={ind.id: role for ind, role in roles_list},
        )
        # 12. Update the household with the new data
        self._update_household(
            Household.objects.get(id=old_household_id),
            household_to_merge,
            updated_head_of_household,
        )


collision_detectors_registry = Registry(AbstractCollisionDetector)
collision_detectors_registry.append(IdentificationKeyCollisionDetector)
