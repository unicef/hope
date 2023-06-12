from functools import partial
from typing import Any, Dict

from django.db import transaction
from django.shortcuts import get_object_or_404

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.accountability.celery_tasks import (
    export_survey_sample_task,
    send_survey_to_users,
)
from hct_mis_api.apps.accountability.inputs import (
    CreateAccountabilityCommunicationMessageInput,
    CreateFeedbackInput,
    CreateFeedbackMessageInput,
    CreateSurveyInput,
    UpdateFeedbackInput,
)
from hct_mis_api.apps.accountability.models import (
    Feedback,
    FeedbackMessage,
    Message,
    Survey,
)
from hct_mis_api.apps.accountability.nodes import (
    CommunicationMessageNode,
    FeedbackMessageNode,
    FeedbackNode,
    SurveyNode,
)
from hct_mis_api.apps.accountability.services.feedback_crud_services import (
    FeedbackCrudServices,
)
from hct_mis_api.apps.accountability.services.message_crud_services import (
    MessageCrudServices,
)
from hct_mis_api.apps.accountability.services.survey_crud_services import (
    SurveyCrudServices,
)
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string


class CreateCommunicationMessageMutation(PermissionMutation):
    message = graphene.Field(CommunicationMessageNode)

    class Arguments:
        input = CreateAccountabilityCommunicationMessageInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict[str, Any]) -> "CreateCommunicationMessageMutation":
        user = info.context.user
        business_area_slug = info.context.headers.get("Business-Area")
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.has_permission(info, Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE, business_area)
        message = MessageCrudServices.create(user, business_area, input)
        log_create(Message.ACTIVITY_LOG_MAPPING, "business_area", user, None, message)
        return cls(message=message)


class CreateFeedbackMutation(PermissionMutation):
    feedback = graphene.Field(FeedbackNode)

    class Arguments:
        input = CreateFeedbackInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict[str, Any]) -> "CreateFeedbackMutation":
        user = info.context.user
        business_area_slug = info.context.headers.get("Business-Area")
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_CREATE, business_area)
        feedback = FeedbackCrudServices.create(user, business_area, input)
        log_create(Feedback.ACTIVITY_LOG_MAPPING, "business_area", user, None, feedback)
        return cls(feedback=feedback)


class UpdateFeedbackMutation(PermissionMutation):
    feedback = graphene.Field(FeedbackNode)

    class Arguments:
        input = UpdateFeedbackInput(required=True)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root: Any, info: Any, input: Dict[str, Any]) -> "UpdateFeedbackMutation":
        user = info.context.user
        old_feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback_id"]))
        feedback = get_object_or_404(Feedback, id=decode_id_string(input["feedback_id"]))

        cls.has_permission(info, Permissions.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE, feedback.business_area.slug)
        updated_feedback = FeedbackCrudServices.update(feedback, input)
        log_create(
            Feedback.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
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
    def mutate(cls, root: Any, info: Any, input: Dict[str, Any]) -> "CreateFeedbackMessageMutation":
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
    def mutate(cls, root: Any, info: Any, input: Dict[str, Any]) -> "CreateSurveyMutation":
        business_area_slug = info.context.headers.get("Business-Area")
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.has_permission(info, Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE, business_area)
        survey = SurveyCrudServices.create(info.context.user, business_area, input)
        transaction.on_commit(partial(send_survey_to_users.delay, survey.id, input["flow"], business_area.id))
        log_create(
            Survey.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            None,
            survey,
        )
        return cls(survey=survey)


class ExportSurveySampleMutationMutation(PermissionMutation):
    survey = graphene.Field(SurveyNode)

    class Arguments:
        survey_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, survey_id: str) -> "ExportSurveySampleMutationMutation":
        survey = get_object_or_404(Survey, id=decode_id_string(survey_id))
        cls.has_permission(info, Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS, survey.business_area)

        export_survey_sample_task.delay(survey.id, info.context.user.id)
        return cls(survey=survey)


class Mutations(graphene.ObjectType):
    create_accountability_communication_message = CreateCommunicationMessageMutation.Field()
    create_feedback = CreateFeedbackMutation.Field()
    update_feedback = UpdateFeedbackMutation.Field()
    create_feedback_message = CreateFeedbackMessageMutation.Field()
    create_survey = CreateSurveyMutation.Field()
    export_survey_sample = ExportSurveySampleMutationMutation.Field()
