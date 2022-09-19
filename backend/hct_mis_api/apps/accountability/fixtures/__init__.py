from random import choice

import factory
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.models import BusinessArea


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
