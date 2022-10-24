from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.accountability.inputs import (
    CreateAccountabilityCommunicationMessageInput,
    CreateFeedbackInput,
    CreateFeedbackMessageInput,
    CreateSurveyInput,
    UpdateFeedbackInput,
)
from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage, Survey
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string

from ..core.models import BusinessArea
from .models import Message
from .schema import (
    CommunicationMessageNode,
    FeedbackMessageNode,
    FeedbackNode,
    SurveyNode,
)
from .services.feedback_crud_services import FeedbackCrudServices
from .services.message_crud_services import MessageCrudServices
from .services.survey_crud_services import SurveyCrudServices


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
            Feedback.ACTIVITY_LOG_MAPPING,
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
        old_feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback_id"]))
        feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback_id"]))
        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE, feedback.business_area.slug)
        updated_feedback = FeedbackCrudServices.update(feedback, input)
        log_create(
            Feedback.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_feedback,
            updated_feedback,
        )
        return cls(feedback=updated_feedback)


class CreateFeedbackMessageMutation(PermissionMutation):
    feedback_message = graphene.Field(FeedbackMessageNode)

    class Arguments:
        input = CreateFeedbackMessageInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input):
        feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback"]))
        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_MESSAGE_VIEW_CREATE, feedback.business_area.slug)

        feedback_message = FeedbackMessage.objects.create(
            feedback=feedback, description=input["description"], created_by=info.context.user
        )
        return cls(feedback_message=feedback_message)


class CreateSurveyMutation(PermissionMutation):
    survey = graphene.Field(SurveyNode)

    class Arguments:
        input = CreateSurveyInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input):
        business_area_slug = info.context.META.get("Business-Area")
        business_area = BusinessArea.objects.get(slug=business_area_slug)
        cls.has_permission(info, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE, business_area)
        survey = SurveyCrudServices.create(info.context.user, business_area, input)
        log_create(
            Survey.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            survey,
        )
        return cls(survey=survey)


class Mutations(graphene.ObjectType):
    create_accountability_communication_message = CreateCommunicationMessageMutation.Field()
    create_feedback = CreateFeedbackMutation.Field()
    update_feedback = UpdateFeedbackMutation.Field()
    create_feedback_message = CreateFeedbackMessageMutation.Field()
    create_survey = CreateSurveyMutation.Field()
