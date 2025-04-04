import graphene

from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.targeting.graphql_types import TargetingCriteriaObjectType


class FullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class RandomSamplingArguments(graphene.InputObjectType):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    excluded_admin_areas = graphene.List(graphene.String)
    age = AgeInput()
    sex = graphene.String()


class RapidProArguments(graphene.InputObjectType):
    flow_id = graphene.String(required=True)


class ManualArguments(graphene.InputObjectType):
    pass


class CreateUpdatePaymentVerificationPlan(graphene.InputObjectType):
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    business_area_slug = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()


class CreatePaymentVerificationInput(CreateUpdatePaymentVerificationPlan):
    cash_or_payment_plan_id = graphene.ID(required=True)


class EditPaymentVerificationInput(CreateUpdatePaymentVerificationPlan):
    payment_verification_plan_id = graphene.ID(required=True)


class GetCashplanVerificationSampleSizeInput(graphene.InputObjectType):
    cash_or_payment_plan_id = graphene.ID()
    payment_verification_plan_id = graphene.ID()
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    business_area_slug = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()


class ActionPaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    action = graphene.Enum.from_enum(PaymentPlan.Action)(required=True)
    comment = graphene.String()


class CreatePaymentPlanInput(graphene.InputObjectType):
    program_cycle_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    targeting_criteria = TargetingCriteriaObjectType(required=True)
    excluded_ids = graphene.String(required=True)
    exclusion_reason = graphene.String()
    fsp_id = graphene.ID(required=False)
    delivery_mechanism_code = graphene.String(required=False)


class OpenPaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    dispersion_start_date = graphene.Date(required=True)
    dispersion_end_date = graphene.Date(required=True)
    currency = graphene.String(required=True)


class UpdatePaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    dispersion_start_date = graphene.Date(required=False)
    dispersion_end_date = graphene.Date(required=False)
    currency = graphene.String(required=False)

    name = graphene.String()
    targeting_criteria = TargetingCriteriaObjectType()
    program_cycle_id = graphene.ID()
    vulnerability_score_min = graphene.Decimal()
    vulnerability_score_max = graphene.Decimal()
    excluded_ids = graphene.String()
    exclusion_reason = graphene.String()

    fsp_id = graphene.ID(required=False)
    delivery_mechanism_code = graphene.String(required=False)
