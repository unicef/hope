import graphene

from hct_mis_api.apps.payment.models import PaymentPlan


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
    # TODO: remove business_area_slug it comes from cycle.program
    business_area_slug = graphene.String(required=True)
    # TODO: remove TP id it comes from Cycle
    targeting_id = graphene.ID(required=True)
    dispersion_start_date = graphene.Date(required=True)
    dispersion_end_date = graphene.Date(required=True)
    currency = graphene.String(required=True)


class UpdatePaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    # TODO: remove TP id it comes from Cycle
    targeting_id = graphene.ID(required=False)
    dispersion_start_date = graphene.Date(required=False)
    dispersion_end_date = graphene.Date(required=False)
    currency = graphene.String(required=False)


class ChooseDeliveryMechanismsForPaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    delivery_mechanisms = graphene.List(graphene.String, required=True)


class FSPToDeliveryMechanismMappingInput(graphene.InputObjectType):
    fsp_id = graphene.ID(required=True)
    delivery_mechanism = graphene.String(required=True)
    chosen_configuration = graphene.String(required=False)
    order = graphene.Int(required=True)


class AssignFspToDeliveryMechanismInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    mappings = graphene.List(FSPToDeliveryMechanismMappingInput, required=True)


class AvailableFspsForDeliveryMechanismsInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
