"""Accountability-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import Feedback, FeedbackMessage, Message, Survey

from .core import BusinessAreaFactory


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    issue_type = Feedback.POSITIVE_FEEDBACK
    description = factory.Sequence(lambda n: f"Feedback description {n}")
    business_area = factory.SubFactory(BusinessAreaFactory)


class FeedbackMessageFactory(DjangoModelFactory):
    class Meta:
        model = FeedbackMessage

    feedback = factory.SubFactory(FeedbackFactory)
    description = factory.Sequence(lambda n: f"Feedback message {n}")


class CommunicationMessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    title = factory.Sequence(lambda n: f"Message {n}")
    body = factory.Sequence(lambda n: f"Message body {n}")
    sampling_type = Message.SamplingChoices.FULL_LIST
    full_list_arguments = {"excluded_admin_areas": []}
    business_area = factory.SubFactory(BusinessAreaFactory)


class SurveyFactory(DjangoModelFactory):
    class Meta:
        model = Survey

    title = factory.Sequence(lambda n: f"Survey {n}")
    category = Survey.CATEGORY_MANUAL
    business_area = factory.SubFactory(BusinessAreaFactory)
