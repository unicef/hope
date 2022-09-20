import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection

from .filters import MessageRecipientsMapFilter, MessagesFilter
from .inputs import GetAccountabilityCommunicationMessageSampleSizeInput
from .models import Message
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
        model = Message.households.through
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []
        fields = (
            "id",
            "household",
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
