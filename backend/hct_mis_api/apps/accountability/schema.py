from typing import Any, Dict, List

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
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import decode_id_string, to_choice_object
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation


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
    available_flows = graphene.List(RapidProFlowNode)

    def resolve_all_accountability_communication_messages(self, info: Any, **kwargs: Any) -> QuerySet[Message]:
        business_area_slug = info.context.headers.get("Business-Area")
        return Message.objects.filter(business_area__slug=business_area_slug)

    def resolve_all_feedback(self, info: Any, **kwargs: Any) -> QuerySet[Feedback]:
        business_area_slug = info.context.headers.get("Business-Area")
        return Feedback.objects.filter(business_area__slug=business_area_slug)

    def resolve_survey_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Survey.CATEGORY_CHOICES)

    def resolve_feedback_issue_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Feedback.ISSUE_TYPE_CHOICES)

    def resolve_accountability_communication_message_sample_size(self, info: Any, input: Dict, **kwargs: Any) -> Dict:
        verifier = MessageArgumentVerifier(input)
        verifier.verify()

        households = MessageCrudServices._get_households(input)

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }

    def resolve_accountability_sample_size(self, info: Any, input: Dict, **kwargs: Any) -> Dict:
        if target_population := input.get("target_population"):
            obj = get_object_or_404(TargetPopulation, id=decode_id_string(target_population))
            households = Household.objects.filter(target_populations=obj)
        elif program := input.get("program"):
            obj = get_object_or_404(Program, id=decode_id_string(program))
            households = Household.objects.filter(target_populations__program=obj)
        else:
            raise ValidationError("Target population or program should be provided.")

        sampling = Sampling(input, households)
        number_of_recipients, sample_size = sampling.generate_sampling()

        return {
            "number_of_recipients": number_of_recipients,
            "sample_size": sample_size,
        }

    def resolve_available_flows(self, info: Any, *args: Any, **kwargs: Any) -> List:
        api = RapidProAPI(info.context.headers["Business-Area"])
        return api.get_flows()
