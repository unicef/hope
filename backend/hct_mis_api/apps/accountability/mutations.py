from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.utils import decode_id_string

from .inputs import CreateAccountabilityCommunicationMessageInput, CreateFeedbackInput, UpdateFeedbackInput
from .models import Message
from .schema import CommunicationMessageNode, FeedbackNode
from .services.message_crud_services import MessageCrudServices
from .services.feedback_crud_services import FeedbackCrudServices


class CreateCommunicationMessageMutation(PermissionMutation):
    message = graphene.Field(CommunicationMessageNode)

    class Arguments:
        business_area_slug = graphene.String(required=True)
        inputs = CreateAccountabilityCommunicationMessageInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, business_area_slug, inputs):
        cls.has_permission(info, Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE, business_area_slug)
        new_message = MessageCrudServices.create(info.context.user, business_area_slug, inputs)
        log_create(
            Message.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            new_message,
        )
        return cls(message=new_message)


class CreateFeedbackMutation(PermissionMutation):
    feedback = graphene.Field(FeedbackNode)

    class Arguments:
        input = CreateFeedbackInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input):
        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_CREATE, input.get("business_area_slug"))
        new_feedback = FeedbackCrudServices.create(info.context.user, input)
        log_create(
            Message.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            new_feedback,
        )
        return cls(feedback=new_feedback)


class UpdateFeedbackMutation(PermissionMutation):
    feedback = graphene.Field(FeedbackNode)

    class Arguments:
        input = UpdateFeedbackInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input):
        feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback_id"]))
        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE, feedback.business_area.slug)
        updated_feedback = FeedbackCrudServices.update(feedback, input)
        log_create(
            Message.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            updated_feedback,
        )
        return cls(feedback=updated_feedback)


class Mutations(graphene.ObjectType):
    create_accountability_communication_message = CreateCommunicationMessageMutation.Field()
    create_feedback = CreateFeedbackMutation.Field()
    update_feedback = UpdateFeedbackMutation.Field()
