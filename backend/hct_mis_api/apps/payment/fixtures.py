import factory

from datetime import timedelta
from decimal import Decimal
from random import randint
from factory import fuzzy
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import CaIdIterator
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory, IndividualRoleInHouseholdFactory
from hct_mis_api.apps.household.models import Household, ROLE_PRIMARY
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FinancialServiceProviderXlsxReport,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
    CashPlanPaymentVerificationSummary,
    PaymentPlan,
    Payment,
    GenericPayment,
    PaymentChannel,
)
from hct_mis_api.apps.program.fixtures import (
    ProgramFactory,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.payment.models import CashPlan
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


class CashPlanPaymentVerificationSummaryFactory(factory.DjangoModelFactory):
    class Meta:
        model = CashPlanPaymentVerificationSummary


class CashPlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = CashPlan

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    status = fuzzy.FuzzyChoice(
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
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    dispersion_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
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
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE,
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

    @factory.post_generation
    def cash_plan_payment_verification_summary(self, create, extracted, **kwargs):
        if not create:
            return

        CashPlanPaymentVerificationSummaryFactory(cash_plan=self)


class ServiceProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    ca_id = factory.Iterator(CaIdIterator("SRV"))
    full_name = factory.Faker("company")
    short_name = factory.LazyAttribute(lambda o: o.full_name[0:3])
    country = factory.Faker("country_code")
    vision_id = factory.fuzzy.FuzzyInteger(1342342, 9999999932)


class FinancialServiceProviderXlsxTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = FinancialServiceProviderXlsxTemplate

    columns = fuzzy.FuzzyChoice(
        FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS,
        getter=lambda c: c[0],
    )


class FinancialServiceProviderFactory(factory.DjangoModelFactory):
    class Meta:
        model = FinancialServiceProvider

    name = factory.Faker("company")
    vision_vendor_number = factory.Faker("ssn")
    delivery_mechanisms = factory.List(
        [
            fuzzy.FuzzyChoice(
                GenericPayment.DELIVERY_TYPE_CHOICE,
                getter=lambda c: c[0],
            )
        ]
    )
    distribution_limit = fuzzy.FuzzyDecimal(100.0, 1000.0)
    communication_channel = fuzzy.FuzzyChoice(
        FinancialServiceProvider.COMMUNICATION_CHANNEL_CHOICES, getter=lambda c: c[0]
    )
    data_transfer_configuration = factory.Faker("json")
    fsp_xlsx_template = factory.SubFactory(FinancialServiceProviderXlsxTemplateFactory)


class FinancialServiceProviderXlsxReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = FinancialServiceProviderXlsxReport

    financial_service_provider = factory.SubFactory(FinancialServiceProviderFactory)


class PaymentRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = fuzzy.FuzzyChoice(
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
    cash_plan = factory.SubFactory(CashPlanFactory)
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
    entitlement_card_status = fuzzy.FuzzyChoice(
        PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    entitlement_card_issue_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE,
        getter=lambda c: c[0],
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
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


class CashPlanPaymentVerificationFactory(factory.DjangoModelFactory):
    status = fuzzy.FuzzyChoice(
        ((CashPlanPaymentVerification.STATUS_PENDING, "pending"),),
        getter=lambda c: c[0],
    )
    sampling = fuzzy.FuzzyChoice(
        CashPlanPaymentVerification.SAMPLING_CHOICES,
        getter=lambda c: c[0],
    )
    verification_channel = fuzzy.FuzzyChoice(
        CashPlanPaymentVerification.VERIFICATION_CHANNEL_CHOICES,
        getter=lambda c: c[0],
    )
    cash_plan = factory.Iterator(CashPlan.objects.all())
    sample_size = fuzzy.FuzzyInteger(0, 100)
    responded_count = fuzzy.FuzzyInteger(20, 90)
    received_count = fuzzy.FuzzyInteger(30, 70)
    not_received_count = fuzzy.FuzzyInteger(0, 10)
    received_with_problems_count = fuzzy.FuzzyInteger(0, 10)
    rapid_pro_flow_start_uuids = factory.LazyFunction(list)

    class Meta:
        model = CashPlanPaymentVerification


class PaymentVerificationFactory(factory.DjangoModelFactory):
    cash_plan_payment_verification = factory.Iterator(CashPlanPaymentVerification.objects.all())
    payment_record = factory.LazyAttribute(
        lambda o: PaymentRecord.objects.filter(cash_plan=o.cash_plan_payment_verification.cash_plan)
        .order_by("?")
        .first()
    )
    status = fuzzy.FuzzyChoice(
        PaymentVerification.STATUS_CHOICES,
        getter=lambda c: c[0],
    )
    status_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)

    class Meta:
        model = PaymentVerification


class RealProgramFactory(factory.DjangoModelFactory):
    class Meta:
        model = Program

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    ca_id = factory.Iterator(CaIdIterator("PRG"))
    name = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    status = fuzzy.FuzzyChoice(
        Program.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True,
        ext_word_list=None,
    )
    budget = factory.fuzzy.FuzzyDecimal(1000000.0, 900000000.0)
    frequency_of_payments = fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE,
        getter=lambda c: c[0],
    )
    sector = fuzzy.FuzzyChoice(
        Program.SECTOR_CHOICE,
        getter=lambda c: c[0],
    )
    scope = fuzzy.FuzzyChoice(
        Program.SCOPE_CHOICE,
        getter=lambda c: c[0],
    )
    cash_plus = fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)
    administrative_areas_of_implementation = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    individual_data_needed = fuzzy.FuzzyChoice((True, False))


class RealCashPlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = CashPlan

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    ca_id = factory.Iterator(CaIdIterator("CSH"))
    ca_hash_id = factory.Faker("uuid4")
    program = factory.SubFactory(RealProgramFactory)
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    status = fuzzy.FuzzyChoice(
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
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    dispersion_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
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
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE,
        getter=lambda c: c[0],
    )
    assistance_measurement = factory.Faker("currency_name")
    assistance_through = factory.LazyAttribute(lambda o: ServiceProvider.objects.order_by("?").first().ca_id)
    vision_id = factory.fuzzy.FuzzyInteger(123534, 12353435234)
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

    @factory.post_generation
    def cash_plan_payment_verification_summary(self, create, extracted, **kwargs):
        if not create:
            return

        CashPlanPaymentVerificationSummaryFactory(cash_plan=self)


class RealPaymentRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentRecord

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = fuzzy.FuzzyChoice(
        PaymentRecord.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    full_name = factory.Faker("name")
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    ca_id = factory.Iterator(CaIdIterator("PR"))
    ca_hash_id = factory.Faker("uuid4")
    household = factory.LazyAttribute(lambda o: Household.objects.order_by("?").first())
    head_of_household = factory.LazyAttribute(lambda o: o.household.head_of_household)
    total_persons_covered = factory.fuzzy.FuzzyInteger(1, 7)
    distribution_modality = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
    entitlement_card_number = factory.Faker("ssn")
    entitlement_card_status = fuzzy.FuzzyChoice(
        PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    entitlement_card_issue_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE,
        getter=lambda c: c[0],
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    delivered_quantity = factory.LazyAttribute(lambda o: Decimal(randint(10, int(o.entitlement_quantity))))
    delivered_quantity_usd = factory.LazyAttribute(lambda o: Decimal(randint(10, int(o.entitlement_quantity))))
    delivery_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    service_provider = factory.LazyAttribute(lambda o: ServiceProvider.objects.order_by("?").first())
    registration_ca_id = factory.Faker("uuid4")


def generate_real_cash_plans():
    if ServiceProvider.objects.count() < 3:
        ServiceProviderFactory.create_batch(3)
    program = RealProgramFactory()
    cash_plans = RealCashPlanFactory.create_batch(3, program=program)
    for cash_plan in cash_plans:
        RealPaymentRecordFactory.create_batch(
            5,
            cash_plan=cash_plan,
        )
    program.households.set(
        PaymentRecord.objects.exclude(status=PaymentRecord.STATUS_ERROR)
        .filter(cash_plan__in=cash_plans)
        .values_list("household__id", flat=True)
    )


def generate_real_cash_plans_for_households(households):
    if ServiceProvider.objects.count() < 3:
        ServiceProviderFactory.create_batch(3, business_area=households[0].business_area)
    program = RealProgramFactory(business_area=households[0].business_area)
    cash_plans = RealCashPlanFactory.create_batch(3, program=program, business_area=households[0].business_area)
    for cash_plan in cash_plans:
        for hh in households:
            RealPaymentRecordFactory(
                cash_plan=cash_plan,
                household=hh,
                business_area=hh.business_area,
            )
    program.households.set(
        PaymentRecord.objects.exclude(status=PaymentRecord.STATUS_ERROR)
        .filter(cash_plan__in=cash_plans)
        .values_list("household__id", flat=True)
    )


class PaymentPlanFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentPlan

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    exchange_rate = factory.fuzzy.FuzzyDecimal(0.1, 9.9)

    total_entitled_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_entitled_quantity_revised = 0.0
    total_delivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)

    total_entitled_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_entitled_quantity_revised_usd = 0.0
    total_delivered_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)
    total_undelivered_quantity_usd = factory.fuzzy.FuzzyDecimal(20000.0, 90000000.0)

    created_by = factory.SubFactory(UserFactory)
    unicef_id = factory.Faker("uuid4")
    target_population = factory.SubFactory(TargetPopulationFactory)
    program = factory.SubFactory(RealProgramFactory)
    currency = fuzzy.FuzzyChoice(CURRENCY_CHOICES, getter=lambda c: c[0])

    dispersion_start_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    dispersion_end_date = factory.LazyAttribute(lambda o: o.dispersion_start_date + timedelta(days=randint(60, 1000)))
    female_children_count = factory.fuzzy.FuzzyInteger(2, 4)
    male_children_count = factory.fuzzy.FuzzyInteger(2, 4)
    female_adults_count = factory.fuzzy.FuzzyInteger(2, 4)
    male_adults_count = factory.fuzzy.FuzzyInteger(2, 4)
    total_households_count = factory.fuzzy.FuzzyInteger(2, 4)
    total_individuals_count = factory.fuzzy.FuzzyInteger(8, 16)


class PaymentChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = PaymentChannel

    individual = factory.SubFactory(IndividualFactory)
    delivery_mechanism = fuzzy.FuzzyChoice(
        GenericPayment.DELIVERY_TYPE_CHOICE,
        getter=lambda c: c[0],
    )


class PaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Payment

    payment_plan = factory.SubFactory(PaymentPlanFactory)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = fuzzy.FuzzyChoice(
        PaymentRecord.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    household = factory.LazyAttribute(lambda o: HouseholdFactory(head_of_household=IndividualFactory(household=None)))
    head_of_household = factory.LazyAttribute(lambda o: o.household.head_of_household)
    collector = factory.LazyAttribute(
        lambda o: (
            o.household.individuals_and_roles.filter(role=ROLE_PRIMARY).first()
            or
            IndividualRoleInHouseholdFactory(
                household=o.household,
                individual=o.household.head_of_household,
                role=ROLE_PRIMARY
            )
        ).individual
    )
    delivery_type = fuzzy.FuzzyChoice(
        PaymentRecord.DELIVERY_TYPE_CHOICE,
        getter=lambda c: c[0],
    )
    currency = factory.Faker("currency_code")
    entitlement_quantity = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    entitlement_quantity_usd = factory.LazyAttribute(lambda o: Decimal(randint(10, int(o.entitlement_quantity))))
    delivered_quantity = factory.LazyAttribute(lambda o: Decimal(randint(10, int(o.entitlement_quantity))))
    delivered_quantity_usd = factory.LazyAttribute(lambda o: Decimal(randint(10, int(o.entitlement_quantity))))

    delivery_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    entitlement_date = factory.Faker(
        "date_time_this_decade",
        before_now=False,
        after_now=True,
        tzinfo=utc,
    )
    financial_service_provider = factory.SubFactory(FinancialServiceProviderFactory)
    excluded = fuzzy.FuzzyChoice((True, False))
    assigned_payment_channel = factory.LazyAttribute(
        lambda o: PaymentChannelFactory(individual=o.collector)
    )


def generate_real_payment_plans():
    afghanistan = BusinessArea.objects.get(slug="afghanistan")

    if ServiceProvider.objects.count() < 3:
        ServiceProviderFactory.create_batch(3)
    program = RealProgramFactory()
    payment_plans = PaymentPlanFactory.create_batch(
        3, program=program, business_area=afghanistan
    )
    program.households.set(Household.objects.all().values_list("id", flat=True))
    for payment_plan in payment_plans:
        for household in program.households.all():
            PaymentFactory(payment_plan=payment_plan, household=household, business_area=afghanistan)
