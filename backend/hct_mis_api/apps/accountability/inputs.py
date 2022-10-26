import graphene

from hct_mis_api.apps.accountability.models import Message


class AccountabilityFullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AccountabilityCommunicationMessageAgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class AccountabilityRandomSamplingArguments(AccountabilityFullListArguments):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    age = AccountabilityCommunicationMessageAgeInput()
    sex = graphene.String()


class GetAccountabilityCommunicationMessageSampleSizeInput(graphene.InputObjectType):
    households = graphene.List(graphene.ID)
    target_population = graphene.ID()
    registration_data_import = graphene.ID()
    sampling_type = graphene.Enum.from_enum(Message.SamplingChoices)(required=True)
    full_list_arguments = AccountabilityFullListArguments()
    random_sampling_arguments = AccountabilityRandomSamplingArguments()


class CreateAccountabilityCommunicationMessageInput(GetAccountabilityCommunicationMessageSampleSizeInput):
    title = graphene.String(required=True)
    body = graphene.String(required=True)


class CreateFeedbackInput(graphene.InputObjectType):
    business_area_slug = graphene.String(required=True)
    issue_type = graphene.String(required=True)
    household_lookup = graphene.ID()
    individual_lookup = graphene.ID()
    description = graphene.String(required=True)
    comments = graphene.String()
    admin2 = graphene.ID()
    area = graphene.String()
    language = graphene.String()
    consent = graphene.Boolean()
    program = graphene.ID()


class UpdateFeedbackInput(graphene.InputObjectType):
    feedback_id = graphene.ID(required=True)
    issue_type = graphene.String()
    household_lookup = graphene.ID()
    individual_lookup = graphene.ID()
    description = graphene.String()
    comments = graphene.String()
    admin2 = graphene.ID()
    area = graphene.String()
    language = graphene.String()
    consent = graphene.Boolean()
    program = graphene.ID()


class CreateSurveyInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    category = graphene.String(required=True)
    target_population = graphene.ID()
    program = graphene.ID()
    sampling_type = graphene.String(required=True)
    full_list_arguments = AccountabilityFullListArguments()
    random_sampling_arguments = AccountabilityRandomSamplingArguments()


class AccountabilitySampleSizeInput(graphene.InputObjectType):
    target_population = graphene.ID()
    program = graphene.ID()
    sampling_type = graphene.String(required=True)
    full_list_arguments = AccountabilityFullListArguments()
    random_sampling_arguments = AccountabilityRandomSamplingArguments()


class CreateFeedbackMessageInput(graphene.InputObjectType):
    from .schema import FeedbackMessageNode

    description = graphene.String(required=True)
    feedback = graphene.GlobalID(node=FeedbackMessageNode, required=True)
