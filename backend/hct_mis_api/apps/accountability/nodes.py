from typing import Any, Optional

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
