import random
from io import BytesIO
from typing import Any

from django.core.files.uploadedfile import InMemoryUploadedFile

import factory
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
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
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.program.fixtures import ProgramFactory


class GrievanceTicketFactory(DjangoModelFactory):
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


    @factory.post_generation
    def programs(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return

        self.programs.add(ProgramFactory())


class SensitiveGrievanceTicketFactory(DjangoModelFactory):
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
    payment_obj = None

    @factory.post_generation
    def create_extras(obj, create: bool, extracted: bool, **kwargs: Any) -> None:
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_obj = PaymentRecordFactory(household=household)
        obj.save()


class GrievanceComplaintTicketFactory(DjangoModelFactory):
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
    payment_object_id = None
    payment_content_type_id = None

    @factory.post_generation
    def create_extras(obj, create: bool, extracted: bool, **kwargs: Any) -> None:
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_object_id = PaymentRecordFactory(household=household).id
        obj.payment_content_type_id = 80

        obj.save()


class SensitiveGrievanceTicketWithoutExtrasFactory(DjangoModelFactory):
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
    payment_obj = None


class GrievanceComplaintTicketWithoutExtrasFactory(DjangoModelFactory):
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
    payment_object_id = None
    payment_content_type_id = None


class TicketNoteFactory(DjangoModelFactory):
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


class TicketAddIndividualDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketAddIndividualDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    household = None
    individual_data = {}
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketDeleteIndividualDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketDeleteIndividualDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
    )
    individual = None
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketDeleteHouseholdDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketDeleteHouseholdDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
    )
    household = None
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketIndividualDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketIndividualDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    individual = None
    individual_data = {}


class TicketHouseholdDataUpdateDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketHouseholdDataUpdateDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
    )
    household = None
    household_data = {}


class TicketSystemFlaggingDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketSystemFlaggingDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
    )


class TicketNeedsAdjudicationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketNeedsAdjudicationDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=None,
    )


class PositiveFeedbackTicketWithoutExtrasFactory(DjangoModelFactory):
    class Meta:
        model = TicketPositiveFeedbackDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK)
    household = None
    individual = None


class NegativeFeedbackTicketWithoutExtrasFactory(DjangoModelFactory):
    class Meta:
        model = TicketNegativeFeedbackDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK)
    household = None
    individual = None


class ReferralTicketWithoutExtrasFactory(DjangoModelFactory):
    class Meta:
        model = TicketReferralDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_REFERRAL)
    household = None
    individual = None


class TicketPaymentVerificationDetailsFactory(DjangoModelFactory):
    class Meta:
        model = TicketPaymentVerificationDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION)
    payment_verification = factory.SubFactory(
        PaymentVerificationFactory, status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
    )


class GrievanceDocumentFactory(DjangoModelFactory):
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
