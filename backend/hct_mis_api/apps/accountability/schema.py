import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.household.models import Household

from .filters import MessageRecipientsMapFilter, MessagesFilter, FeedbackFilter
from .inputs import GetAccountabilityCommunicationMessageSampleSizeInput
from .models import Feedback, Message, FeedbackMessage
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
        business_area_slug=graphene.String(required=True),
        inputs=GetAccountabilityCommunicationMessageSampleSizeInput(),
    )

    feedback = graphene.relay.Node.Field(FeedbackNode)
    all_feedbacks = DjangoPermissionFilterConnectionField(
        FeedbackNode,
        filterset_class=FeedbackFilter,
    )

    feedback_issue_type_choices = graphene.List(ChoiceObject)

    def resolve_feedback_issue_type_choices(self, info, **kwargs):
        return to_choice_object(Feedback.ISSUE_TYPE_CHOICES)

    def resolve_accountability_communication_message_sample_size(
        self, info, business_area_slug: str, inputs: dict, **kwargs
    ):
        verifier = MessageArgumentVerifier(inputs)
        verifier.verify()

        households = MessageCrudServices._get_households(inputs)

        sampling = Sampling(inputs, households)
        number_of_recipients, sample_size = sampling.generate_sampling(inputs.get("sampling_type"))

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }
