import random
import string
from datetime import timedelta
from decimal import Decimal
from random import choice, randint
from typing import Any, Optional, Union
from uuid import UUID

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.core.utils import CaIdIterator
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import (
    EntitlementCardFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    MALE,
    REFUGEE,
    ROLE_PRIMARY,
    Household,
    Individual,
)
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    CashPlan,
    DeliveryMechanism,
    DeliveryMechanismData,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    GenericPayment,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.utils import to_decimal
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import full_rebuild
from hct_mis_api.apps.utils.models import MergeStatusModel


def update_kwargs_with_usd_currency(kwargs: Any) -> Any:
    currency = kwargs.get("currency", "USD")
    if currency == "USD":
        kwargs["entitlement_quantity"] = kwargs["entitlement_quantity_usd"]
        kwargs["delivered_quantity"] = kwargs["delivered_quantity_usd"]
    return kwargs


class PaymentVerificationSummaryFactory(DjangoModelFactory):
    payment_plan_obj = factory.SubFactory("payment.fixtures.CashPlanFactory")

    class Meta:
        model = PaymentVerificationSummary


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

    @factory.post_generation
    def payment_verification_summary(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return

        PaymentVerificationSummaryFactory(payment_plan_obj=self)


class ServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = ServiceProvider

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    ca_id = factory.Iterator(CaIdIterator("SRV"))
    full_name = factory.Faker("company")
    short_name = factory.LazyAttribute(lambda o: o.full_name[0:3])
    country = factory.Faker("country_code")
    vision_id = factory.fuzzy.FuzzyInteger(1342342, 9999999932)


class DeliveryMechanismFactory(DjangoModelFactory):
    payment_gateway_id = factory.Faker("uuid4")
    code = factory.Faker("uuid4")
    name = factory.Faker("sentence", nb_words=3, variable_nb_words=True, ext_word_list=None)
    transfer_type = factory.fuzzy.FuzzyChoice(DeliveryMechanism.TransferType.choices, getter=lambda c: c[0])

    class Meta:
        model = DeliveryMechanism


class FinancialServiceProviderXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProviderXlsxTemplate

    name = factory.Faker("name")
    columns = FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS


class FinancialServiceProviderFactory(DjangoModelFactory):
    class Meta:
        model = FinancialServiceProvider
        django_get_or_create = ("name",)

    name = factory.Faker("company")
    vision_vendor_number = factory.Faker("ssn")
    distribution_limit = factory.fuzzy.FuzzyDecimal(pow(10, 5), pow(10, 6))
    communication_channel = factory.fuzzy.FuzzyChoice(
        FinancialServiceProvider.COMMUNICATION_CHANNEL_CHOICES, getter=lambda c: c[0]
    )
    data_transfer_configuration = factory.Faker("json")


class FspXlsxTemplatePerDeliveryMechanismFactory(DjangoModelFactory):
    class Meta:
        model = FspXlsxTemplatePerDeliveryMechanism

    financial_service_provider = factory.SubFactory(FinancialServiceProviderFactory)
    delivery_mechanism = factory.SubFactory(DeliveryMechanismFactory)
    xlsx_template = factory.SubFactory(FinancialServiceProviderXlsxTemplateFactory)


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

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> "PaymentRecord":
        instance = model_class(**update_kwargs_with_usd_currency(kwargs))
        instance.save()
        return instance


class PaymentVerificationPlanFactory(DjangoModelFactory):
    payment_plan_obj = factory.SubFactory(CashPlanFactory)
    status = factory.fuzzy.FuzzyChoice(
        ((PaymentVerificationPlan.STATUS_PENDING, "pending"),),
        getter=lambda c: c[0],
    )
    sampling = factory.fuzzy.FuzzyChoice(
        PaymentVerificationPlan.SAMPLING_CHOICES,
        getter=lambda c: c[0],
    )
    verification_channel = factory.fuzzy.FuzzyChoice(
        PaymentVerificationPlan.VERIFICATION_CHANNEL_CHOICES,
        getter=lambda c: c[0],
    )
    sample_size = factory.fuzzy.FuzzyInteger(0, 100)
    responded_count = factory.fuzzy.FuzzyInteger(20, 90)
    received_count = factory.fuzzy.FuzzyInteger(30, 70)
    not_received_count = factory.fuzzy.FuzzyInteger(0, 10)
    received_with_problems_count = factory.fuzzy.FuzzyInteger(0, 10)
    rapid_pro_flow_start_uuids = factory.LazyFunction(list)

    class Meta:
        model = PaymentVerificationPlan


class PaymentVerificationFactory(DjangoModelFactory):
    payment_obj = factory.SubFactory(PaymentRecordFactory)
    payment_verification_plan = factory.Iterator(PaymentVerificationPlan.objects.all())
    status = factory.fuzzy.FuzzyChoice(
        PaymentVerification.STATUS_CHOICES,
        getter=lambda c: c[0],
    )
    status_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)

    class Meta:
        model = PaymentVerification


