from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.accountability.filters import (
    FeedbackFilter,
    MessageRecipientsMapFilter,
    MessagesFilter,
    RecipientFilter,
    SurveyFilter,
)
from hct_mis_api.apps.accountability.inputs import (
    AccountabilitySampleSizeInput,
    GetAccountabilityCommunicationMessageSampleSizeInput,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import decode_id_string, to_choice_object
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation

from .models import (
    Feedback,
    FeedbackMessage,
    Message,
    SampleFileExpiredException,
    Survey,
)
from .services.message_crud_services import MessageCrudServices
from .services.sampling import Sampling
from .services.verifiers import MessageArgumentVerifier


class CommunicationMessageRecipientMapNode(DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
        ),
    )

    class Meta:
        model = Household
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []
        fields = (
            "id",
            "size",
            "head_of_household",
        )


class CommunicationMessageNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
        ),
    )

    class Meta:
        model = Message
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []


class FeedbackMessageNode(DjangoObjectType):
    class Meta:
        model = FeedbackMessage
        exclude = ("feedback",)
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class FeedbackNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_LIST,
            Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_DETAILS,
        ),
    )

    class Meta:
        model = Feedback
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []


class GetCommunicationMessageSampleSizeObject(BaseNodePermissionMixin, graphene.ObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
        ),
    )

    number_of_recipients = graphene.Int()
    sample_size = graphene.Int()


class SurveyNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST,
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
        ),
    )

    sample_file_path = graphene.String()
    has_valid_sample_file = graphene.Boolean()

    class Meta:
        model = Survey
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []

    @staticmethod
    def resolve_sample_file_path(survey: Survey, info):
        try:
            return survey.sample_file_path()
        except SampleFileExpiredException:
            return None

    @staticmethod
    def resolve_has_valid_sample_file(survey: Survey, info):
        return survey.has_valid_sample_file()


class RecipientNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS,
        ),
    )

    class Meta:
        model = Household
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []
        fields = (
            "id",
            "size",
            "head_of_household",
        )


class AccountabilitySampleSizeObject(graphene.ObjectType):
    number_of_recipients = graphene.Int()
    sample_size = graphene.Int()


class Query(graphene.ObjectType):
    accountability_communication_message = graphene.relay.Node.Field(CommunicationMessageNode)
    all_accountability_communication_messages = DjangoPermissionFilterConnectionField(
        CommunicationMessageNode,
        filterset_class=MessagesFilter,
    )

    accountability_communication_message_recipient = graphene.relay.Node.Field(CommunicationMessageRecipientMapNode)
    all_accountability_communication_message_recipients = DjangoPermissionFilterConnectionField(
        CommunicationMessageRecipientMapNode,
        filterset_class=MessageRecipientsMapFilter,
    )

    accountability_communication_message_sample_size = graphene.Field(
        GetCommunicationMessageSampleSizeObject,
        input=GetAccountabilityCommunicationMessageSampleSizeInput(),
    )

    feedback = graphene.relay.Node.Field(FeedbackNode)
    all_feedbacks = DjangoPermissionFilterConnectionField(
        FeedbackNode,
        filterset_class=FeedbackFilter,
    )

    feedback_issue_type_choices = graphene.List(ChoiceObject)

    survey = graphene.relay.Node.Field(SurveyNode)
    all_surveys = DjangoPermissionFilterConnectionField(
        SurveyNode,
        filterset_class=SurveyFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST),),
    )
    recipients = DjangoPermissionFilterConnectionField(
        RecipientNode,
        filterset_class=RecipientFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS),),
    )
    accountability_sample_size = graphene.Field(
        AccountabilitySampleSizeObject,
        input=AccountabilitySampleSizeInput(),
    )

    def resolve_feedback_issue_type_choices(self, info, **kwargs):
        return to_choice_object(Feedback.ISSUE_TYPE_CHOICES)

    def resolve_accountability_communication_message_sample_size(self, info, input: dict, **kwargs):
        verifier = MessageArgumentVerifier(input)
        verifier.verify()

        households = MessageCrudServices._get_households(input)

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }

    def resolve_accountability_sample_size(self, info, input: dict, **kwargs):
        if target_population := input.get("target_population"):
            obj = get_object_or_404(TargetPopulation, id=decode_id_string(target_population))
            households = Household.objects.filter(target_populations=obj)
        elif program := input.get("program"):
            obj = get_object_or_404(Program, id=decode_id_string(program))
            households = Household.objects.filter(target_populations__program=obj)
        else:
            raise ValidationError("Target population or program should be provided.")

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }
