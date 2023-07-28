from collections import Counter
from typing import TYPE_CHECKING, Dict, Union
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

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

    from hct_mis_api.apps.program.models import Program


def reassign_roles_on_disable_individual_service(
    individual_to_remove: Individual,
    role_reassign_data: Dict,
    user: "AbstractUser",
    program_or_qs: Union["Program", QuerySet["Program"]],
    individual_key: str = "individual",
) -> Household:
    roles_to_bulk_update = []
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

        if role_name == ROLE_ALTERNATE and new_individual.role == ROLE_PRIMARY:
            raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")

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
        log_and_raise("Ticket cannot be closed head of household has not been reassigned")

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

        if role_name == ROLE_ALTERNATE and new_individual.role == ROLE_PRIMARY:
            raise ValidationError("Cannot reassign the role. Selected individual has primary collector role.")

        if role_name in (ROLE_PRIMARY, ROLE_ALTERNATE):
            role = get_object_or_404(
                IndividualRoleInHousehold,
                role=role_name,
                household=household,
                individual=individual,
            )
            role.individual = new_individual
            roles_to_bulk_update.append(role)

    if roles_to_bulk_update:
        IndividualRoleInHousehold.objects.bulk_update(roles_to_bulk_update, ["individual"])