class RealProgramFactory(DjangoModelFactory):
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
    status = factory.fuzzy.FuzzyChoice(
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
    frequency_of_payments = factory.fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE,
        getter=lambda c: c[0],
    )
    sector = factory.fuzzy.FuzzyChoice(
        Program.SECTOR_CHOICE,
        getter=lambda c: c[0],
    )
    scope = factory.fuzzy.FuzzyChoice(
        Program.SCOPE_CHOICE,
        getter=lambda c: c[0],
    )
    cash_plus = factory.fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)
    administrative_areas_of_implementation = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    programme_code = factory.LazyAttribute(
        lambda o: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    )
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return
        ProgramCycleFactory(program=self, **kwargs)


class RealCashPlanFactory(DjangoModelFactory):
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

    service_provider = factory.LazyAttribute(lambda o: ServiceProvider.objects.order_by("?").first())

    @factory.post_generation
    def payment_verification_summary(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return

        PaymentVerificationSummaryFactory(payment_plan_obj=self)

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return
        ProgramCycleFactory(program=self.program, **kwargs)


class RealPaymentRecordFactory(DjangoModelFactory):
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
    delivery_type = factory.LazyAttribute(lambda o: DeliveryMechanism.objects.order_by("?").first())
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


class PaymentPlanFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlan

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
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
    program_cycle = factory.LazyAttribute(lambda o: o.program.cycles.first())
    currency = factory.fuzzy.FuzzyChoice(CURRENCY_CHOICES, getter=lambda c: c[0])

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


class PaymentPlanSplitFactory(DjangoModelFactory):
    class Meta:
        model = PaymentPlanSplit

    payment_plan = factory.SubFactory(PaymentPlanFactory)
    split_type = factory.fuzzy.FuzzyChoice(
        PaymentPlanSplit.SplitType.choices,
        getter=lambda c: c[0],
    )


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    parent = factory.SubFactory(PaymentPlanFactory)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = GenericPayment.STATUS_PENDING
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
            or IndividualRoleInHouseholdFactory(
                household=o.household, individual=o.household.head_of_household, role=ROLE_PRIMARY
            )
        ).individual
    )
    delivery_type = factory.SubFactory(DeliveryMechanismFactory)
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
    excluded = False
    conflicted = False

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> "Payment":
        instance = model_class(**update_kwargs_with_usd_currency(kwargs))
        instance.save()
        return instance


class ApprovalProcessFactory(DjangoModelFactory):
    class Meta:
        model = ApprovalProcess


class ApprovalFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Approval


class DeliveryMechanismPerPaymentPlanFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryMechanismPerPaymentPlan

    payment_plan = factory.SubFactory(PaymentPlanFactory)
    financial_service_provider = factory.SubFactory(FinancialServiceProviderFactory)
    created_by = factory.SubFactory(UserFactory)
    sent_by = factory.SubFactory(UserFactory)
    sent_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    delivery_mechanism = factory.SubFactory(DeliveryMechanismFactory)
    delivery_mechanism_order = factory.fuzzy.FuzzyInteger(1, 4)


