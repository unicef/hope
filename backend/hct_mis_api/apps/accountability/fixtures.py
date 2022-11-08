import random
from random import choice

import factory
import factory.fuzzy
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.models import (
    Feedback,
    FeedbackMessage,
    Message,
    Survey,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household


class FeedbackFactory(factory.DjangoModelFactory):
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


class FeedbackMessageFactory(factory.DjangoModelFactory):
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


class SurveyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Survey

    title = factory.Faker("sentence", nb_words=2, variable_nb_words=True, ext_word_list=None)
    category = factory.fuzzy.FuzzyChoice(Survey.CATEGORY_CHOICES, getter=lambda c: c[0])
    created_by = factory.SubFactory(UserFactory)
    target_population = None
    program = None
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())


class CommunicationMessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Message

    title = factory.Faker("text", max_nb_chars=60)
    body = factory.Faker("text", max_nb_chars=1000)
    created_by = factory.SubFactory(UserFactory)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    sampling_type = factory.Faker("random_element", elements=Message.SamplingChoices.choices)
    full_list_arguments = factory.LazyAttribute(
        lambda o: {"excludedAdminAreas": []} if o.sampling_type == Message.SamplingChoices.FULL_LIST else None
    )
    random_sampling_arguments = factory.LazyAttribute(
        lambda o: {
            "age": {"max": 80, "min": 30},
            "sex": choice(["MALE", "FEMALE"]),
            "margin_of_error": 20.0,
            "confidence_interval": 0.9,
            "excluded_admin_areas": [],
        }
        if o.sampling_type == Message.SamplingChoices.RANDOM
        else None
    )
    created_at = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)

    @factory.post_generation
    def cash_plan_payment_verification_summary(obj, create, extracted, **kwargs):
        if not create:
            return

        households = Household.objects.all()
        obj.number_of_recipients = len(households)
        obj.households.set(households)
        obj.save()
