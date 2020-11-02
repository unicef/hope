import factory
from factory import fuzzy
from pytz import utc

from account.fixtures import UserFactory
from core.models import BusinessArea, AdminAreaType
from grievance.models import GrievanceTicket


class GrievanceTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrievanceTicket

    user_modified = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)
    created_by = factory.SubFactory(UserFactory)
    assigned_to = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(GrievanceTicket.STATUS_CHOICES, getter=lambda c: c[0],)
    category = factory.fuzzy.FuzzyChoice(
        (GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT, GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK)
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    admin = factory.LazyAttribute(
        lambda o: AdminAreaType.objects.filter(admin_level=2).order_by("?").first().display_name
    )
    area = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    language = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