class DeliveryMechanismDataFactory(DjangoModelFactory):
    individual = factory.SubFactory(IndividualFactory)
    delivery_mechanism = factory.SubFactory(DeliveryMechanismFactory)
    rdi_merge_status = MergeStatusModel.MERGED

    class Meta:
        model = DeliveryMechanismData


class PendingDeliveryMechanismDataFactory(DeliveryMechanismDataFactory):
    rdi_merge_status = MergeStatusModel.PENDING

    class Meta:
        model = DeliveryMechanismData


def create_payment_verification_plan_with_status(
    cash_plan: Union[CashPlan, PaymentPlan],
    user: "User",
    business_area: BusinessArea,
    program: Program,
    target_population: "TargetPopulation",
    status: str,
    verification_channel: Optional[str] = None,
    create_failed_payments: bool = False,
) -> PaymentVerificationPlan:
    if not cash_plan.payment_verification_summary.exists():
        PaymentVerificationSummary.objects.create(
            payment_plan_obj=cash_plan,
        )
    payment_verification_plan = PaymentVerificationPlanFactory(payment_plan_obj=cash_plan)
    payment_verification_plan.status = status
    if verification_channel:
        payment_verification_plan.verification_channel = verification_channel
    payment_verification_plan.save(update_fields=("status", "verification_channel"))
    registration_data_import = RegistrationDataImportFactory(
        imported_by=user, business_area=business_area, program=program
    )
    for n in range(5):
        household, _ = create_household(
            {
                "registration_data_import": registration_data_import,
                "admin_area": Area.objects.order_by("?").first(),
                "program": program,
            },
            {"registration_data_import": registration_data_import},
        )

        household.programs.add(program)

        currency = getattr(cash_plan, "currency", None)
        if currency is None:
            currency = "PLN"

        if isinstance(cash_plan, CashPlan):
            payment_record = PaymentRecordFactory(
                parent=cash_plan, household=household, target_population=target_population, currency=currency
            )
        else:
            additional_args = {}
            if create_failed_payments:  # create only two failed Payments
                if n == 2:
                    additional_args = {
                        "delivered_quantity": to_decimal(0),
                        "delivered_quantity_usd": to_decimal(0),
                        "status": Payment.STATUS_NOT_DISTRIBUTED,
                    }
                if n == 3:
                    additional_args = {
                        "delivered_quantity": None,
                        "delivered_quantity_usd": None,
                        "status": Payment.STATUS_ERROR,
                    }
            payment_record = PaymentFactory(
                parent=cash_plan,
                household=household,
                currency=currency,
                **additional_args,
            )

        pv = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment_obj=payment_record,
            status=PaymentVerification.STATUS_PENDING,
        )
        pv.set_pending()
        pv.save()
        EntitlementCardFactory(household=household)
    return payment_verification_plan


def generate_real_cash_plans() -> None:
    if ServiceProvider.objects.count() < 3:
        ServiceProviderFactory.create_batch(3)
    program = Program.objects.filter(name="Test Program").first() or RealProgramFactory(status=Program.ACTIVE)
    cash_plans = RealCashPlanFactory.create_batch(3, program=program)
    for cash_plan in cash_plans:
        generate_payment_verification_plan_with_status = choice([True, False, False])
        targeting_criteria = TargetingCriteriaFactory()

        rule = TargetingCriteriaRule.objects.create(targeting_criteria=targeting_criteria)
        TargetingCriteriaRuleFilter.objects.create(
            targeting_criteria_rule=rule, comparison_method="EQUALS", field_name="residence_status", arguments=[REFUGEE]
        )
        target_population = TargetPopulationFactory(
            program=program,
            status=TargetPopulation.STATUS_OPEN,
            targeting_criteria=targeting_criteria,
        )
        full_rebuild(target_population)
        target_population.status = TargetPopulation.STATUS_READY_FOR_CASH_ASSIST
        target_population.save()
        RealPaymentRecordFactory.create_batch(
            5,
            target_population=target_population,
            parent=cash_plan,
        )

        if generate_payment_verification_plan_with_status:
            root = User.objects.get(username="root")
            create_payment_verification_plan_with_status(
                cash_plan,
                root,
                cash_plan.business_area,
                target_population.program,
                target_population,
                PaymentVerificationPlan.STATUS_ACTIVE,
            )

    program.households.set(
        PaymentRecord.objects.exclude(status=PaymentRecord.STATUS_ERROR)
        .filter(parent__in=cash_plans)
        .values_list("household__id", flat=True)
    )


