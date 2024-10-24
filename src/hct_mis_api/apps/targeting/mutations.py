import logging
from typing import Any, Dict, List, Optional, Type

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

import graphene

from hct_mis_api.apps.account.permissions import (
    PermissionMutation,
    PermissionRelayMutation,
    Permissions,
)
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core import utils
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
)
from hct_mis_api.apps.core.validators import raise_program_status_is
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.mis_datahub.celery_tasks import send_target_population_task
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.steficon.schema import SteficonRuleNode
from hct_mis_api.apps.targeting.celery_tasks import (
    target_population_apply_steficon,
    target_population_full_rebuild,
    target_population_rebuild_stats,
)
from hct_mis_api.apps.targeting.inputs import (
    CopyTargetPopulationInput,
    CreateTargetPopulationInput,
    UpdateTargetPopulationInput,
)
from hct_mis_api.apps.targeting.models import (
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.schema import TargetPopulationNode
from hct_mis_api.apps.targeting.validators import (
    FinalizeTargetPopulationValidator,
    LockTargetPopulationValidator,
    RebuildTargetPopulationValidator,
    TargetingCriteriaInputValidator,
    TargetValidator,
    UnlockTargetPopulationValidator,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin
from hct_mis_api.apps.utils.schema import Arg

logger = logging.getLogger(__name__)


class ValidatedMutation(PermissionMutation):
    arguments_validators = []
    object_validators: List = []
    permissions: Optional[Any] = None

    model_class: Type

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "ValidatedMutation":
        for validator in cls.arguments_validators:
            validator.validate(kwargs)
        model_object = cls.get_object(root, info, **kwargs)
        check_concurrency_version_in_mutation(kwargs.get("version"), model_object)
        old_model_object = cls.get_object(root, info, **kwargs)
        if cls.permissions:
            cls.has_permission(info, cls.permissions, model_object.business_area)
        return cls.validated_mutate(root, info, model_object=model_object, old_model_object=old_model_object, **kwargs)

    @classmethod
    def get_object(cls, root: Any, info: Any, **kwargs: Any) -> Any:
        id = kwargs.get("id")
        if id is None:
            return None
        object = get_object_or_404(cls.model_class, id=decode_id_string(id))
        for validator in cls.object_validators:
            validator.validate(object)
        return object


def get_unicef_ids(ids_string: str, type_id: str, program: Program) -> str:
    list_ids = []
    ids_list = ids_string.split(",")
    ids_list = [i.strip() for i in ids_list]
    if type_id == "household":
        hh_ids = [hh_id for hh_id in ids_list if hh_id.startswith("HH")]
        list_ids = (
            Household.objects.filter(unicef_id__in=hh_ids, program=program)
            .order_by("unicef_id")
            .values_list("unicef_id", flat=True)
        )
    if type_id == "individual":
        ind_ids = [ind_id for ind_id in ids_list if ind_id.startswith("IND")]
        list_ids = (
            Individual.objects.filter(unicef_id__in=ind_ids, program=program)
            .order_by("unicef_id")
            .values_list("unicef_id", flat=True)
        )

    return ", ".join(list_ids)


def from_input_to_targeting_criteria(targeting_criteria_input: Dict, program: Program) -> TargetingCriteria:
    rules = targeting_criteria_input.pop("rules", [])
    household_ids = targeting_criteria_input.get("household_ids")
    individual_ids = targeting_criteria_input.get("individual_ids")
    if household_ids:
        targeting_criteria_input["household_ids"] = get_unicef_ids(household_ids, "household", program)
    if individual_ids:
        targeting_criteria_input["individual_ids"] = get_unicef_ids(individual_ids, "individual", program)

    targeting_criteria = TargetingCriteria(**targeting_criteria_input)
    targeting_criteria.save()
    for rule_input in rules:
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        for filter_input in rule_input.get("filters", []):
            rule_filter = TargetingCriteriaRuleFilter(targeting_criteria_rule=rule, **filter_input)
            rule_filter.save()
        for block_input in rule_input.get("individuals_filters_blocks", []):
            block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=rule)
            block.save()
            for individual_block_filters_input in block_input.get("individual_block_filters"):
                individual_block_filters = TargetingIndividualBlockRuleFilter(
                    individuals_filters_block=block, **individual_block_filters_input
                )
                individual_block_filters.save()
    return targeting_criteria


class CreateTargetPopulationMutation(PermissionMutation, ValidationErrorMutationMixin):
    target_population = graphene.Field(TargetPopulationNode)

    class Arguments:
        input = CreateTargetPopulationInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def processed_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "CreateTargetPopulationMutation":
        user = info.context.user
        input_data = kwargs.pop("input")
        program = get_object_or_404(Program, pk=decode_id_string(input_data.get("program_id")))
        program_cycle = get_object_or_404(ProgramCycle, pk=decode_id_string(input_data.get("program_cycle_id")))

        cls.has_permission(info, Permissions.TARGETING_CREATE, program.business_area)

        if program.status != Program.ACTIVE:
            raise ValidationError("Only Active program can be assigned to Targeting")
        if program_cycle.status == ProgramCycle.FINISHED:
            raise ValidationError("Not possible to assign Finished Program Cycle to Targeting")

        tp_name = input_data.get("name", "").strip()
        if TargetPopulation.objects.filter(name=tp_name, program=program, is_removed=False).exists():
            raise ValidationError(f"Target population with name: {tp_name} and program: {program.name} already exists.")
        targeting_criteria_input = input_data.get("targeting_criteria")

        business_area = BusinessArea.objects.get(slug=input_data.pop("business_area_slug"))
        TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)
        targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
        target_population = TargetPopulation(
            name=tp_name,
            created_by=user,
            business_area=business_area,
            excluded_ids=input_data.get("excluded_ids", "").strip(),
            exclusion_reason=input_data.get("exclusion_reason", "").strip(),
            program_cycle=program_cycle,
        )
        target_population.targeting_criteria = targeting_criteria
        target_population.program = program
        target_population.full_clean()
        target_population.save()
        transaction.on_commit(lambda: target_population_full_rebuild.delay(target_population.id))
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program.pk,
            None,
            target_population,
        )
        return cls(target_population=target_population)


