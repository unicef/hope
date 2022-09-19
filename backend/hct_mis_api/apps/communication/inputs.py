import graphene

from .models import Message


class MessageFullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class MessageAgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class MessageRandomSamplingArguments(MessageFullListArguments):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    age = MessageAgeInput()
    sex = graphene.String()


class GetCommunicationMessageSampleSizeInput(graphene.InputObjectType):
    households = graphene.List(graphene.String)
    target_population = graphene.String()
    registration_data_import = graphene.String()
    sampling_type = graphene.Enum.from_enum(Message.SamplingChoices)(required=True)
    full_list_arguments = MessageFullListArguments()
    random_sampling_arguments = MessageRandomSamplingArguments()


class CreateCommunicationMessageInput(GetCommunicationMessageSampleSizeInput):
    title = graphene.String(required=True)
    body = graphene.String(required=True)
