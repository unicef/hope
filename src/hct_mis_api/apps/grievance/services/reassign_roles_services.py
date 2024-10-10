from collections import Counter
from typing import TYPE_CHECKING, Dict, Optional, Union
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import (
    HEAD,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.utils.exceptions import log_and_raise
from hct_mis_api.apps.utils.querysets import evaluate_qs

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from hct_mis_api.apps.program.models import Program

"""
Reassing data structure:
{
    "role_id|HEAD":{
        "role": "PRIMARY|ALTERNATE|HEAD",
        "household": "household_id", # base 64 graphql relay id
        "individual": "individual_id", # base 64 graphql relay id
        "new_individual": "new_individual_id" # base 64 graphql relay id
        },
    }
}
"""


def reassign_roles_on_marking_as_duplicate_individual_service(
    role_reassign_data: Dict,
    user: "AbstractUser",
    duplicated_individuals: QuerySet[Individual],
) -> Optional[Household]:
    roles_to_bulk_update = []
    roles_to_delete = []
    duplicated_individuals_ids = [str(individual.id) for individual in duplicated_individuals]
    duplicated_individuals_roles_households_ids = evaluate_qs(
        IndividualRoleInHousehold.objects.filter(individual__in=duplicated_individuals).values_list(
            "household_id", flat=True
        )
    )
    for key,role_data in role_reassign_data.items():
        role_name = role_data.get("role")
        new_individual = get_object_or_404(Individual, id=decode_id_string(role_data.get("new_individual")))
        old_individual_to_log = Individual.objects.get(id=new_individual.id)
        household = get_object_or_404(Household, id=decode_id_string(role_data.get("household")))
        individual_which_loses_role = get_object_or_404(Individual, id=decode_id_string(role_data.get("individual")))

        if new_individual.program != individual_which_loses_role.program:
            raise ValidationError("Cannot reassign head of household to individual from different program")

        if str(individual_which_loses_role.id) not in duplicated_individuals_ids:
            raise ValidationError(f"Individual ({individual_which_loses_role.unicef_id}) was not marked as duplicated")
        if str(new_individual.id) in duplicated_individuals_ids:
            raise ValidationError(
                f"Individual({new_individual.unicef_id}) which get role {role_name} was marked as duplicated"
            )
        if role_name == HEAD:
            reassign_head_of_household_relationship_for_need_adjudication_ticket(
                household, individual_which_loses_role, new_individual, old_individual_to_log, user
            )
            continue

        if new_individual_current_role := IndividualRoleInHousehold.objects.filter(
            household=household, individual=new_individual
        ).first():
            if role_name == ROLE_ALTERNATE and new_individual_current_role.role == ROLE_PRIMARY:
                raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")

            # remove alternate role if the new individual is being assigned as primary
            if role_name == ROLE_PRIMARY and new_individual_current_role.role == ROLE_ALTERNATE:
                roles_to_delete.append(new_individual_current_role)
        if role_name not in (ROLE_PRIMARY, ROLE_ALTERNATE):
            raise ValidationError("Invalid role name")
        role = IndividualRoleInHousehold.objects.filter(
            role=role_name,
            household=household,
            individual=individual_which_loses_role,
        ).first()
        if role is None:
            raise ValidationError(
                f"Individual with unicef_id {individual_which_loses_role.unicef_id} does not have role {role_name} in household with unicef_id {household.unicef_id}"
            )
        role.individual = new_individual
        roles_to_bulk_update.append(role)

    for role_to_delete in roles_to_delete:
        role_to_delete.delete(soft=False)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])

    # check if all households have head of household
    for individual in duplicated_individuals:
        household_to_check = Household.objects.get(id=individual.household.id)
        if str(household_to_check.head_of_household.id) in duplicated_individuals_ids:
            raise ValidationError(
                f"Role for head of household in household with unicef_id {household_to_check.unicef_id} was not reassigned, when individual ({individual.unicef_id}) was marked as duplicated"
            )

    # check if all households have primary role:
    for household_id in duplicated_individuals_roles_households_ids:
        primary_role = IndividualRoleInHousehold.objects.filter(household=household_id, role=ROLE_PRIMARY).first()
        if primary_role is None:
            raise ValidationError(f"Household with id {household_id} was left without primary role")
        if str(primary_role.individual.id) in duplicated_individuals_ids:
            raise ValidationError(
                f"Primary role in household with id {household_id} is still assigned to duplicated individual({primary_role.individual.unicef_id})"
            )


