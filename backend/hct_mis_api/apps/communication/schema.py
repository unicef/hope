import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.household.models import Household

from .filters import MessageRecipientsMapFilter, MessagesFilter
from .inputs import GetCommunicationMessageSampleSizeInput
from .models import Message
from .services.message_crud_services import MessageCrudServices
from .services.sampling import Sampling
from .services.verifiers import MessageArgumentVerifier


class MessageRecipientMapNode(DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.COMMUNICATION_MESSAGE_VIEW_LIST,
            Permissions.COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
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


class MessageNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopeOneOfPermissionClass(
            Permissions.COMMUNICATION_MESSAGE_VIEW_LIST,
            Permissions.COMMUNICATION_MESSAGE_VIEW_DETAILS,
            Permissions.COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
        ),
    )

    class Meta:
        model = Message
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []
        fields = (
            "id",
            "unicef_id",
            "title",
            "body",
            "number_of_recipients",
            "sampling_type",
            "sample_size",
            "created_at",
            "created_by",
            "updated_at",
        )


class GetMessageSampleSizeObject(graphene.ObjectType):
    number_of_recipients = graphene.Int()
    sample_size = graphene.Int()


class Query(graphene.ObjectType):
    communication_message = graphene.relay.Node.Field(MessageNode)
    all_communication_messages = DjangoPermissionFilterConnectionField(
        MessageNode,
        filterset_class=MessagesFilter,
    )

    communication_message_recipient = graphene.relay.Node.Field(MessageRecipientMapNode)
    all_communication_message_recipients = DjangoPermissionFilterConnectionField(
        MessageRecipientMapNode,
        filterset_class=MessageRecipientsMapFilter,
    )

    communication_message_sample_size = graphene.Field(
        GetMessageSampleSizeObject,
        business_area_slug=graphene.String(required=True),
        inputs=GetCommunicationMessageSampleSizeInput(),
    )

    def resolve_communication_message_sample_size(self, info, business_area_slug: str, inputs: dict, **kwargs):
        verifier = MessageArgumentVerifier(inputs)
        verifier.verify()

        households = MessageCrudServices._get_households(inputs)

        sampling = Sampling(inputs, households)
        number_of_recipients, sample_size = sampling.generate_sampling(inputs.get("sampling_type"))

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }
