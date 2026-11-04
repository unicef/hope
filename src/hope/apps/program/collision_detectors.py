from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import Q
from django.db.transaction import atomic
from django.forms.models import model_to_dict
from strategy_field.registry import Registry

from hope.apps.household.const import REMOVED_BY_COLLISION
from hope.models import BiometricDedupeSimilarityPair, Household, Individual, IndividualRoleInHousehold

if TYPE_CHECKING:
    from hope.models import Program


class AbstractCollisionDetector:
    def __init__(self, context: "Program"):
        self.program = context

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
            "is_removed",
            "removed_date",
            "updated_at",
            "last_sync_at",
            "version",
            "internal_data",
            "copied_from",
            "copied_from_id",
            "origin_unicef_id",
            "is_migration_handled",
            "migrated_at",
            "imported_individual_id",
            "withdrawn",
            "withdrawn_date",
            "first_registration_date",
            "age_at_registration",
            "duplicate",
            "duplicate_date",
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
            "biometric_deduplication_golden_record_status",
            "biometric_deduplication_batch_status",
            "biometric_deduplication_golden_record_results",
            "biometric_deduplication_batch_results",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
        }
        data = self._get_update_data(individual_source, exclude)
        self._record_replaced_ids(individual_destination, data, ("country_workspace_id", "originating_id"))
        self._restore_removed_by_collision(individual_destination, data)
        self._update_biometric_pairs(individual_destination, individual_source)
        # the source still holds the country_workspace_id and originating_id the destination takes over,
        # both unique among live rows, so it has to be gone before the copy
        Household.all_objects.filter(head_of_household=individual_source).update(head_of_household=None)
        # queryset delete: Individual.delete() would send individual_deleted (an adjust_program_size job) per member
        Individual.all_objects.filter(pk=individual_source.pk).delete()
        Individual.objects.filter(pk=individual_destination.pk).update(**data)

    def _update_biometric_pairs(self, individual_destination: Individual, individual_source: Individual) -> None:
        """Reassign biometric deduplication pairs.

        Pairs are stored against the pending source before the merge and would be cascade-deleted with it.
        1. Recreates each source pair with the destination in place of the source
        2. Skips pairs that would point the destination at itself
        """
        pairs_source = BiometricDedupeSimilarityPair.objects.filter(
            Q(individual1=individual_source) | Q(individual2=individual_source)
        )
        pairs_destination = []
        for pair in pairs_source:
            ids = [
                individual_destination.pk if individual_id == individual_source.pk else individual_id
                for individual_id in (pair.individual1_id, pair.individual2_id)
            ]
            if ids[0] == ids[1]:
                continue
            if None not in ids:
                # same ordering as BiometricDedupeSimilarityPair.bulk_add_pairs (individual1_lt_individual2)
                ids.sort(key=str)
            pairs_destination.append(
                BiometricDedupeSimilarityPair(
                    program_id=pair.program_id,
                    individual1_id=ids[0],
                    individual2_id=ids[1],
                    similarity_score=pair.similarity_score,
                    status_code=pair.status_code,
                )
            )
        BiometricDedupeSimilarityPair.objects.bulk_create(pairs_destination, ignore_conflicts=True)

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
            "is_removed",
            "removed_date",
            "last_sync_at",
            "version",
            "internal_data",
            "copied_from",
            "copied_from_id",
            "origin_unicef_id",
            "is_migration_handled",
            "migrated_at",
            "withdrawn",
            "withdrawn_date",
            "first_registration_date",
            "total_cash_received",
            "total_cash_received_usd",
            "storage_obj",
            "storage_obj_id",
            "kobo_submission_uuid",
            "kobo_submission_time",
            "flex_registrations_record_id",
        }
        data = self._get_update_data(household_source, exclude)
        self._record_replaced_ids(household_destination, data, ("originating_id",))
        # need to set None because of protected FK
        household_source.head_of_household = None
        household_source.save()
        # the source still holds the originating_id the destination takes over,
        # unique among live rows, so it has to be gone before the copy
        household_source.delete(soft=False)
        Household.objects.filter(id=household_destination.id).update(**data, head_of_household=head_of_household)

    def _record_replaced_ids(self, destination: models.Model, data: dict[str, Any], fields: tuple[str, ...]) -> None:
        """Append the ids the destination held before this collision to internal_data, one entry per collision."""
        previous = {
            name: getattr(destination, name)
            for name in fields
            if getattr(destination, name) is not None and getattr(destination, name) != data.get(name)
        }
        if not previous:
            return
        internal_data = data.get("internal_data", dict(destination.internal_data or {}))
        internal_data["collision_replaced_ids"] = [*internal_data.get("collision_replaced_ids", []), previous]
        data["internal_data"] = internal_data

    def _restore_removed_by_collision(self, destination: Individual, data: dict[str, Any]) -> None:
        """Undo _process_removed_individual when a member dropped by an earlier collision is back in the household."""
        internal_data = data.get("internal_data", dict(destination.internal_data or {}))
        removed = internal_data.pop("removed_by_collision_detector", None)
        if removed is None:
            return
        data["internal_data"] = internal_data
        if removed.get("withdrawn_by_collision"):
            data["withdrawn"] = False
            data["withdrawn_date"] = None

    def _get_update_data(self, source: models.Model, exclude: set[str]) -> dict[str, Any]:
        """Prepare the data to copy from a source model to a destination model.

        This function performs the following steps:
        1. Converts the source model to a dictionary, excluding specified fields
        2. Removes many-to-many fields from the data dictionary

        Args:
            source: The source Django model instance to copy data from
            exclude: A set/list of field names to exclude from the update

        """
        data = model_to_dict(source, exclude=list(exclude))
        for name, field in source._meta.fields_map.items():
            if field.many_to_many:
                data.pop(name, None)
        return data

    def _process_removed_individual(
        self,
        individual: Individual,
        household_id: str,
        old_head_of_household_id: Any,
    ) -> None:
        """Process an individual being removed from household during collision.

        Instead of deleting:
        1. Get previous roles
        2. Check if was head_of_household
        3. Store previous data in internal_data
        4. Update relationship to REMOVED_BY_COLLISION
        5. Remove roles from IndividualRoleInHousehold
        6. Withdraw the individual
        """
        # 1. Get previous roles before deleting them
        previous_roles = list(
            IndividualRoleInHousehold.all_objects.filter(individual=individual, household_id=household_id).values_list(
                "role", flat=True
            )
        )

        # 2. Check if was head_of_household
        was_head = individual.id == old_head_of_household_id

        # 3. Store previous data in internal_data
        individual.internal_data["removed_by_collision_detector"] = {
            "previous_relationship": individual.relationship,
            "previous_roles": previous_roles,
            "was_head_of_household": was_head,
            "withdrawn_by_collision": not individual.withdrawn,
        }

        # 4. Update relationship to REMOVED_BY_COLLISION
        individual.relationship = REMOVED_BY_COLLISION
        individual.save(update_fields=["relationship", "internal_data"])

        # 5. Remove roles from IndividualRoleInHousehold
        IndividualRoleInHousehold.all_objects.filter(individual=individual, household_id=household_id).delete()

        # 6. Withdraw the individual (only if not already withdrawn)
        if not individual.withdrawn:
            individual.withdraw(notify=False)


class NoopCollisionDetector(AbstractCollisionDetector):
    def detect_collision(self, household: Household) -> str | None:
        pass

    @atomic
    def update_household(self, household_to_merge: Household) -> None:
        pass


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
        if household.identification_key is None:
            return None
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
        8. Process individuals that are in the old household but not in the new household
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
        # Store old head_of_household_id before we clear it (needed for step 8)
        old_head_of_household_id = old_household.head_of_household_id
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
        # 8. Process individuals that are in the old household but not in the new household
        for individual in individuals_to_remove:
            self._process_removed_individual(individual, old_household_id, old_head_of_household_id)
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


collision_detectors_registry: Registry = Registry(AbstractCollisionDetector)
collision_detectors_registry.append(IdentificationKeyCollisionDetector)
collision_detectors_registry.append(NoopCollisionDetector)
