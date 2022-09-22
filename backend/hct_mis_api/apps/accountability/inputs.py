import graphene

from .models import Message


class AccountabilityCommunicationMessageFullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AccountabilityCommunicationMessageAgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class AccountabilityCommunicationMessageRandomSamplingArguments(AccountabilityCommunicationMessageFullListArguments):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    age = AccountabilityCommunicationMessageAgeInput()
    sex = graphene.String()


class GetAccountabilityCommunicationMessageSampleSizeInput(graphene.InputObjectType):
    households = graphene.List(graphene.String)
    target_population = graphene.String()
    registration_data_import = graphene.String()
    sampling_type = graphene.Enum.from_enum(Message.SamplingChoices)(required=True)
    full_list_arguments = AccountabilityCommunicationMessageFullListArguments()
    random_sampling_arguments = AccountabilityCommunicationMessageRandomSamplingArguments()


class CreateAccountabilityCommunicationMessageInput(GetAccountabilityCommunicationMessageSampleSizeInput):
    title = graphene.String(required=True)
    body = graphene.String(required=True)


class CreateFeedbackInput(graphene.InputObjectType):
    business_area_slug = graphene.String(required=True)
    issue_type = graphene.String(required=True)
