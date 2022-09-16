from django.db import transaction

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.permissions import is_authenticated

from .inputs import CreateCommunicationMessageInput
from .models import Message
from .schema import CommunicationMessageNode
from .services.message_crud_services import MessageCrudServices


class CreateCommunicationMessageMutation(PermissionMutation):
    message = graphene.Field(CommunicationMessageNode)

    class Arguments:
        business_area_slug = graphene.String(required=True)
        inputs = CreateCommunicationMessageInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, business_area_slug, inputs):
        cls.has_permission(info, Permissions.COMMUNICATION_MESSAGE_VIEW_CREATE, business_area_slug)
        new_message = MessageCrudServices.create(info.context.user, business_area_slug, inputs)
        log_create(
            Message.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            new_message,
        )
        return cls(message=new_message)


class Mutations(graphene.ObjectType):
    create_communication_message = CreateCommunicationMessageMutation.Field()
