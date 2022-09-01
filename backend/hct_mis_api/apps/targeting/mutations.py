import logging
import graphene

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphql import GraphQLError

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
from hct_mis_api.apps.mis_datahub.celery_tasks import send_target_population_task
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.steficon.schema import SteficonRuleNode
from hct_mis_api.apps.targeting.models import (
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetingIndividualBlockRuleFilter,
    TargetingIndividualRuleFilterBlock,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.schema import (
    TargetingCriteriaObjectType,
    TargetPopulationNode,
)
from hct_mis_api.apps.targeting.validators import (
    ApproveTargetPopulationValidator,
    FinalizeTargetPopulationValidator,
    TargetingCriteriaInputValidator,
    TargetValidator,
    UnapproveTargetPopulationValidator,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin
from hct_mis_api.apps.utils.schema import Arg
from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon

logger = logging.getLogger(__name__)


class CopyTargetPopulationInput(graphene.InputObjectType):
    """All attribute inputs to create a new entry."""

    id = graphene.ID()
    name = graphene.String()


class ValidatedMutation(PermissionMutation):
    arguments_validators = []
    object_validators = []
    permissions = None

    model_class = None

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        for validator in cls.arguments_validators:
            validator.validate(kwargs)
        model_object = cls.get_object(root, info, **kwargs)
        check_concurrency_version_in_mutation(kwargs.get("version"), model_object)
        old_model_object = cls.get_object(root, info, **kwargs)
        if cls.permissions:
            cls.has_permission(info, cls.permissions, model_object.business_area)
        return cls.validated_mutate(root, info, model_object=model_object, old_model_object=old_model_object, **kwargs)

    @classmethod
    def get_object(cls, root, info, **kwargs):
        id = kwargs.get("id")
        if id is None:
            return None
        object = get_object_or_404(cls.model_class, id=decode_id_string(id))
        for validator in cls.object_validators:
            validator.validate(object)
        return object


class UpdateTargetPopulationInput(graphene.InputObjectType):

    id = graphene.ID(required=True)
    name = graphene.String()
    targeting_criteria = TargetingCriteriaObjectType()
    program_id = graphene.ID()
    vulnerability_score_min = graphene.Decimal()
    vulnerability_score_max = graphene.Decimal()
    excluded_ids = graphene.String()
    exclusion_reason = graphene.String()


class CreateTargetPopulationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    targeting_criteria = TargetingCriteriaObjectType(required=True)
    business_area_slug = graphene.String(required=True)
    program_id = graphene.ID(required=True)
    excluded_ids = graphene.String(required=True)
    exclusion_reason = graphene.String()


def from_input_to_targeting_criteria(targeting_criteria_input, program: Program):
    targeting_criteria = TargetingCriteria()
    targeting_criteria.save()
    for rule_input in targeting_criteria_input.get("rules"):
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        for filter_input in rule_input.get("filters", []):
            rule_filter = TargetingCriteriaRuleFilter(targeting_criteria_rule=rule, **filter_input)
            rule_filter.save()
        for block_input in rule_input.get("individuals_filters_blocks", []):
            block = TargetingIndividualRuleFilterBlock(
                targeting_criteria_rule=rule, target_only_hoh=not program.individual_data_needed
            )
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
    def processed_mutate(cls, root, info, **kwargs):
        user = info.context.user
        input = kwargs.pop("input")
        program = get_object_or_404(Program, pk=decode_id_string(input.get("program_id")))

        cls.has_permission(info, Permissions.TARGETING_CREATE, program.business_area)

        if program.status != Program.ACTIVE:
            logger.error("Only Active program can be assigned to Targeting")
            raise ValidationError("Only Active program can be assigned to Targeting")

        targeting_criteria_input = input.get("targeting_criteria")

        business_area = BusinessArea.objects.get(slug=input.pop("business_area_slug"))
        TargetingCriteriaInputValidator.validate(targeting_criteria_input)
        targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, program)
        target_population = TargetPopulation(
            name=input.get("name"),
            created_by=user,
            business_area=business_area,
            excluded_ids=input.get("excluded_ids"),
            exclusion_reason=input.get("exclusion_reason", ""),
        )
        target_population.candidate_list_targeting_criteria = targeting_criteria
        target_population.program = program
        target_population.full_clean()
        target_population.save()
        log_create(TargetPopulation.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, target_population)
        return cls(target_population=target_population)


class UpdateTargetPopulationMutation(PermissionMutation, ValidationErrorMutationMixin):
    target_population = graphene.Field(TargetPopulationNode)

    class Arguments:
        input = UpdateTargetPopulationInput(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def processed_mutate(cls, root, info, **kwargs):
        input = kwargs.get("input")
        id = input.get("id")
        target_population = cls.get_object(id)
        check_concurrency_version_in_mutation(kwargs.get("version"), target_population)
        old_target_population = cls.get_object(id)

        cls.has_permission(info, Permissions.TARGETING_UPDATE, target_population.business_area)

        name = input.get("name")
        program_id_encoded = input.get("program_id")
        vulnerability_score_min = input.get("vulnerability_score_min")
        vulnerability_score_max = input.get("vulnerability_score_max")
        excluded_ids = input.get("excluded_ids")
        exclusion_reason = input.get("exclusion_reason")
        if not target_population.is_approved() and (
            vulnerability_score_min is not None or vulnerability_score_max is not None
        ):
            logger.error(
                "You can only set vulnerability_score_min and vulnerability_score_max on APPROVED Target Population"
            )
            raise ValidationError(
                "You can only set vulnerability_score_min and vulnerability_score_max on APPROVED Target Population"
            )
        if vulnerability_score_min is not None:
            target_population.vulnerability_score_min = vulnerability_score_min
        if vulnerability_score_max is not None:
            target_population.vulnerability_score_max = vulnerability_score_max

        if target_population.is_locked() and name:
            logger.error("Name can't be changed when Target Population is in APPROVED status")
            raise ValidationError("Name can't be changed when Target Population is in APPROVED status")
        if target_population.is_finalized():
            logger.error("Finalized Target Population can't be changed")
            raise ValidationError("Finalized Target Population can't be changed")
        if target_population.status == TargetPopulation.STATUS_ASSIGNED:
            logger.error("Assigned Target Population can't be changed")
            raise ValidationError("Assigned Target Population can't be changed")
        if name:
            target_population.name = name
        if program_id_encoded:
            program = get_object_or_404(Program, pk=decode_id_string(program_id_encoded))
            target_population.program = program
        targeting_criteria_input = input.get("targeting_criteria")
        if targeting_criteria_input is not None:
            TargetingCriteriaInputValidator.validate(targeting_criteria_input)
        if targeting_criteria_input:
            targeting_criteria = from_input_to_targeting_criteria(targeting_criteria_input, target_population.program)
            if target_population.status == TargetPopulation.STATUS_DRAFT:
                if target_population.candidate_list_targeting_criteria:
                    target_population.candidate_list_targeting_criteria.delete()
                target_population.candidate_list_targeting_criteria = targeting_criteria
            elif target_population.status == TargetPopulation.STATUS_LOCKED:
                if target_population.final_list_targeting_criteria:
                    target_population.final_list_targeting_criteria.delete()
                target_population.final_list_targeting_criteria = targeting_criteria
        if excluded_ids is not None:
            target_population.excluded_ids = excluded_ids
        if exclusion_reason is not None:
            target_population.exclusion_reason = exclusion_reason
        target_population.full_clean()
        target_population.save()
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)

    @classmethod
    def get_object(cls, id):
        if id is None:
            return None
        object = get_object_or_404(TargetPopulation, id=decode_id_string(id))
        return object


class ApproveTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [ApproveTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_LOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    def validated_mutate(cls, root, info, **kwargs):
        user = info.context.user
        target_population = kwargs.get("model_object")
        if target_population.status != TargetPopulation.STATUS_DRAFT:
            logger.error("You can only lock open target population")
            raise ValidationError("You can only lock open target population")
        old_target_population = kwargs.get("old_model_object")
        target_population.status = TargetPopulation.STATUS_LOCKED
        target_population.changed_by = user
        target_population.change_date = timezone.now()
        target_population.apply_criteria_query()
        target_population.save()
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class UnapproveTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [UnapproveTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_UNLOCK]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validated_mutate(cls, root, info, **kwargs):
        target_population = kwargs.get("model_object")
        old_target_population = kwargs.get("old_model_object")
        target_population.status = TargetPopulation.STATUS_DRAFT
        target_population.save()
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_target_population,
            target_population,
        )
        return cls(target_population=target_population)


class FinalizeTargetPopulationMutation(ValidatedMutation):
    target_population = graphene.Field(TargetPopulationNode)
    object_validators = [FinalizeTargetPopulationValidator]
    model_class = TargetPopulation
    permissions = [Permissions.TARGETING_SEND]

    class Arguments:
        id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def validated_mutate(cls, root, info, **kwargs):
        user = info.context.user
        old_target_population = kwargs.get("old_model_object")
        target_population: TargetPopulation = kwargs.get("model_object")
        if target_population.program.business_area.is_payment_plan_applicable:
            with transaction.atomic():
                target_population.status = TargetPopulation.STATUS_READY
                target_population.finalized_by = user
                target_population.finalized_at = timezone.now()
                target_population.save()
        else:
            with transaction.atomic():
                target_population.status = TargetPopulation.STATUS_PROCESSING
                target_population.finalized_by = user
                target_population.finalized_at = timezone.now()
                if target_population.final_list_targeting_criteria:
                    """Gets all households from candidate list which
                    don't meet final_list_targeting_criteria and set them (HouseholdSelection m2m model)
                    final=False (final list is candidate list filtered by final=True"""
                    households_ids_queryset = target_population.households.filter(
                        ~Q(target_population.final_list_targeting_criteria.get_query())
                    ).values_list("id")
                    HouseholdSelection.objects.filter(
                        household__id__in=households_ids_queryset,
                        target_population=target_population,
                    ).update(final=False)

                HouseholdSelection.objects.filter(target_population=target_population,).exclude(
                    household__id__in=target_population.vulnerability_score_filtered_households.values_list("id")
                ).update(final=False)

                target_population.save()
            send_target_population_task.delay(target_population.id)
        log_create(
            TargetPopulation.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
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
    @transaction.atomic
    def mutate_and_get_payload(cls, _root, info, **kwargs):
        try:
            user = info.context.user
            target_population_data = kwargs["target_population_data"]
            name = target_population_data.pop("name")
            target_id = utils.decode_id_string(target_population_data.pop("id"))
            target_population = TargetPopulation.objects.get(id=target_id)

            cls.has_permission(info, Permissions.TARGETING_DUPLICATE, target_population.business_area)

            target_population_copy = TargetPopulation(
                name=name,
                created_by=user,
                business_area=target_population.business_area,
                status=TargetPopulation.STATUS_DRAFT,
                candidate_list_total_households=target_population.candidate_list_total_households,
                candidate_list_total_individuals=target_population.candidate_list_total_individuals,
                steficon_rule=target_population.steficon_rule,
                steficon_applied_date=target_population.steficon_applied_date,
                program=target_population.program,
            )
            target_population_copy.full_clean()
            target_population_copy.save()
            if target_population.candidate_list_targeting_criteria:
                target_population_copy.candidate_list_targeting_criteria = cls.copy_target_criteria(
                    target_population.candidate_list_targeting_criteria
                )
            target_population_copy.full_clean()
            target_population_copy.save()
            target_population_copy.refresh_from_db()
            log_create(
                TargetPopulation.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, None, target_population
            )
            return CopyTargetPopulationMutation(target_population_copy)
        except ValidationError as e:
            logger.exception(e)
            return cls(validation_errors=e.message_dict)

    @classmethod
    def copy_target_criteria(cls, targeting_criteria):
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

        return targeting_criteria_copy


class DeleteTargetPopulationMutation(PermissionRelayMutation, TargetValidator):
    ok = graphene.Boolean()

    class Input:
        target_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate_and_get_payload(cls, _root, _info, **kwargs):
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
    def mutate_and_get_payload(cls, _root, _info, **kwargs):
        target_id = utils.decode_id_string(kwargs["target_id"])
        target_population = TargetPopulation.objects.get(id=target_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), target_population)
        old_target_population = TargetPopulation.objects.get(id=target_id)
        cls.has_permission(_info, Permissions.TARGETING_UPDATE, target_population.business_area)

        encoded_steficon_rule_id = kwargs.get("steficon_rule_id")
        if encoded_steficon_rule_id is not None:
            steficon_rule_id = utils.decode_id_string(encoded_steficon_rule_id)
            if target_population.allowed_steficon_rule is not None and steficon_rule_id != str(
                target_population.allowed_steficon_rule.id
            ):
                logger.error(
                    "Another formula was applied to a previous target population for this programme. You can only apply the same formula"
                )
                raise GraphQLError(
                    "Another formula was applied to a previous target population for this programme. You can only apply the same formula"
                )
            steficon_rule = get_object_or_404(Rule, id=steficon_rule_id)
            steficon_rule_commit = steficon_rule.latest
            if not steficon_rule.enabled or steficon_rule.deprecated:
                logger.error("This steficon rule is not enabled or is deprecated.")
                raise GraphQLError("This steficon rule is not enabled or is deprecated.")
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
            old_target_population,
            target_population,
        )
        return SetSteficonRuleOnTargetPopulationMutation(target_population=target_population)


class Mutations(graphene.ObjectType):
    create_target_population = CreateTargetPopulationMutation.Field()
    update_target_population = UpdateTargetPopulationMutation.Field()
    copy_target_population = CopyTargetPopulationMutation.Field()
    delete_target_population = DeleteTargetPopulationMutation.Field()
    approve_target_population = ApproveTargetPopulationMutation.Field()
    unapprove_target_population = UnapproveTargetPopulationMutation.Field()
    finalize_target_population = FinalizeTargetPopulationMutation.Field()
    set_steficon_rule_on_target_population = SetSteficonRuleOnTargetPopulationMutation.Field()
