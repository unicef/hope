from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

import graphene

from hct_mis_api.apps.account.permissions import (
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
from hct_mis_api.apps.accountability.models import Feedback, Message, Survey
from hct_mis_api.apps.accountability.nodes import (
    AccountabilitySampleSizeNode,
    CommunicationMessageNode,
    CommunicationMessageRecipientMapNode,
    FeedbackNode,
    GetCommunicationMessageSampleSizeNode,
    RapidProFlowNode,
    RecipientNode,
    SurveyNode,
)
from hct_mis_api.apps.accountability.services.message_crud_services import (
    MessageCrudServices,
)
from hct_mis_api.apps.accountability.services.sampling import Sampling
from hct_mis_api.apps.accountability.services.verifiers import MessageArgumentVerifier
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    get_program_id_from_headers,
    to_choice_object,
)
from hct_mis_api.apps.grievance.utils import filter_feedback_based_on_partner_areas_2
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program


class Query(graphene.ObjectType):
    accountability_communication_message = graphene.relay.Node.Field(CommunicationMessageNode)
    all_accountability_communication_messages = DjangoPermissionFilterConnectionField(
        CommunicationMessageNode,
        filterset_class=MessagesFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
            ),
        ),
    )

    all_accountability_communication_message_recipients = DjangoPermissionFilterConnectionField(
        CommunicationMessageRecipientMapNode,
        filterset_class=MessageRecipientsMapFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
            ),
        ),
    )

    accountability_communication_message_sample_size = graphene.Field(
        GetCommunicationMessageSampleSizeNode,
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
        AccountabilitySampleSizeNode,
        input=AccountabilitySampleSizeInput(),
    )
    survey_category_choices = graphene.List(ChoiceObject)
    survey_available_flows = graphene.List(RapidProFlowNode)

    def resolve_all_accountability_communication_messages(self, info: Any, **kwargs: Any) -> QuerySet[Message]:
        business_area_slug = info.context.headers.get("Business-Area")
        return Message.objects.filter(business_area__slug=business_area_slug)

    def resolve_all_feedbacks(self, info: Any, **kwargs: Any) -> QuerySet[Feedback]:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")
        business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
        queryset = Feedback.objects.filter(business_area__slug=business_area_slug).select_related("admin2")

        if user.partner.has_area_limits_in_program(program_id):
            queryset = filter_feedback_based_on_partner_areas_2(
                queryset,
                user,
                business_area_id,
                program_id,
                [Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST, Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS],
            )

        return queryset

    def resolve_survey_category_choices(self, info: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(Survey.CATEGORY_CHOICES)

    def resolve_feedback_issue_type_choices(self, info: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(Feedback.ISSUE_TYPE_CHOICES)

    def resolve_accountability_communication_message_sample_size(self, info: Any, input: dict, **kwargs: Any) -> dict:
        verifier = MessageArgumentVerifier(input)
        verifier.verify()

        households = MessageCrudServices._get_households(input)

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }

    def resolve_accountability_sample_size(self, info: Any, input: dict, **kwargs: Any) -> dict:
        if payment_plan := input.get("payment_plan"):
            obj = get_object_or_404(PaymentPlan, id=decode_id_string(payment_plan))
            households = Household.objects.filter(payment__parent=obj)
        elif program := input.get("program"):
            obj = get_object_or_404(Program, id=decode_id_string(program))
            households = obj.households_with_payments_in_program
        else:
            raise ValidationError("Target population or program should be provided.")

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }

    def resolve_survey_available_flows(self, info: Any, *args: Any, **kwargs: Any) -> list:
        api = RapidProAPI(info.context.headers["Business-Area"], RapidProAPI.MODE_SURVEY)
        return api.get_flows()
