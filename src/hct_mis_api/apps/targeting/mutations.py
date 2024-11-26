import logging
from typing import Any, Dict, List, Optional, Type

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene

from hct_mis_api.apps.account.permissions import (
    PermissionMutation,
    PermissionRelayMutation,
    Permissions,
)
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core import utils
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    get_program_id_from_headers,
)
from hct_mis_api.apps.core.validators import raise_program_status_is
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.celery_tasks import (
    payment_plan_apply_steficon_hh_selection,
    payment_plan_full_rebuild,
    payment_plan_rebuild_stats,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.schema import PaymentPlanNode
from hct_mis_api.apps.program.models import Program, ProgramCycle
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.steficon.schema import SteficonRuleNode
from hct_mis_api.apps.targeting.inputs import (
    CopyTargetPopulationInput,
    CreateTargetPopulationInput,
    UpdateTargetPopulationInput,
)
from hct_mis_api.apps.targeting.models import (
    TargetingCollectorBlockRuleFilter,
    TargetingCollectorRuleFilterBlock,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
)
from hct_mis_api.apps.targeting.schema import TargetPopulationNode
from hct_mis_api.apps.targeting.validators import (
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

    targeting_criteria = TargetingCriteria(**targeting_criteria_input)
    targeting_criteria.save()

    for rule in rules:
        household_ids = rule.get("household_ids", "")
        individual_ids = rule.get("individual_ids", "")
        households_filters_blocks = rule.get("households_filters_blocks", [])
        individuals_filters_blocks = rule.get("individuals_filters_blocks", [])
        collectors_filters_blocks = rule.get("collectors_filters_blocks", [])
        if household_ids:
            household_ids = get_unicef_ids(household_ids, "household", program)
        if individual_ids:
            individual_ids = get_unicef_ids(individual_ids, "individual", program)

        tc_rule = TargetingCriteriaRule(
            targeting_criteria=targeting_criteria, household_ids=household_ids, individual_ids=individual_ids
        )
        tc_rule.save()
        for hh_filter in households_filters_blocks:
            tc_rule_filter = TargetingCriteriaRuleFilter(targeting_criteria_rule=tc_rule, **hh_filter)
            tc_rule_filter.save()

        for ind_filter_block in individuals_filters_blocks:
            ind_block = TargetingIndividualRuleFilterBlock(targeting_criteria_rule=tc_rule)
            ind_block.save()
            for ind_filter in ind_filter_block.get("individual_block_filters", []):
                individual_filter = TargetingIndividualBlockRuleFilter(
                    individuals_filters_block=ind_block, **ind_filter
                )
                individual_filter.save()

        for collector_filter_block in collectors_filters_blocks:
            collector_block = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=tc_rule)
            collector_block.save()
            for collectors_filter in collector_filter_block.get("collector_block_filters", []):
                collector_block_filters = TargetingCollectorBlockRuleFilter(
                    collector_block_filters=collector_block, **collectors_filter
                )
                collector_block_filters.save()

    return targeting_criteria


class CreateTargetPopulationMutation(PermissionMutation, ValidationErrorMutationMixin):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = CreateTargetPopulationInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def processed_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "CreateTargetPopulationMutation":
        user = info.context.user
        input_data = kwargs.pop("input")
        program_id = get_program_id_from_headers(info.context.headers)
        program = get_object_or_404(Program, pk=program_id)
        program_cycle = get_object_or_404(ProgramCycle, pk=decode_id_string(input_data.get("program_cycle_id")))
        business_area = program.business_area

        cls.has_permission(info, Permissions.TARGETING_CREATE, business_area)

        if program.status != Program.ACTIVE:
            raise ValidationError("Only Active program can be assigned to Targeting")
        if program_cycle.status == ProgramCycle.FINISHED:
            raise ValidationError("Not possible to assign Finished Program Cycle to Targeting")

        pp_name = input_data.get("name", "").strip()
        if PaymentPlan.objects.filter(name=pp_name, program=program, is_removed=False).exists():
            raise ValidationError(f"Payment Plan with name: {pp_name} and program: {program.name} already exists.")
        targeting_criteria_input = input_data.get("targeting_criteria")

        TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)
        targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
        payment_plan = PaymentPlan(
            status=PaymentPlan.Status.DRAFT,
            name=pp_name,
            created_by=user,
            business_area=business_area,
            excluded_ids=input_data.get("excluded_ids", "").strip(),
            exclusion_reason=input_data.get("exclusion_reason", "").strip(),
            program_cycle=program_cycle,
        )
        payment_plan.targeting_criteria = targeting_criteria
        payment_plan.program = program
        payment_plan.full_clean()  # ???
        payment_plan.save()
        transaction.on_commit(lambda: payment_plan_full_rebuild.delay(payment_plan.id))
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            program.pk,
            None,
            payment_plan,
        )
        return cls(payment_plan=payment_plan)


class UpdateTargetPopulationMutation(PermissionMutation, ValidationErrorMutationMixin):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)

    class Arguments:
        input = UpdateTargetPopulationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def processed_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "UpdateTargetPopulationMutation":
        input_data = kwargs.get("input")
        pp_id = input_data.get("id")
        payment_plan = cls.get_object_required(pp_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan)
        old_payment_plan = cls.get_object(pp_id)

        cls.has_permission(info, Permissions.TARGETING_UPDATE, payment_plan.business_area)

        name = input_data.get("name", "").strip()
        vulnerability_score_min = input_data.get("vulnerability_score_min")
        vulnerability_score_max = input_data.get("vulnerability_score_max")
        excluded_ids = input_data.get("excluded_ids")
        exclusion_reason = input_data.get("exclusion_reason")
        targeting_criteria_input = input_data.get("targeting_criteria")
        program_cycle_id_encoded = input_data.get("program_cycle_id")
        program = payment_plan.program

        should_rebuild_stats = False
        should_rebuild_list = False

        if payment_plan.is_population_locked() and name:
            msg = "Name can't be changed when Payment Plan is in Locked Population status"
            logger.error(msg)
            raise ValidationError(msg)
        if (
            PaymentPlan.objects.filter(name=name, program=payment_plan.program, is_removed=False)
            .exclude(id=decode_id_string(pp_id))
            .exists()
        ):
            raise ValidationError(
                f"Payment Plan with name: {name} and program: {payment_plan.program.name} already exists."
            )
        if payment_plan.is_population_finalized():
            msg = "Finalized Population Payment Plan can't be changed"
            logger.error(msg)
            raise ValidationError(msg)
        if name:
            payment_plan.name = name
        if vulnerability_score_min is not None:
            should_rebuild_stats = True
            payment_plan.vulnerability_score_min = vulnerability_score_min
        if vulnerability_score_max is not None:
            should_rebuild_stats = True
            payment_plan.vulnerability_score_max = vulnerability_score_max

        if program_cycle_id_encoded:
            program_cycle = get_object_or_404(ProgramCycle, pk=decode_id_string(program_cycle_id_encoded))
            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Payment Plan")
            payment_plan.program_cycle = program_cycle

        if targeting_criteria_input:
            should_rebuild_list = True
            TargetingCriteriaInputValidator.validate(targeting_criteria_input, program)
            targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
            if payment_plan.status == PaymentPlan.Status.TP_OPEN:
                if payment_plan.targeting_criteria:
                    payment_plan.targeting_criteria.delete()
                payment_plan.targeting_criteria = targeting_criteria
        if excluded_ids is not None:
            should_rebuild_list = True
            payment_plan.excluded_ids = excluded_ids
        if exclusion_reason is not None:
            should_rebuild_list = True
            payment_plan.exclusion_reason = exclusion_reason
        payment_plan.save()
        # prevent race between commit transaction and using in task
        transaction.on_commit(
            lambda: cls.rebuild_pp_population(should_rebuild_list, should_rebuild_stats, payment_plan)
        )
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_plan.program, "pk", None),
            old_payment_plan,
            payment_plan,
        )
        return cls(payment_plan=payment_plan)

    @classmethod
    def rebuild_pp_population(
        cls, should_rebuild_list: bool, should_rebuild_stats: bool, payment_plan: PaymentPlan
    ) -> None:
        rebuild_list = payment_plan.is_population_open() and should_rebuild_list
        rebuild_stats = (not rebuild_list and should_rebuild_list) or should_rebuild_stats
        if rebuild_list or rebuild_stats:
            payment_plan.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
            payment_plan.save()
        if rebuild_list:
            payment_plan_full_rebuild.delay(payment_plan.id)
        if rebuild_stats and not rebuild_list:
            payment_plan_rebuild_stats.delay(payment_plan.id)

    @classmethod
    def validate_statuses(
        cls,
        name: str,
        payment_plan: PaymentPlan,
        targeting_criteria_input: Dict,
        vulnerability_score_max: int,
        vulnerability_score_min: int,
    ) -> None:
        if not payment_plan.is_population_locked() and (
            vulnerability_score_min is not None or vulnerability_score_max is not None
        ):
            raise ValidationError(
                "You can only set vulnerability_score_min and vulnerability_score_max on Locked Payment Plan"
            )
        if payment_plan.is_population_locked() and name:
            raise ValidationError("Name can't be changed when Payment Plan is in Locked status")
        if payment_plan.is_population_finalized():
            raise ValidationError("Finalized Population Payment Plan can't be changed")
        if targeting_criteria_input and not payment_plan.is_population_open():
            raise ValidationError("Locked Population Payment Plan can't be changed")

    @classmethod
    def get_object_required(cls, id: str) -> PaymentPlan:
        return get_object_or_404(PaymentPlan, id=decode_id_string(id))

    @classmethod
    def get_object(cls, id: Optional[str]) -> Optional[PaymentPlan]:
        if id is None:
            return None
        return cls.get_object_required(id)