def generate_reconciled_payment_plan() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    root = User.objects.get(username="root")
    now = timezone.now()
    tp: TargetPopulation = TargetPopulation.objects.all()[0]

    payment_plan = PaymentPlan.objects.update_or_create(
        unicef_id="PP-0060-22-11223344",
        business_area=afghanistan,
        target_population=tp,
        currency="USD",
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        status=PaymentPlan.Status.ACCEPTED,
        created_by=root,
        program=tp.program,
        program_cycle=tp.program.cycles.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        exchange_rate=234.6742,
    )[0]
    # update status
    payment_plan.status_finished()
    payment_plan.save()

    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp_1 = FinancialServiceProviderFactory()
    fsp_1.delivery_mechanisms.set([dm_cash])
    FspXlsxTemplatePerDeliveryMechanismFactory(financial_service_provider=fsp_1)
    DeliveryMechanismPerPaymentPlanFactory(
        payment_plan=payment_plan,
        financial_service_provider=fsp_1,
        delivery_mechanism=dm_cash,
    )

    create_payment_verification_plan_with_status(
        payment_plan,
        root,
        afghanistan,
        tp.program,
        tp,
        PaymentVerificationPlan.STATUS_ACTIVE,
        PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        True,  # create failed payments
    )
    payment_plan.update_population_count_fields()