def reassign_head_of_household_relationship_for_need_adjudication_ticket(
    household: Household,
    individual_which_loses_role: Individual,
    new_individual: Individual,
    old_individual_to_log: Individual,
    user: "User",
):
    if household != individual_which_loses_role.household:
        raise ValidationError("Household missmatch Individual which loses role and household")
    if household.head_of_household.pk == new_individual.pk or new_individual == individual_which_loses_role:
        raise ValidationError("Cannot reassign head of household to the same individual")
    if new_individual.household != individual_which_loses_role.household:
        raise ValidationError("Cannot reassign head of household to individual from different household")
    household.head_of_household = new_individual
    household.save()
    # update relationship to unknown for all individuals except new head of household
    # because we don't know relationship to new head
    individuals_to_change_relationship_to_unknown = evaluate_qs(
        household.individuals.exclude(id=new_individual.id).order_by("id")
    )
    household.individuals.exclude(id__in=individuals_to_change_relationship_to_unknown).update(
        relationship=RELATIONSHIP_UNKNOWN
    )
    updated_individuals_with_relationship_unknown = evaluate_qs(
        household.individuals.exclude(id=new_individual.id).order_by("id")
    )
    for individual_before_change, individual_after_change in zip(
        individuals_to_change_relationship_to_unknown, updated_individuals_with_relationship_unknown
    ):
        log_create(
            Individual.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            individual_before_change.program.pk,
            individual_before_change,
            individual_after_change,
        )
    new_individual.relationship = HEAD
    new_individual.save()
    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        user,
        new_individual.program.pk,
        old_individual_to_log,
        new_individual,
    )


def reassign_roles_on_disable_individual_service(
    individual_to_remove: Individual,
    role_reassign_data: Dict,
    user: "AbstractUser",
    program_or_qs: Union["Program", QuerySet["Program"]],
    individual_key: str = "individual",
) -> Optional[Household]:
    roles_to_bulk_update = []
    roles_to_delete = []
    for role_data in role_reassign_data.values():
        role_name = role_data.get("role")
        new_individual = get_object_or_404(Individual, id=decode_id_string(role_data.get(individual_key)))
        household = get_object_or_404(Household, id=decode_id_string(role_data.get("household")))
        old_individual = Individual.objects.get(id=new_individual.id)

        if role_name == HEAD:
            if household.head_of_household.pk != new_individual.pk:
                household.head_of_household = new_individual

                # can be directly saved, because there is always only one head of household to update
                household.save()
                household.individuals.exclude(id=new_individual.id).update(relationship=RELATIONSHIP_UNKNOWN)
            new_individual.relationship = HEAD
            new_individual.save()
            log_create(
                Individual.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                getattr(program_or_qs, "pk", None) if isinstance(program_or_qs, UUID) else program_or_qs,
                old_individual,
                new_individual,
            )

        if new_individual_current_role := IndividualRoleInHousehold.objects.filter(
            household=household, individual=new_individual
        ).first():
            if role_name == ROLE_ALTERNATE and new_individual_current_role.role == ROLE_PRIMARY:
                raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")
            elif (
                role_name == ROLE_PRIMARY and new_individual_current_role.role == ROLE_ALTERNATE
            ):  # remove alternate role if the new individual is being assigned as primary
                roles_to_delete.append(new_individual_current_role)
        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold,
                role=role_name,
                household=household,
                individual=individual_to_remove,
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    primary_roles_count = Counter([role.get("role") for role in role_reassign_data.values()])[ROLE_PRIMARY]

    household_to_remove = individual_to_remove.household
    is_one_individual = household_to_remove.individuals.count() == 1 if household_to_remove else False

    if primary_roles_count != individual_to_remove.count_primary_roles() and not is_one_individual:
        log_and_raise("Ticket cannot be closed, not all roles have been reassigned")

    if (
        all(HEAD not in key for key in role_reassign_data.keys())
        and individual_to_remove.is_head()
        and not is_one_individual
    ):
        log_and_raise("Ticket cannot be closed, head of household has not been reassigned")

    for role_to_delete in roles_to_delete:
        role_to_delete.delete(soft=False)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])

    return household_to_remove


def reassign_roles_on_update_service(
    individual: Individual,
    role_reassign_data: Dict,
    user: "AbstractUser",
    program_or_qs: Union["Program", QuerySet["Program"]],
) -> None:
    roles_to_bulk_update = []
    roles_to_delete = []
    for role_data in role_reassign_data.values():
        role_name = role_data.get("role")
        new_individual = get_object_or_404(Individual, id=decode_id_string(role_data.get("individual")))
        household = get_object_or_404(Household, id=decode_id_string(role_data.get("household")))
        old_individual = Individual.objects.get(id=new_individual.id)

        if role_name == HEAD:
            household.head_of_household = new_individual
            household.save()
            new_individual.relationship = HEAD
            new_individual.save()
            log_create(
                Individual.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                getattr(program_or_qs, "pk", None) if isinstance(program_or_qs, UUID) else program_or_qs,
                old_individual,
                new_individual,
            )

        if new_individual_current_role := IndividualRoleInHousehold.objects.filter(
            household=household, individual=new_individual
        ).first():
            if role_name == ROLE_ALTERNATE and new_individual_current_role.role == ROLE_PRIMARY:
                raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")
            elif (
                role_name == ROLE_PRIMARY and new_individual_current_role.role == ROLE_ALTERNATE
            ):  # remove alternate role if the new individual is being assigned as primary
                roles_to_delete.append(new_individual_current_role)

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold,
                role=role_name,
                household=household,
                individual=individual,
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    for role_to_delete in roles_to_delete:
        role_to_delete.delete(soft=False)
    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])