class LockTargetPopulationMutation(ValidatedMutation):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)
    object_validators = [LockTargetPopulationValidator]
    model_class = PaymentPlan
    permissions = [Permissions.TARGETING_LOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "LockTargetPopulationMutation":
        payment_plan = kwargs.get("model_object")
        if payment_plan.status != PaymentPlan.Status.TP_OPEN:
            raise ValidationError("You can only lock population for open population Payment Plan")
        old_target_population = kwargs.get("old_model_object")
        payment_plan.status = PaymentPlan.Status.TP_LOCKED
        payment_plan.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
        payment_plan.save()
        transaction.on_commit(lambda: payment_plan_rebuild_stats.delay(payment_plan.id))
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_plan.program_cycle.program, "pk", None),
            old_target_population,
            payment_plan,
        )
        return cls(payment_plan=payment_plan)


class UnlockTargetPopulationMutation(ValidatedMutation):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)
    object_validators = [UnlockTargetPopulationValidator]
    model_class = PaymentPlan
    permissions = [Permissions.TARGETING_UNLOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @raise_program_status_is(Program.FINISHED)
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "UnlockTargetPopulationMutation":
        payment_plan = kwargs.get("model_object")
        old_target_population = kwargs.get("old_model_object")
        payment_plan.status = PaymentPlan.Status.TP_OPEN
        payment_plan.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
        payment_plan.save()
        transaction.on_commit(lambda: payment_plan_rebuild_stats.delay(payment_plan.id))
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_plan.program_cycle.program, "pk", None),
            old_target_population,
            payment_plan,
        )
        return cls(payment_plan=payment_plan)


class CopyTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)
    validation_errors = graphene.Field(Arg)

    class Input:
        payment_plan_data = CopyTargetPopulationInput()

    @classmethod
    @is_authenticated
    @raise_program_status_is(Program.FINISHED)
    @transaction.atomic
    def mutate_and_get_payload(cls, _root: Any, info: Any, **kwargs: Any) -> "CopyTargetPopulationMutation":
        try:
            user = info.context.user
            payment_plan_data = kwargs["payment_plan_data"]
            name = payment_plan_data.pop("name").strip()
            payment_plan_id = decode_id_string(payment_plan_data.pop("id"))
            payment_plan = get_object_or_404(PaymentPlan, pk=payment_plan_id)
            program_cycle = get_object_or_404(
                ProgramCycle, pk=decode_id_string(payment_plan_data.get("program_cycle_id"))
            )
            program = program_cycle.program

            if program_cycle.status == ProgramCycle.FINISHED:
                raise ValidationError("Not possible to assign Finished Program Cycle to Targeting")

            cls.has_permission(info, Permissions.TARGETING_DUPLICATE, payment_plan.business_area)

            if PaymentPlan.objects.filter(name=name, program_cycle=program_cycle, is_removed=False).exists():
                raise ValidationError(
                    f"Payment Plan with name: {name} and program cycle: {program_cycle.title} already exists."
                )

            payment_plan_copy = PaymentPlan(
                name=name,
                created_by=user,
                business_area=payment_plan.business_area,
                status=PaymentPlan.Status.TP_OPEN,
                male_children_count=payment_plan.male_children_count,
                female_children_count=payment_plan.female_children_count,
                male_adults_count=payment_plan.male_adults_count,
                female_adults_count=payment_plan.female_adults_count,
                total_households_count=payment_plan.total_households_count,
                total_individuals_count=payment_plan.total_individuals_count,
                steficon_rule_targeting=payment_plan.steficon_rule_targeting,
                steficon_targeting_applied_date=payment_plan.steficon_targeting_applied_date,
                program=program,
                program_cycle=program_cycle,
            )
            payment_plan_copy.save()
            if payment_plan.targeting_criteria:
                payment_plan_copy.targeting_criteria = cls.copy_target_criteria(payment_plan.targeting_criteria)
            payment_plan_copy.save()
            payment_plan_copy.refresh_from_db()
            transaction.on_commit(lambda: payment_plan_full_rebuild.delay(payment_plan_copy.id))
            log_create(
                PaymentPlan.ACTIVITY_LOG_MAPPING,
                "business_area",
                info.context.user,
                getattr(program, "pk", None),
                None,
                payment_plan_copy,
            )
            return CopyTargetPopulationMutation(payment_plan_copy)
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
            rule_copy = TargetingCriteriaRule(
                targeting_criteria=targeting_criteria_copy,
                household_ids=rule.household_ids,
                individual_ids=rule.individual_ids,
            )
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

            for col_filter_block in rule.collectors_filters_blocks.all():
                col_filter_block_copy = TargetingCollectorRuleFilterBlock(targeting_criteria_rule=rule_copy)
                col_filter_block_copy.save()
                for col_filter in col_filter_block.collector_block_filters.all():
                    col_filter.pk = None
                    col_filter.collector_block_filters = col_filter_block_copy
                    col_filter.save()
        # TODO: will remove after refactoring
        targeting_criteria_copy.household_ids = targeting_criteria.household_ids
        targeting_criteria_copy.individual_ids = targeting_criteria.individual_ids
        targeting_criteria_copy.save()

        return targeting_criteria_copy


class SetSteficonRuleOnTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(PaymentPlanNode)

    class Input:
        payment_plan_id = graphene.GlobalID(
            required=True,
            node=PaymentPlanNode,
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
        payment_plan_id = utils.decode_id_string(kwargs["payment_plan_id"])
        payment_plan = get_object_or_404(PaymentPlan, pk=payment_plan_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_plan)
        old_payment_plan = PaymentPlan.objects.get(id=payment_plan_id)
        cls.has_permission(_info, Permissions.TARGETING_UPDATE, payment_plan.business_area)

        encoded_steficon_rule_id = kwargs.get("steficon_rule_id")
        if encoded_steficon_rule_id is not None:
            steficon_rule_id = utils.decode_id_string(encoded_steficon_rule_id)
            steficon_rule = get_object_or_404(Rule, id=steficon_rule_id)
            steficon_rule_commit = steficon_rule.latest
            if not steficon_rule.enabled or steficon_rule.deprecated:
                raise ValidationError("This steficon rule is not enabled or is deprecated.")
            payment_plan.steficon_rule_targeting = steficon_rule_commit
            payment_plan.status = PaymentPlan.Status.TP_STEFICON_WAIT
            payment_plan.save()
            payment_plan_apply_steficon_hh_selection.delay(payment_plan.pk)
        else:
            payment_plan.steficon_rule_targeting = None
            payment_plan.vulnerability_score_min = None
            payment_plan.vulnerability_score_max = None
            payment_plan.save()
            # TODO: remove this one ??
            # for selection in HouseholdSelection.objects.filter(target_population=payment_plan):
            #     selection.vulnerability_score = None
            #     selection.save(update_fields=["vulnerability_score"])
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            _info.context.user,
            getattr(payment_plan.program_cycle.program, "pk", None),
            old_payment_plan,
            payment_plan,
        )
        return SetSteficonRuleOnTargetPopulationMutation(payment_plan=payment_plan)


class RebuildTargetPopulationMutation(ValidatedMutation):
    # TODO: rename and move it into Payment app?
    payment_plan = graphene.Field(TargetPopulationNode)
    object_validators = [RebuildTargetPopulationValidator]
    model_class = PaymentPlan
    permissions = [Permissions.TARGETING_UPDATE]

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def validated_mutate(cls, root: Any, info: Any, **kwargs: Any) -> "RebuildTargetPopulationMutation":
        payment_plan = kwargs.get("model_object")
        old_payment_plan = kwargs.get("old_model_object")
        payment_plan.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
        payment_plan.save()
        transaction.on_commit(lambda: payment_plan_full_rebuild.delay(payment_plan.id))
        log_create(
            PaymentPlan.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            getattr(payment_plan.program_cycle.program, "pk", None),
            old_payment_plan,
            payment_plan,
        )
        return cls(payment_plan=payment_plan)


class Mutations(graphene.ObjectType):
    create_target_population = CreateTargetPopulationMutation.Field()
    update_target_population = UpdateTargetPopulationMutation.Field()
    copy_target_population = CopyTargetPopulationMutation.Field()
    lock_target_population = LockTargetPopulationMutation.Field()
    unlock_target_population = UnlockTargetPopulationMutation.Field()
    set_steficon_rule_on_target_population = SetSteficonRuleOnTargetPopulationMutation.Field()
    target_population_rebuild = RebuildTargetPopulationMutation.Field()
