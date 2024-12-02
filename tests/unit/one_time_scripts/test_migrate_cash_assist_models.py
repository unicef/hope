import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

import factory
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import CaIdIterator
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketSensitiveDetails,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, create_household
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.payment.models import (
    CashPlan,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.one_time_scripts.migrate_cash_assist_models import (
    get_status,
    migrate_cash_plan_to_payment_plan,
)


class CashPlanFactory(DjangoModelFactory):
    class Meta:
        model = CashPlan

    ca_id = factory.Sequence(lambda n: f"PP-0000-00-1122334{n}")
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    status = factory.fuzzy.FuzzyChoice(
        CashPlan.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    name = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    distribution_level = "Registration Group"
    dispersion_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    coverage_duration = factory.fuzzy.FuzzyInteger(1, 4)
    coverage_unit = factory.Faker(
        "random_element",
        elements=["Day(s)", "Week(s)", "Month(s)", "Year(s)"],
    )
    comments = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    delivery_type = factory.fuzzy.FuzzyChoice(
        DeliveryMechanismChoices.DELIVERY_TYPE_CHOICES,
        getter=lambda c: c[0],
    )
    assistance_measurement = factory.Faker("currency_name")
    assistance_through = factory.Faker("random_element", elements=["ING", "Bank of America", "mBank"])
    vision_id = factory.Faker("uuid4")
    funds_commitment = factory.fuzzy.FuzzyInteger(1000, 99999999)
    exchange_rate = factory.fuzzy.FuzzyDecimal(0.1, 9.9)
    down_payment = factory.fuzzy.FuzzyInteger(1000, 99999999)
    validation_alerts_count = factory.fuzzy.FuzzyInteger(1, 3)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 4)
    total_persons_covered_revised = factory.fuzzy.FuzzyInteger(1, 4)

    total_entitled_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_entitled_quantity_revised = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_delivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)

    total_entitled_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_entitled_quantity_revised_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_delivered_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)


class ServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    ca_id = factory.Iterator(CaIdIterator("SRV"))
    full_name = factory.Faker("company")
    short_name = factory.LazyAttribute(lambda o: o.full_name[0:3])
    country = factory.Faker("country_code")
    vision_id = factory.fuzzy.FuzzyInteger(1342342, 9999999932)