def generate_payment_plan() -> None:
    # creates a payment plan that has all the necessary data needed to go with it for manual testing

    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    root = User.objects.get(username="root")
    now = timezone.now()
    address = "Ohio"

    program_pk = UUID("00000000-0000-0000-0000-faceb00c0000")
    program = Program.objects.update_or_create(
        pk=program_pk,
        business_area=afghanistan,
        name="Test Program",
        start_date=now,
        end_date=now + timedelta(days=365),
        budget=pow(10, 6),
        cash_plus=True,
        population_goal=250,
        status=Program.ACTIVE,
        frequency_of_payments=Program.ONE_OFF,
        sector=Program.MULTI_PURPOSE,
        scope=Program.SCOPE_UNICEF,
        data_collecting_type=DataCollectingType.objects.get(code="full"),
        programme_code="T3ST",
    )[0]
    program_cycle = ProgramCycleFactory(
        program=program,
    )

    rdi_pk = UUID("4d100000-0000-0000-0000-000000000000")
    rdi = RegistrationDataImportFactory(
        pk=rdi_pk,
        name="Test Import",
        number_of_individuals=3,
        number_of_households=1,
        business_area=afghanistan,
        program=program,
    )

    individual_1_pk = UUID("cc000000-0000-0000-0000-000000000001")
    individual_1 = Individual.objects.update_or_create(
        pk=individual_1_pk,
        birth_date=now - timedelta(days=365 * 30),
        first_registration_date=now - timedelta(days=365),
        last_registration_date=now,
        business_area=afghanistan,
        full_name="Jan Kowalski",
        sex=MALE,
        program=program,
        registration_data_import=rdi,
        defaults={"individual_collection": IndividualCollectionFactory()},
    )[0]

    individual_2_pk = UUID("cc000000-0000-0000-0000-000000000002")
    individual_2 = Individual.objects.update_or_create(
        pk=individual_2_pk,
        birth_date=now - timedelta(days=365 * 30),
        first_registration_date=now - timedelta(days=365),
        last_registration_date=now,
        business_area=afghanistan,
        full_name="Adam Nowak",
        sex=MALE,
        program=program,
        registration_data_import=rdi,
        defaults={"individual_collection": IndividualCollectionFactory()},
    )[0]

    household_1_pk = UUID("aa000000-0000-0000-0000-000000000001")
    household_1 = Household.objects.update_or_create(
        pk=household_1_pk,
        size=4,
        head_of_household=individual_1,
        business_area=afghanistan,
        registration_data_import=rdi,
        first_registration_date=now - timedelta(days=365),
        last_registration_date=now,
        address=address,
        program=program,
        defaults={"household_collection": HouseholdCollectionFactory()},
    )[0]
    individual_1.household = household_1
    individual_1.save()

    household_2_pk = UUID("aa000000-0000-0000-0000-000000000002")
    household_2 = Household.objects.update_or_create(
        pk=household_2_pk,
        size=4,
        head_of_household=individual_2,
        business_area=afghanistan,
        registration_data_import=rdi,
        first_registration_date=now - timedelta(days=365),
        last_registration_date=now,
        address=address,
        program=program,
        defaults={"household_collection": HouseholdCollectionFactory()},
    )[0]
    individual_2.household = household_2
    individual_2.save()

    targeting_criteria_pk = UUID("00000000-0000-0000-0000-feedb00c0000")
    targeting_criteria = TargetingCriteria.objects.update_or_create(
        pk=targeting_criteria_pk,
    )[0]

    targeting_criteria_rule_pk = UUID("00000000-0000-0000-0000-feedb00c0009")
    targeting_criteria_rule = TargetingCriteriaRule.objects.update_or_create(
        pk=targeting_criteria_rule_pk,
        targeting_criteria=targeting_criteria,
    )[0]

    targeting_criteria_rule_condition_pk = UUID("00000000-0000-0000-0000-feedb00c0008")
    TargetingCriteriaRuleFilter.objects.update_or_create(
        pk=targeting_criteria_rule_condition_pk,
        targeting_criteria_rule=targeting_criteria_rule,
        comparison_method="EQUALS",
        field_name="address",
        arguments=[address],
    )

    target_population_pk = UUID("00000000-0000-0000-0000-faceb00c0123")
    target_population = TargetPopulation.objects.update_or_create(
        pk=target_population_pk,
        name="Test Target Population",
        targeting_criteria=targeting_criteria,
        status=TargetPopulation.STATUS_ASSIGNED,
        business_area=afghanistan,
        program=program,
        created_by=root,
        program_cycle=program_cycle,
    )[0]
    full_rebuild(target_population)
    target_population.save()

    payment_plan_pk = UUID("00000000-feed-beef-0000-00000badf00d")
    payment_plan = PaymentPlan.objects.update_or_create(
        pk=payment_plan_pk,
        business_area=afghanistan,
        target_population=target_population,
        currency="USD",
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        created_by=root,
        program=program,
        program_cycle=program_cycle,
    )[0]

    delivery_mechanism_cash = DeliveryMechanism.objects.get(code="cash")

    fsp_1_pk = UUID("00000000-0000-0000-0000-f00000000001")
    fsp_1 = FinancialServiceProvider.objects.update_or_create(
        pk=fsp_1_pk,
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number=123456789,
    )[0]
    fsp_1.delivery_mechanisms.add(delivery_mechanism_cash)

    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1, delivery_mechanism=delivery_mechanism_cash
    )

    DeliveryMechanismPerPaymentPlanFactory(
        payment_plan=payment_plan,
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanism_cash,
    )
    # create primary collector role
    IndividualRoleInHouseholdFactory(household=household_1, individual=individual_1, role=ROLE_PRIMARY)
    IndividualRoleInHouseholdFactory(household=household_2, individual=individual_2, role=ROLE_PRIMARY)
    payment_1_pk = UUID("10000000-feed-beef-0000-00000badf00d")
    Payment.objects.get_or_create(
        pk=payment_1_pk,
        parent=payment_plan,
        business_area=afghanistan,
        currency="USD",
        household=household_1,
        collector=individual_1,
        delivery_type=delivery_mechanism_cash,
        financial_service_provider=fsp_1,
        status_date=now,
        status=Payment.STATUS_PENDING,
        program=program,
    )

    payment_2_pk = UUID("20000000-feed-beef-0000-00000badf00d")
    Payment.objects.get_or_create(
        pk=payment_2_pk,
        parent=payment_plan,
        business_area=afghanistan,
        currency="USD",
        household=household_2,
        collector=individual_2,
        delivery_type=delivery_mechanism_cash,
        financial_service_provider=fsp_1,
        status_date=now,
        status=Payment.STATUS_PENDING,
        program=program,
    )

    payment_plan.update_population_count_fields()


