import random
from io import BytesIO

import factory
from django.core.files.uploadedfile import InMemoryUploadedFile
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
    TicketPaymentVerificationDetails,
    GrievanceDocument,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification


class GrievanceTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrievanceTicket

    user_modified = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)
    created_by = factory.SubFactory(UserFactory)
    assigned_to = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(GrievanceTicket.STATUS_CHOICES, getter=lambda c: c[0])
    category = factory.fuzzy.FuzzyChoice(
        (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_REFERRAL,
        )
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    admin2 = factory.LazyAttribute(
        lambda o: Area.objects.filter(area_type__country__name__iexact="afghanistan").first()
    )
    area = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    language = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    created_at = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)


class SensitiveGrievanceTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSensitiveDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None

    @factory.post_generation
    def create_extras(obj, create, extracted, **kwargs):
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_record = PaymentRecordFactory(household=household)
        obj.save()


class GrievanceComplaintTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None

    @factory.post_generation
    def create_extras(obj, create, extracted, **kwargs):
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_record = PaymentRecordFactory(household=household)

        obj.save()


class SensitiveGrievanceTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSensitiveDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None


class GrievanceComplaintTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None


class TicketNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketNote

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=random.choice(
            (
                GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                GrievanceTicket.CATEGORY_REFERRAL,
            )
        ),
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    created_by = factory.SubFactory(UserFactory)


class TicketAddIndividualDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketAddIndividualDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    household = None
    individual_data = {}
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketDeleteIndividualDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketDeleteIndividualDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        ),
    )
    individual = None
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketDeleteHouseholdDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketDeleteHouseholdDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        ),
    )
    household = None
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketIndividualDataUpdateDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketIndividualDataUpdateDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    individual = None
    individual_data = {}


class TicketHouseholdDataUpdateDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketHouseholdDataUpdateDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    household = None
    household_data = {}


class TicketSystemFlaggingDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSystemFlaggingDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            issue_type=None,
        ),
    )


class TicketNeedsAdjudicationDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketNeedsAdjudicationDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            issue_type=None,
        ),
    )


class PositiveFeedbackTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketPositiveFeedbackDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK)
    household = None
    individual = None


class NegativeFeedbackTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketNegativeFeedbackDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK)
    household = None
    individual = None


class ReferralTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketReferralDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_REFERRAL)
    household = None
    individual = None


class TicketPaymentVerificationDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketPaymentVerificationDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION)
    payment_verification = factory.SubFactory(
        PaymentVerificationFactory, status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    )


class GrievanceDocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrievanceDocument

    file = InMemoryUploadedFile(
        name="xyz.jpg",
        file=BytesIO(b"xxxxxxxxxxx"),
        charset=None,
        field_name="0",
        size=2 * 1024 * 1024,
        content_type="image/jpeg",
    )
    name = "xyz"
    file_size = 2 * 1024 * 1024
    content_type = "image/jpeg"
    grievance_ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK)
