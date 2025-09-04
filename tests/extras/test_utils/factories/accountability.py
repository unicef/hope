import random
from random import choice
from typing import Any

from factory.django import DjangoModelFactory
import factory.fuzzy
from pytz import utc

from extras.test_utils.factories.account import UserFactory
from hope.apps.account.models import User
from hope.apps.accountability.models import Feedback, FeedbackMessage, Message, Survey
from hope.apps.core.models import BusinessArea
from hope.apps.geo.models import Area
from hope.apps.household.models import Household
from hope.apps.program.models import Program


class FeedbackFactory(DjangoModelFactory):
    class Meta:
        model = Feedback

    created_by = factory.SubFactory(UserFactory)
    issue_type = factory.fuzzy.FuzzyChoice(
        (
            Feedback.POSITIVE_FEEDBACK,
            Feedback.NEGATIVE_FEEDBACK,
        )
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    admin2 = factory.LazyAttribute(
        lambda o: Area.objects.filter(area_type__country__name__iexact="afghanistan").first()
    )
    area = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    language = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())


class FeedbackMessageFactory(DjangoModelFactory):
    class Meta:
        model = FeedbackMessage

    feedback = factory.SubFactory(
        FeedbackFactory,
        issue_type=random.choice(
            (
                Feedback.POSITIVE_FEEDBACK,
                Feedback.NEGATIVE_FEEDBACK,
            )
        ),
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    created_by = factory.SubFactory(UserFactory)


class SurveyFactory(DjangoModelFactory):
    class Meta:
        model = Survey

    title = factory.Faker("sentence", nb_words=2, variable_nb_words=True, ext_word_list=None)
    category = factory.fuzzy.FuzzyChoice(Survey.CATEGORY_CHOICES, getter=lambda c: c[0])
    created_by = factory.SubFactory(UserFactory)
    payment_plan = None
    program = None
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())

    @factory.post_generation
    def payment_plan_payment_verification_summary(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return

        if self.payment_plan is not None:
            self.program = self.payment_plan.program_cycle.program
            self.save()


class CommunicationMessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    title = factory.Faker("text", max_nb_chars=60)
    body = factory.Faker("text", max_nb_chars=1000)
    created_by = factory.SubFactory(UserFactory)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    sampling_type = factory.Faker("random_element", elements=Message.SamplingChoices.choices)
    full_list_arguments = factory.LazyAttribute(
        lambda o: {"excluded_admin_areas": []} if o.sampling_type == Message.SamplingChoices.FULL_LIST else None
    )
    random_sampling_arguments = factory.LazyAttribute(
        lambda o: (
            {
                "age": {"max": 80, "min": 30},
                "sex": choice(["MALE", "FEMALE"]),
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            }
            if o.sampling_type == Message.SamplingChoices.RANDOM
            else None
        )
    )
    created_at = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)

    @factory.post_generation
    def cash_plan_payment_verification_summary(obj, create: bool, extracted: bool, **kwargs: Any) -> None:  # noqa: N805
        if not create:
            return

        households = Household.objects.all()
        obj.number_of_recipients = len(households)
        obj.households.set(households)
        obj.save()


def generate_messages() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    user_root = User.objects.get(username="root")
    program = Program.objects.get(name="Test Program")
    households = Household.objects.filter(program=program)
    hh_1 = households.first()
    hh_2 = households.last()

    msg_data = [
        {
            "unicef_id": "MSG-22-0001",
            "title": "Hello World!",
            "body": "World is beautiful, don't mess with it!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0004",
            "title": "You got credit of USD 200",
            "body": "Greetings {recipient_full_name}, we have sent you USD 200 in your registered account on "
            "{rp_timestamp}",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 80.0,
                "confidence_interval": 0.8,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0002",
            "title": "Hello There!",
            "body": "Hey, there. Welcome to the party!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0003",
            "title": "We hold your back!",
            "body": "Hey XYZ, don't be worry. We UNICEF are here to help to grow!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": None,
            "sample_size": 2,
        },
    ]
    for msg in msg_data:
        msg_obj = CommunicationMessageFactory(**msg)
        msg_obj.households.set([hh_1, hh_2])


def generate_feedback() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    feedback_data = [
        {
            "business_area": ba,
            "issue_type": "POSITIVE_FEEDBACK",
            "description": "Positive Feedback",
        },
        {
            "business_area": ba,
            "issue_type": "NEGATIVE_FEEDBACK",
            "description": "Negative Feedback",
        },
    ]
    feedback_positive = FeedbackFactory(**feedback_data[0])
    feedback_positive.unicef_id = "FED-23-0001"
    feedback_positive.save()
    feedback_negative = FeedbackFactory(**feedback_data[1])
    feedback_negative.unicef_id = "FED-23-0002"
    feedback_negative.save()
