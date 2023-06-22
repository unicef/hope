from typing import Any, Optional

from django.conf import settings

import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.accountability.models import (
    Feedback,
    FeedbackMessage,
    Message,
    SampleFileExpiredException,
    Survey,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.household.models import Household


class RapidProFlowNode(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()

    def resolve_id(parent, info: Any) -> str:
        return parent["uuid"]  # type: ignore


class CommunicationMessageRecipientMapNode(BaseNodePermissionMixin, DjangoObjectType):
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


class GetCommunicationMessageSampleSizeNode(BaseNodePermissionMixin, graphene.ObjectType):
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
    rapid_pro_url = graphene.String()

    class Meta:
        model = Survey
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection
        filter_fields = []

    @staticmethod
    def resolve_sample_file_path(survey: Survey, info: Any) -> Optional[str]:
        try:
            return survey.sample_file_path()
        except SampleFileExpiredException:
            return None

    @staticmethod
    def resolve_has_valid_sample_file(survey: Survey, info: Any) -> bool:
        return survey.has_valid_sample_file()

    @staticmethod
    def resolve_rapid_pro_url(survey: Survey, info: Any) -> Optional[str]:
        if not survey.flow_id:
            return None
        return f"{settings.RAPID_PRO_URL}/flow/results/{survey.flow_id}/"


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


class AccountabilitySampleSizeNode(graphene.ObjectType):
    number_of_recipients = graphene.Int()
    sample_size = graphene.Int()