def update_fsps() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    for fsp in FinancialServiceProvider.objects.all():
        fsp.allowed_business_areas.add(afghanistan)


def generate_delivery_mechanisms() -> None:
    data = [
        {
            "code": "cardless_cash_withdrawal",
            "name": "Cardless cash withdrawal",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "cash",
            "name": "Cash",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "cash_by_fsp",
            "name": "Cash by FSP",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "cheque",
            "name": "Cheque",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "deposit_to_card",
            "name": "Deposit to Card",
            "requirements": {
                "required_fields": [
                    "card_number__deposit_to_card",
                ],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [
                    "card_number__deposit_to_card",
                ],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "mobile_money",
            "name": "Mobile Money",
            "requirements": {
                "required_fields": ["delivery_phone_number__mobile_money", "provider__mobile_money"],
                "optional_fields": ["full_name", "service_provider_code__mobile_money"],
                "unique_fields": ["delivery_phone_number__mobile_money", "provider__mobile_money"],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "pre-paid_card",
            "name": "Pre-paid card",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "referral",
            "name": "Referral",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "transfer",
            "name": "Transfer",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "transfer_to_account",
            "name": "Transfer to Account",
            "requirements": {
                "required_fields": ["bank_name__transfer_to_account", "bank_account_number__transfer_to_account"],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [
                    "bank_account_number__transfer_to_account",
                ],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "voucher",
            "name": "Voucher",
            "requirements": {
                "required_fields": [],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "VOUCHER",
        },
        {
            "code": "cash_over_the_counter",
            "name": "Cash over the counter",
            "requirements": {
                "required_fields": [
                    "mobile_phone_number__cash_over_the_counter",
                ],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "atm_card",
            "name": "ATM Card",
            "requirements": {
                "required_fields": [
                    "card_number__atm_card",
                    "card_expiry_date__atm_card",
                    "name_of_cardholder__atm_card",
                ],
                "optional_fields": [
                    "full_name",
                ],
                "unique_fields": [
                    "card_number__atm_card",
                    "card_expiry_date__atm_card",
                    "name_of_cardholder__atm_card",
                ],
            },
            "transfer_type": "CASH",
        },
        {
            "code": "transfer_to_digital_wallet",
            "name": "Transfer to Digital Wallet",
            "requirements": {
                "required_fields": [
                    "blockchain_name__transfer_to_digital_wallet",
                    "wallet_address__transfer_to_digital_wallet",
                ],
                "optional_fields": ["full_name", "wallet_name__transfer_to_digital_wallet"],
                "unique_fields": [
                    "blockchain_name__transfer_to_digital_wallet",
                    "wallet_address__transfer_to_digital_wallet",
                ],
            },
            "transfer_type": "DIGITAL",
        },
    ]
    for dm in data:
        DeliveryMechanism.objects.update_or_create(
            code=dm["code"],
            defaults={
                "name": dm["name"],
                "required_fields": dm["requirements"]["required_fields"],  # type: ignore
                "optional_fields": dm["requirements"]["optional_fields"],  # type: ignore
                "unique_fields": dm["requirements"]["unique_fields"],  # type: ignore
                "transfer_type": dm["transfer_type"],
                "is_active": True,
            },
        )