class UpdateTargetPopulationMutation(PermissionMutation, ValidationErrorMutationMixin):
    target_population = graphene.Field(TargetPopulationNode)

    class Arguments:
        input = UpdateTargetPopulationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def processed_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "UpdateTargetPopulationMutation":
        input_data = kwargs.get("input")
        tp_id = input_data.get("id")
        target_population = cls.get_object_required(tp_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), target_population)
        old_target_population = cls.get_object(tp_id)

        cls.has_permission(info, Permissions.TARGETING_UPDATE, target_population.business_area)

        name = input_data.get("name", "").strip()
        program_id_encoded = input_data.get("program_id")
        vulnerability_score_min = input_data.get("vulnerability_score_min")
        vulnerability_score_max = input_data.get("vulnerability_score_max")
        excluded_ids = input_data.get("excluded_ids")
        exclusion_reason = input_data.get("exclusion_reason")
        targeting_criteria_input = input_data.get("targeting_criteria")
        program_cycle_id_encoded = input_data.get("program_cycle_id")

        should_rebuild_stats = False
        should_rebuild_list = False

        if target_population.is_locked() and name:
            msg = "Name can't be changed when Target Population is in Locked status"
            logger.error(msg)
            raise ValidationError(msg)
        if (
            TargetPopulation.objects.filter(name=name, program=target_population.program, is_removed=False)
            .exclude(id=decode_id_string(tp_id))
            .exists()
        ):
            raise ValidationError(
                f"Target population with name: {name} and program: {target_population.program.name} already exists."
            )
        if target_population.is_finalized():
            msg = "Finalized Target Population can't be changed"
            logger.error(msg)
            raise ValidationError(msg)
        if target_population.status == TargetPopulation.STATUS_ASSIGNED:
            logger.error("Assigned Target Population can't be changed")
            raise ValidationError("Assigned Target Population can't be changed")
        if name:
            target_population.name = name
        if vulnerability_score_min is not None:
            should_rebuild_stats = True
            target_population.vulnerability_score_min = vulnerability_score_min
        if vulnerability_score_max is not None:
            should_rebuild_stats = True
            target_population.vulnerability_score_max = vulnerability_score_max
        if program_id_encoded:
            should_rebuild_list = True
            program = get_object_or_404(Program, pk=decode_id_string(program_id_encoded))
            target_population.program = program
        else:
            program = target_population.program

        if program_cycle_id_encoded:
            program_cycle = get_object_or_404(ProgramCycle, pk=decode_id_string(program_cycle_id_encoded))
            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Targeting")
            target_population.program_cycle = program_cycle

        if targeting_criteria_input:
            should_rebuild_list = True
            TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)
            targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
            if target_population.status == TargetPopulation.STATUS_OPEN:
                if target_population.targeting_criteria:
                    target_population.targeting_criteria.delete()
                target_population.targeting_criteria = targeting_criteria
        if excluded_ids is not None:
            should_rebuild_list = True
            target_population.excluded_ids = excluded_ids
        if exclusion_reason is not None:
            should_rebuild_list = True
            target_population.exclusion_reason = exclusion_reason
        target_population.full_clean()
        target_population.save()
        # prevent race between commit transaction and using in task
        transaction.on_commit(lambda: cls.rebuild_tp(should_rebuild_list, should_rebuild_stats, target_population))
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)

    @classmethod
    def rebuild_tp(
        cls, should_rebuild_list: bool, should_rebuild_stats: bool, target_population: TargetPopulation
    ) -> None:
        rebuild_list = target_population.is_open() and should_rebuild_list
        rebuild_stats = (not rebuild_list and should_rebuild_list) or should_rebuild_stats
        if rebuild_list or rebuild_stats:
            target_population.build_status = TargetPopulation.BUILD_STATUS_PENDING
            target_population.save()
        if rebuild_list:
            target_population_full_rebuild.delay(target_population.id)
        if rebuild_stats and not rebuild_list:
            target_population_rebuild_stats.delay(target_population.id)

    @classmethod
    def validate_statuses(
        cls,
        name: str,
        target_population: TargetPopulation,
        targeting_criteria_input: Dict,
        vulnerability_score_max: int,
        vulnerability_score_min: int,
    ) -> None:
        if not target_population.is_locked() and (
            vulnerability_score_min is not None or vulnerability_score_max is not None
        ):
            raise ValidationError(
                "You can only set vulnerability_score_min and vulnerability_score_max on Locked Target Population"
            )
        if target_population.is_locked() and name:
            raise ValidationError("Name can't be changed when Target Population is in Locked status")
        if target_population.is_finalized():
            raise ValidationError("Finalized Target Population can't be changed")
        if targeting_criteria_input and not target_population.is_open():
            raise ValidationError("Locked Target Population can't be changed")

    @classmethod
    def get_object_required(cls, id: str) -> TargetPopulation:
        return get_object_or_404(TargetPopulation, id=decode_id_string(id))

    @classmethod
    def get_object(cls, id: Optional[str]) -> Optional[TargetPopulation]:
        if id is None:
            return None
        return cls.get_object_required(id)


class LockTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [LockTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_LOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "LockTargetPopulationMutation":
        user = info.context.user
        target_population = kwargs.get("model_object")
        if target_population.status != TargetPopulation.STATUS_OPEN:
            raise ValidationError("You can only lock open target population")
        old_target_population = kwargs.get("old_model_object")
        target_population.status = TargetPopulation.STATUS_LOCKED
        target_population.changed_by = user
        target_population.change_date = timezone.now()
        target_population.build_status = TargetPopulation.BUILD_STATUS_PENDING
        target_population.save()
        transaction.on_commit(lambda: target_population_rebuild_stats.delay(target_population.id))
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class UnlockTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [UnlockTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_UNLOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @raise_program_status_is(Program.FINISHED)
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "UnlockTargetPopulationMutation":
        target_population = kwargs.get("model_object")
        old_target_population = kwargs.get("old_model_object")
        target_population.status = TargetPopulation.STATUS_OPEN
        target_population.build_status = TargetPopulation.BUILD_STATUS_PENDING
        target_population.save()
        transaction.on_commit(lambda: target_population_rebuild_stats.delay(target_population.id))
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class FinalizeTargetPopulationMutation(ValidatedMutation):
    """
    Set final status and prepare to send to cash assist
    """

    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [FinalizeTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_SEND]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "FinalizeTargetPopulationMutation":
        user = info.context.user
        old_target_population = kwargs.get("old_model_object")
        target_population: TargetPopulation = kwargs["model_object"]
        if target_population.program.business_area.is_payment_plan_applicable:
            with transaction.atomic():
                target_population.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
                target_population.finalized_by = user
                target_population.finalized_at = timezone.now()
                target_population.save()
        else:
            with transaction.atomic():
                target_population.status = TargetPopulation.STATUS_PROCESSING
                target_population.finalized_by = user
                target_population.finalized_at = timezone.now()
                target_population.save()
                transaction.on_commit(
                    lambda: send_target_population_task.delay(target_population_id=target_population.id)
                )
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class CopyTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    target_population = graphene.Field(TargetPopulationNode)

    validation_errors = graphene.Field(Arg)

    class Input:
        target_population_data = CopyTargetPopulationInput()

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def mutate_and_get_payload(cls, _root: Any, info: Any, **kwargs: Any) -> "CopyTargetPopulationMutation":
        try:
            user = info.context.user
            target_population_data = kwargs["target_population_data"]
            name = target_population_data.pop("name").strip()
            target_id = utils.decode_id_string(target_population_data.pop("id"))
            target_population = TargetPopulation.objects.get(id=target_id)
            program = target_population.program
            program_cycle = get_object_or_404(
                ProgramCycle, pk=decode_id_string(target_population_data.get("program_cycle_id"))
            )

            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Targeting")

            cls.has_permission(info, Permissions.TARGETING_DUPLICATE, target_population.business_area)

            if TargetPopulation.objects.filter(name=name, program=program, is_removed=False).exists():
                raise ValidationError(
                    f"Target population with name: {name} and program: {program.name} already exists."
                )

            target_population_copy = TargetPopulation(
                name=name,
                created_by=user,
                business_area=target_population.business_area,
                status=TargetPopulation.STATUS_OPEN,
                child_male_count=target_population.child_male_count,
                child_female_count=target_population.child_female_count,
                adult_male_count=target_population.adult_male_count,
                adult_female_count=target_population.adult_female_count,
                total_households_count=target_population.total_households_count,
                total_individuals_count=target_population.total_individuals_count,
                steficon_rule=target_population.steficon_rule,
                steficon_applied_date=target_population.steficon_applied_date,
                program=program,
                program_cycle=program_cycle,
            )
            target_population_copy.full_clean()
            target_population_copy.save()
            if target_population.targeting_criteria:
                target_population_copy.targeting_criteria = cls.copy_target_criteria(
                    target_population.targeting_criteria
                )
            target_population_copy.full_clean()
            target_population_copy.save()
            target_population_copy.refresh_from_db()
            transaction.on_commit(lambda: target_population_full_rebuild.delay(target_population_copy.id))
            log_create(
                TargetPopulation.ACTIVITY_LOG_MAPPING,
                "business_area",
                info.context.user,
                getattr(program, "pk", None),
                None,
                target_population,
            )
            return CopyTargetPopulationMutation(target_population_copy)
        except ValidationError as e:
            logger.warning(e)
            if hasattr(e, "error_dict"):
                return cls(validation_errors=e.message_dict)  # pragma: no cover
            else:
                raise

    @classmethod
    def copy_target_criteria(cls, targeting_criteria: TargetingCriteria) -> TargetingCriteria:
        targeting_criteria_copy = TargetingCriteria()
        targeting_criteria_copy.save()
        for rule in targeting_criteria.rules.all():
            rule_copy = TargetingCriteriaRule(targeting_criteria=targeting_criteria_copy)
            rule_copy.save()
            for hh_filter in rule.filters.all():
                hh_filter.pk = None
                hh_filter.targeting_criteria_rule = rule_copy
                hh_filter.save()
            for ind_filter_block in rule.individuals_filters_blocks.all():
                ind_filter_block_copy = TargetingIndividualRuleFilterBlock(
                    targeting_criteria_rule=rule_copy, target_only_hoh=ind_filter_block.target_only_hoh
                )
                ind_filter_block_copy.save()
                for ind_filter in ind_filter_block.individual_block_filters.all():
                    ind_filter.pk = None
                    ind_filter.individuals_filters_block = ind_filter_block_copy
                    ind_filter.save()
        targeting_criteria_copy.household_ids = targeting_criteria.household_ids
        targeting_criteria_copy.individual_ids = targeting_criteria.individual_ids
        targeting_criteria_copy.save()

        return targeting_criteria_copy


class DeleteTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    ok = graphene.Boolean()

    class Input:
        target_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    def mutate_and_get_payload(cls, _root: Any, _info: Any, **kwargs: Any) -> "DeleteTargetPopulationMutation":
        target_id = utils.decode_id_string(kwargs["target_id"])
        target_population = TargetPopulation.objects.get(id=target_id)
        old_target_population = TargetPopulation.objects.get(id=target_id)

        cls.has_permission(_info, Permissions.TARGETING_REMOVE, target_population.business_area)

        cls.validate_is_finalized(target_population.status)
        target_population.delete()
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            _info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return DeleteTargetPopulationMutation(ok=True)


class SetSteficonRuleOnTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    target_population = graphene.Field(TargetPopulationNode)

    class Input:
        target_id = graphene.GlobalID(
            required=True,
            node=TargetPopulationNode,
        )
        steficon_rule_id = graphene.GlobalID(
            required=False,
            node=SteficonRuleNode,
        )
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    def mutate_and_get_payload(
        cls, _root: Any, _info: Any, **kwargs: Any
    ) -> "SetSteficonRuleOnTargetPopulationMutation":
        target_id = utils.decode_id_string(kwargs["target_id"])
        target_population = TargetPopulation.objects.get(id=target_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), target_population)
        old_target_population = TargetPopulation.objects.get(id=target_id)
        cls.has_permission(_info, Permissions.TARGETING_UPDATE, target_population.business_area)

        encoded_steficon_rule_id = kwargs.get("steficon_rule_id")
        if encoded_steficon_rule_id is not None:
            steficon_rule_id = utils.decode_id_string(encoded_steficon_rule_id)
            steficon_rule = get_object_or_404(Rule, id=steficon_rule_id)
            steficon_rule_commit = steficon_rule.latest
            if not steficon_rule.enabled or steficon_rule.deprecated:
                raise ValidationError("This steficon rule is not enabled or is deprecated.")
            target_population.steficon_rule = steficon_rule_commit
            target_population.status = TargetPopulation.STATUS_STEFICON_WAIT
            target_population.save()
            target_population_apply_steficon.delay(target_population.pk)
        else:
            target_population.steficon_rule = None
            target_population.vulnerability_score_min = None
            target_population.vulnerability_score_max = None
            target_population.save()
            for selection in HouseholdSelection.objects.filter(target_population=target_population):
                selection.vulnerability_score = None
                selection.save(update_fields=["vulnerability_score"])
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            _info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return SetSteficonRuleOnTargetPopulationMutation(target_population=target_population)


class RebuildTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)

    object_validators = [RebuildTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_UPDATE]

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "RebuildTargetPopulationMutation":
        target_population = kwargs.get("model_object")
        old_target_population = kwargs.get("old_model_object")
        target_population.build_status = TargetPopulation.BUILD_STATUS_PENDING
        target_population.save()
        transaction.on_commit(lambda: target_population_full_rebuild.delay(target_population.id))
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(target_population.program, "pk", None),
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class Mutations(graphene.ObjectType):
    create_target_population = CreateTargetPopulationMutation.Field()
    update_target_population = UpdateTargetPopulationMutation.Field()
    copy_target_population = CopyTargetPopulationMutation.Field()
    delete_target_population = DeleteTargetPopulationMutation.Field()
    lock_target_population = LockTargetPopulationMutation.Field()
    unlock_target_population = UnlockTargetPopulationMutation.Field()
    finalize_target_population = FinalizeTargetPopulationMutation.Field()
    set_steficon_rule_on_target_population = SetSteficonRuleOnTargetPopulationMutation.Field()
    target_population_rebuild = RebuildTargetPopulationMutation.Field()