class PaymentRecordFactory(DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = factory.fuzzy.FuzzyChoice(
        PaymentRecord.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    full_name = factory.Faker("name")
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    ca_id = factory.Iterator(CaIdIterator("PR"))
    ca_hash_id = factory.Faker("uuid4")
    parent = factory.SubFactory(CashPlanFactory)
    household = factory.SubFactory(HouseholdFactory)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 7)
    distribution_modality = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
    entitlement_card_number = factory.Faker("ssn")
    entitlement_card_status = factory.fuzzy.FuzzyChoice(
        PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    entitlement_card_issue_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    entitlement_quantity_usd = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivered_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivered_quantity_usd = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivery_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    service_provider = factory.SubFactory(ServiceProviderFactory)
    registration_ca_id = factory.Faker("uuid4")


class TestMigrateCashPlanToPaymentPlan(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

        cls.content_type_for_payment_plan = ContentType.objects.get_for_model(PaymentPlan)
        cls.content_type_for_cash_plan = ContentType.objects.get_for_model(CashPlan)
        cls.content_type_for_payment = ContentType.objects.get_for_model(Payment)

        cls.cash_delivery_mechanism = DeliveryMechanismFactory(name="Cash")
        cls.digital_delivery_mechanism = DeliveryMechanismFactory(name="Digital")

        cls.service_provider1 = ServiceProviderFactory()
        cls.service_provider2 = ServiceProviderFactory()
        cls.service_provider3 = ServiceProviderFactory()

        cls.tp1 = TargetPopulationFactory()
        cls.tp2 = TargetPopulationFactory()

        cls.cash_plan = CashPlanFactory(
            delivery_type=cls.cash_delivery_mechanism.name,
            service_provider=cls.service_provider1,
            is_migrated_to_payment_plan=False,
            start_date=datetime.date(2021, 1, 1),
            dispersion_date=datetime.date(2021, 1, 2),
            status_date=datetime.date(2021, 1, 3),
        )

        cls.cash_plan2 = CashPlanFactory(
            delivery_type=cls.cash_delivery_mechanism.name,
            service_provider=cls.service_provider2,
            is_migrated_to_payment_plan=False,
        )  # CP without payments, not migrating

        cls.cash_plan3 = CashPlanFactory(
            delivery_type=cls.digital_delivery_mechanism.name,
            service_provider=cls.service_provider1,
            is_migrated_to_payment_plan=False,
        )  # CP without payments, not migrating, same service provider as CP1 so fsp delivery mechanisms should be updated

        hh1, _ = create_household(household_args={"size": 2})
        cls.pr1 = PaymentRecordFactory(
            parent=cls.cash_plan,
            delivery_type=cls.cash_delivery_mechanism,
            target_population=cls.tp1,
            head_of_household=hh1.head_of_household,
            service_provider=cls.service_provider1,
        )
        hh2, _ = create_household(household_args={"size": 2})
        cls.pr2 = PaymentRecordFactory(
            parent=cls.cash_plan,
            delivery_type=cls.digital_delivery_mechanism,
            target_population=cls.tp2,
            head_of_household=hh2.head_of_household,
            service_provider=cls.service_provider1,
        )
        cls.pvs = PaymentVerificationSummaryFactory(
            payment_plan_obj=cls.cash_plan,
        )
        cls.pvp = PaymentVerificationPlanFactory(
            payment_plan_obj=cls.cash_plan,
            payment_plan=None,
        )
        cls.pv1 = PaymentVerificationFactory(
            payment_verification_plan=cls.pvp,
            payment_obj=cls.pr1,
            status=PaymentVerification.STATUS_PENDING,
            payment=None,
        )
        cls.pv2 = PaymentVerificationFactory(
            payment_verification_plan=cls.pvp,
            payment_obj=cls.pr2,
            status=PaymentVerification.STATUS_PENDING,
            payment=None,
        )

        cls.grievance_ticket1 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_complaint_details = TicketComplaintDetails.objects.create(
            ticket=cls.grievance_ticket1,
            payment_obj=cls.pr1,
            payment_object_id=cls.pr1.id,
            payment_content_type=cls.content_type_for_payment,
        )
        cls.grievance_ticket2 = GrievanceTicketFactory(status=GrievanceTicket.STATUS_IN_PROGRESS)
        cls.ticket_sensitive_details = TicketSensitiveDetails.objects.create(
            ticket=cls.grievance_ticket2,
            payment_obj=cls.pr2,
            payment_object_id=cls.pr2.id,
            payment_content_type=cls.content_type_for_payment,
        )

    def test_migrate(self) -> None:
        assert FinancialServiceProvider.objects.count() == 0
        assert PaymentPlan.objects.count() == 0
        assert DeliveryMechanismPerPaymentPlan.objects.count() == 0
        assert Payment.objects.count() == 0
        assert PaymentVerificationSummary.objects.count() == 1
        assert PaymentVerificationPlan.objects.count() == 1
        assert PaymentVerification.objects.count() == 2

        migrate_cash_plan_to_payment_plan()

        self.service_provider1.refresh_from_db()
        self.service_provider2.refresh_from_db()
        self.service_provider3.refresh_from_db()
        self.cash_plan.refresh_from_db()
        self.pr1.refresh_from_db()
        self.pr2.refresh_from_db()
        self.pvs.refresh_from_db()
        self.pvp.refresh_from_db()
        self.pv1.refresh_from_db()
        self.pv2.refresh_from_db()
        self.grievance_ticket1.refresh_from_db()
        self.grievance_ticket2.refresh_from_db()
        self.ticket_complaint_details.refresh_from_db()
        self.ticket_sensitive_details.refresh_from_db()

        # Assert FinancialServiceProvider is created

        assert self.service_provider1.is_migrated_to_payment_plan is True
        assert self.service_provider2.is_migrated_to_payment_plan is True
        assert self.service_provider3.is_migrated_to_payment_plan is False  # no cash plan assigned so not migrated

        assert FinancialServiceProvider.objects.count() == 2

        fsp = FinancialServiceProvider.objects.get(vision_vendor_number=self.service_provider1.vision_id)
        assert fsp.name == self.service_provider1.full_name
        assert fsp.vision_vendor_number == self.service_provider1.vision_id
        assert fsp.communication_channel == "API"
        assert fsp.internal_data == {
            "is_cash_assist": True,
            "business_area": self.service_provider1.business_area.slug,
            "country": self.service_provider1.country,
            "ca_id": self.service_provider1.ca_id,
            "short_name": self.service_provider1.short_name,
        }
        assert self.service_provider1.is_migrated_to_payment_plan is True
        assert fsp.delivery_mechanisms.count() == 2

        assert self.cash_plan.is_migrated_to_payment_plan is True
        assert self.cash_plan2.is_migrated_to_payment_plan is False  # no payments assigned so not migrated

        # Assert PaymentPlans created
        pps = PaymentPlan.objects.filter(unicef_id=self.cash_plan.ca_id)
        assert pps.count() == 2  # One for each target population
        pp1 = pps.get(target_population=self.pr1.target_population)
        assert pp1.unicef_id == self.cash_plan.ca_id
        assert pp1.status == "FINISHED"
        assert pp1.name == self.pr1.target_population.name
        assert pp1.is_cash_assist is True
        assert pp1.business_area_id == self.cash_plan.business_area.id
        assert pp1.created_by_id == self.pr1.target_population.created_by.id
        assert pp1.created_at == self.cash_plan.created_at
        assert pp1.target_population_id == self.pr1.target_population.id
        assert pp1.program_cycle_id == self.pr1.target_population.program_cycle.id
        assert pp1.currency == self.pr1.currency
        assert pp1.dispersion_start_date == datetime.date(2021, 1, 1)
        assert pp1.dispersion_end_date == datetime.date(2021, 1, 2)
        assert pp1.status_date == datetime.datetime(2021, 1, 3, tzinfo=utc)
        assert pp1.exchange_rate == self.cash_plan.exchange_rate
        assert pp1.total_entitled_quantity == self.cash_plan.total_entitled_quantity
        assert pp1.total_entitled_quantity_usd == self.cash_plan.total_entitled_quantity_usd
        assert pp1.total_entitled_quantity_revised == self.cash_plan.total_entitled_quantity_revised
        assert pp1.total_entitled_quantity_revised_usd == self.cash_plan.total_entitled_quantity_revised_usd
        assert pp1.total_delivered_quantity == self.cash_plan.total_delivered_quantity
        assert pp1.total_delivered_quantity_usd == self.cash_plan.total_delivered_quantity_usd
        assert pp1.total_undelivered_quantity == self.cash_plan.total_undelivered_quantity
        assert pp1.total_undelivered_quantity_usd == self.cash_plan.total_undelivered_quantity_usd
        assert pp1.internal_data == {
            "name": self.cash_plan.name,
            "ca_hash_id": str(self.cash_plan.ca_hash_id),
            "distribution_level": self.cash_plan.distribution_level,
            "coverage_duration": self.cash_plan.coverage_duration,
            "coverage_unit": self.cash_plan.coverage_unit,
            "comments": self.cash_plan.comments,
            "assistance_measurement": self.cash_plan.assistance_measurement,
            "assistance_through": self.cash_plan.assistance_through,
            "vision_id": self.cash_plan.vision_id,
            "funds_commitment": self.cash_plan.funds_commitment,
            "down_payment": self.cash_plan.down_payment,
            "validation_alerts_count": self.cash_plan.validation_alerts_count,
            "total_persons_covered": self.cash_plan.total_persons_covered,
            "total_persons_covered_revised": self.cash_plan.total_persons_covered_revised,
        }

        pp2 = pps.get(target_population=self.pr2.target_population)

        # Assert DeliveryMechanismPerPaymentPlans created
        assert DeliveryMechanismPerPaymentPlan.objects.count() == 2
        dmp1 = DeliveryMechanismPerPaymentPlan.objects.get(payment_plan=pp1)
        assert dmp1.delivery_mechanism == self.cash_delivery_mechanism
        assert dmp1.sent_date == self.cash_plan.status_date
        assert dmp1.delivery_mechanism_order == 1
        assert dmp1.created_by == self.pr1.target_population.created_by
        assert dmp1.created_at == self.pr1.target_population.created_at
        assert dmp1.financial_service_provider == fsp

        dmp2 = DeliveryMechanismPerPaymentPlan.objects.get(payment_plan=pp2)
        assert dmp2.delivery_mechanism == self.digital_delivery_mechanism

        # Assert PaymentRecords created
        assert Payment.objects.count() == 2

        ps = Payment.objects.filter(parent_id=pp1.id)
        assert ps.count() == 1
        p1 = ps.first()
        assert p1.business_area_id == self.pr1.business_area.id
        assert p1.status == get_status(self.pr1.status)
        assert p1.status_date == self.pr1.status_date
        assert p1.household_id == self.pr1.household.id
        assert p1.head_of_household_id == self.pr1.head_of_household.id
        assert p1.collector_id == self.pr1.head_of_household.id
        assert p1.delivery_type_id == self.pr1.delivery_type.id
        assert p1.currency == self.pr1.currency
        assert p1.entitlement_quantity == self.pr1.entitlement_quantity
        assert p1.entitlement_quantity_usd == self.pr1.entitlement_quantity_usd
        assert p1.delivered_quantity == self.pr1.delivered_quantity
        assert p1.delivered_quantity_usd == self.pr1.delivered_quantity_usd
        assert p1.delivery_date == self.pr1.delivery_date
        assert p1.transaction_reference_id == self.pr1.transaction_reference_id
        assert p1.transaction_status_blockchain_link == self.pr1.transaction_status_blockchain_link
        assert p1.financial_service_provider == fsp
        assert p1.program_id == self.pr1.target_population.program_cycle.program_id
        assert p1.is_cash_assist is True
        assert p1.internal_data == {
            "ca_hash_id": str(self.pr1.ca_hash_id),
            "full_name": self.pr1.full_name,
            "total_persons_covered": self.pr1.total_persons_covered,
            "distribution_modality": self.pr1.distribution_modality,
            "target_population_cash_assist_id": self.pr1.target_population_cash_assist_id,
            "target_population": str(self.pr1.target_population.id),
            "entitlement_card_number": self.pr1.entitlement_card_number,
            "entitlement_card_status": self.pr1.entitlement_card_status,
            "entitlement_card_issue_date": str(self.pr1.entitlement_card_issue_date),
            "vision_id": self.pr1.vision_id,
            "registration_ca_id": self.pr1.registration_ca_id,
            "service_provider": str(self.pr1.service_provider_id),
        }

        ps = Payment.objects.filter(parent_id=pp2.id)
        assert ps.count() == 1
        p2 = ps.first()
        assert p2.delivery_type_id == self.digital_delivery_mechanism.id

        # Assert PaymentVerificationSummary is created
        assert PaymentVerificationSummary.objects.count() == 2
        assert PaymentVerificationSummary.objects.filter(payment_plan=pp1).count() == 1
        assert PaymentVerificationSummary.objects.filter(payment_plan=pp2).count() == 1

        # Assert PaymentVerificationPlan is created
        assert PaymentVerificationPlan.objects.count() == 2
        pvp1 = PaymentVerificationPlan.objects.get(payment_plan=pp1)
        pvp2 = PaymentVerificationPlan.objects.get(payment_plan=pp2)
        assert pvp2.unicef_id == pvp1.unicef_id

        # Assert PaymentVerification is created
        assert PaymentVerification.objects.count() == 2
        pv1 = PaymentVerification.objects.get(payment_verification_plan=pvp1)
        assert pv1.payment == p1

        pv2 = PaymentVerification.objects.get(payment_verification_plan=pvp2)
        assert pv2.payment == p2

        # Assert GrievanceTickets updated
        assert GrievanceTicket.objects.count() == 2
        assert TicketComplaintDetails.objects.count() == 1
        assert TicketSensitiveDetails.objects.count() == 1
        self.ticket_complaint_details.refresh_from_db()
        self.ticket_sensitive_details.refresh_from_db()
        assert self.ticket_complaint_details.payment == p1
        assert self.ticket_sensitive_details.payment == p2
