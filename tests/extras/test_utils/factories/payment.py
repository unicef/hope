import random
import string
from datetime import timedelta
from decimal import Decimal
from random import randint
from typing import Any, Optional
from uuid import UUID

import factory
from django.utils import timezone
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import (
    EntitlementCardFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household,
)
from extras.test_utils.factories.program import (
    BeneficiaryGroupFactory,
    ProgramCycleFactory,
)
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.targeting import (
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
)
from factory.django import DjangoModelFactory
from pytz import utc

from hope.apps.account.models import User
from hope.apps.core.currencies import CURRENCY_CHOICES
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.geo.models import Area
from hope.apps.household.models import MALE, ROLE_PRIMARY, Household, Individual
from hope.apps.payment.models import (
    Account,
    AccountType,
    Approval,
    ApprovalProcess,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FinancialInstitution,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import to_decimal
from hope.apps.program.models import Program
from hope.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)
from hope.apps.utils.models import MergeStatusModel


def update_kwargs_with_usd_currency(kwargs: Any) -> Any:
    currency = kwargs.get("currency", "USD")
    if currency == "USD":
        kwargs["entitlement_quantity"] = kwargs["entitlement_quantity_usd"]
        kwargs["delivered_quantity"] = kwargs["delivered_quantity_usd"]
    return kwargs


class PaymentVerificationSummaryFactory(DjangoModelFactory):
    class Meta:
        model = PaymentVerificationSummary


class DeliveryMechanismFactory(DjangoModelFactory):
    payment_gateway_id = factory.Faker("uuid4")
    code = factory.Faker("uuid4")
    name = factory.Faker("sentence", nb_words=4, variable_nb_words=True, ext_word_list=None)
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


class PaymentVerificationPlanFactory(DjangoModelFactory):
    payment_plan = factory.SubFactory("extras.test_utils.factories.payment.PaymentPlanFactory")
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
    payment = factory.SubFactory("extras.test_utils.factories.payment.PaymentFactory")
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
    programme_code = factory.LazyAttribute(lambda o: RealProgramFactory.generate_programme_code(o))
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    beneficiary_group = factory.LazyAttribute(
        lambda o: BeneficiaryGroupFactory(
            master_detail=bool(o.data_collecting_type.type != DataCollectingType.Type.SOCIAL),
            name=(
                factory.Faker("word") if o.data_collecting_type.type == DataCollectingType.Type.SOCIAL else "Household"
            ),
        )
    )

    @staticmethod
    def generate_programme_code(obj: Any) -> str:
        programme_code = "".join(random.choice(string.ascii_uppercase + string.digits + "-") for _ in range(4))
        if Program.objects.filter(business_area_id=obj.business_area.id, programme_code=programme_code).exists():
            return RealProgramFactory.generate_programme_code(obj)
        return programme_code

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return
        ProgramCycleFactory(program=self, **kwargs)


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
    status = PaymentPlan.Status.OPEN
    build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
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
    program_cycle = factory.SubFactory(ProgramCycleFactory)
    currency = factory.fuzzy.FuzzyChoice(CURRENCY_CHOICES, getter=lambda c: c[0])

    dispersion_start_date = factory.Faker("date_this_year", before_today=True, after_today=False)
    dispersion_end_date = factory.LazyAttribute(lambda o: o.dispersion_start_date + timedelta(days=randint(365, 1000)))
    female_children_count = factory.fuzzy.FuzzyInteger(2, 4)
    male_children_count = factory.fuzzy.FuzzyInteger(2, 4)
    female_adults_count = factory.fuzzy.FuzzyInteger(2, 4)
    male_adults_count = factory.fuzzy.FuzzyInteger(2, 4)
    total_households_count = factory.fuzzy.FuzzyInteger(2, 4)
    total_individuals_count = factory.fuzzy.FuzzyInteger(8, 16)
    name = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)


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
    status = Payment.STATUS_PENDING
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
                household=o.household,
                individual=o.household.head_of_household,
                role=ROLE_PRIMARY,
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
    has_valid_wallet = True

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


class AccountTypeFactory(DjangoModelFactory):
    key = factory.Faker("uuid4")
    label = factory.Faker("name")

    class Meta:
        model = AccountType


class AccountFactory(DjangoModelFactory):
    individual = factory.SubFactory(IndividualFactory)
    account_type = factory.SubFactory(AccountTypeFactory)
    rdi_merge_status = MergeStatusModel.MERGED

    class Meta:
        model = Account


class PendingAccountFactory(AccountFactory):
    rdi_merge_status = MergeStatusModel.PENDING

    class Meta:
        model = Account


def create_payment_verification_plan_with_status(
    payment_plan: PaymentPlan,
    user: "User",
    business_area: BusinessArea,
    program: Program,
    status: str,
    verification_channel: Optional[str] = None,
    create_failed_payments: bool = False,
) -> PaymentVerificationPlan:
    if not hasattr(payment_plan, "payment_verification_summary"):
        PaymentVerificationSummary.objects.create(payment_plan=payment_plan)

    payment_verification_plan = PaymentVerificationPlanFactory(payment_plan=payment_plan)
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
                "admin2": Area.objects.order_by("?").first(),
                "program": program,
            },
            {"registration_data_import": registration_data_import},
        )

        currency = getattr(payment_plan, "currency", None)
        if currency is None:
            currency = "PLN"

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
            parent=payment_plan,
            household=household,
            currency=currency,
            **additional_args,
        )

        pv = PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment_record,
            status=PaymentVerification.STATUS_PENDING,
        )
        pv.set_pending()
        pv.save()
        EntitlementCardFactory(household=household)
    return payment_verification_plan


def generate_reconciled_payment_plan() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    root = User.objects.get(username="root")
    now = timezone.now()
    program = Program.objects.filter(business_area=afghanistan, name="Test Program").first()
    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp_1 = FinancialServiceProviderFactory()
    fsp_1.delivery_mechanisms.set([dm_cash])
    FspXlsxTemplatePerDeliveryMechanismFactory(financial_service_provider=fsp_1)
    payment_plan = PaymentPlan.objects.update_or_create(
        name="Reconciled Payment Plan",
        unicef_id="PP-0060-22-11223344",
        business_area=afghanistan,
        currency="USD",
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        status=PaymentPlan.Status.ACCEPTED,
        created_by=root,
        program_cycle=program.cycles.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        exchange_rate=234.6742,
        financial_service_provider=fsp_1,
        delivery_mechanism=dm_cash,
    )[0]
    # update status
    payment_plan.status_finished()
    payment_plan.save()

    create_payment_verification_plan_with_status(
        payment_plan,
        root,
        afghanistan,
        program,
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
    data_collecting_type = DataCollectingType.objects.get(code="full_collection")
    if data_collecting_type.type == DataCollectingType.Type.SOCIAL:
        beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)
    else:
        beneficiary_group = BeneficiaryGroupFactory(name="Household", master_detail=True)
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
        data_collecting_type=data_collecting_type,
        programme_code="T3ST",
        beneficiary_group=beneficiary_group,
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
        rdi_merge_status=MergeStatusModel.MERGED,
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
        rdi_merge_status=MergeStatusModel.MERGED,
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
        rdi_merge_status=MergeStatusModel.MERGED,
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
        rdi_merge_status=MergeStatusModel.MERGED,
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

    delivery_mechanism_cash = DeliveryMechanism.objects.get(code="cash")

    fsp_1_pk = UUID("00000000-0000-0000-0000-f00000000001")
    fsp_1 = FinancialServiceProvider.objects.update_or_create(
        pk=fsp_1_pk,
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number=123456789,
    )[0]
    fsp_1.delivery_mechanisms.add(delivery_mechanism_cash)

    fsp_api = FinancialServiceProvider.objects.update_or_create(
        name="Test FSP API",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        vision_vendor_number=554433,
    )[0]
    fsp_api.delivery_mechanisms.add(delivery_mechanism_cash)

    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_1, delivery_mechanism=delivery_mechanism_cash
    )

    payment_plan_pk = UUID("00000000-feed-beef-0000-00000badf00d")
    payment_plan = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan",
        pk=payment_plan_pk,
        business_area=afghanistan,
        currency="USD",
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        created_by=root,
        program_cycle=program_cycle,
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanism_cash,
    )[0]

    targeting_criteria_rule_pk = UUID("00000000-0000-0000-0000-feedb00c0009")
    targeting_criteria_rule = TargetingCriteriaRule.objects.update_or_create(
        pk=targeting_criteria_rule_pk,
        payment_plan=payment_plan,
    )[0]

    targeting_criteria_rule_condition_pk = UUID("00000000-0000-0000-0000-feedb00c0008")
    TargetingCriteriaRuleFilter.objects.update_or_create(
        pk=targeting_criteria_rule_condition_pk,
        targeting_criteria_rule=targeting_criteria_rule,
        comparison_method="CONTAINS",
        field_name="registration_data_import",
        arguments=["4d100000-0000-0000-0000-000000000000"],
    )
    tcr2 = TargetingCriteriaRuleFactory(
        payment_plan=payment_plan,
    )
    TargetingCriteriaRuleFilterFactory(
        targeting_criteria_rule=tcr2,
        comparison_method="RANGE",
        field_name="size",
        arguments=[1, 11],
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
    # add one more PP
    pp2 = PaymentPlan.objects.update_or_create(
        name="Test TP for PM (just click rebuild)",
        status=PaymentPlan.Status.TP_OPEN,
        business_area=afghanistan,
        currency="USD",
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        created_by=root,
        program_cycle=program_cycle,
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanism_cash,
    )[0]
    PaymentPlanService(payment_plan=pp2).full_rebuild()


def update_fsps() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    for fsp in FinancialServiceProvider.objects.all():
        fsp.allowed_business_areas.add(afghanistan)


def generate_delivery_mechanisms() -> None:
    account_types_data = [
        {
            "payment_gateway_id": "123",
            "key": "bank",
            "label": "Bank",
            "unique_fields": [
                "number",
            ],
        },
        {
            "payment_gateway_id": "456",
            "key": "mobile",
            "label": "Mobile",
            "unique_fields": [
                "number",
            ],
        },
    ]
    for at in account_types_data:
        AccountType.objects.update_or_create(
            key=at["key"],
            defaults={
                "label": at["label"],
                "unique_fields": at["unique_fields"],
                "payment_gateway_id": at["payment_gateway_id"],
            },
        )
    account_types = {at.key: at for at in AccountType.objects.all()}
    delivery_mechanisms_data = [
        {
            "code": "cardless_cash_withdrawal",
            "name": "Cardless cash withdrawal",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {"code": "cash", "name": "Cash", "transfer_type": "CASH", "account_type": None},
        {
            "code": "cash_by_fsp",
            "name": "Cash by FSP",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "cheque",
            "name": "Cheque",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "deposit_to_card",
            "name": "Deposit to Card",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "mobile_money",
            "name": "Mobile Money",
            "transfer_type": "CASH",
            "account_type": account_types["mobile"],
            "required_fields": [
                "number",
                "provider",
                "service_provider_code",
            ],
        },
        {
            "code": "pre-paid_card",
            "name": "Pre-paid card",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "referral",
            "name": "Referral",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "transfer",
            "name": "Transfer",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
        },
        {
            "code": "transfer_to_account",
            "name": "Transfer to Account",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
            "required_fields": ["name", "number", "code"],
        },
        {
            "code": "voucher",
            "name": "Voucher",
            "transfer_type": "VOUCHER",
            "account_type": account_types["bank"],
        },
        {
            "code": "cash_over_the_counter",
            "name": "Cash over the counter",
            "transfer_type": "CASH",
            "account_type": None,
        },
        {
            "code": "atm_card",
            "name": "ATM Card",
            "transfer_type": "CASH",
            "account_type": account_types["bank"],
            "required_fields": [
                "number",
                "expiry_date",
                "name_of_cardholder",
            ],
        },
        {
            "code": "transfer_to_digital_wallet",
            "name": "Transfer to Digital Wallet",
            "transfer_type": "DIGITAL",
            "account_type": account_types["bank"],
        },
    ]
    for dm in delivery_mechanisms_data:
        delivery_mechanism, _ = DeliveryMechanism.objects.update_or_create(
            code=dm["code"],
            defaults={
                "name": dm["name"],
                "transfer_type": dm["transfer_type"],
                "is_active": True,
                "account_type": dm["account_type"],
            },
        )
        for fsp in FinancialServiceProvider.objects.all():
            DeliveryMechanismConfig.objects.get_or_create(
                fsp=fsp,
                delivery_mechanism=delivery_mechanism,
                required_fields=dm.get("required_fields", []),
            )
        FinancialServiceProvider.objects.get_or_create(
            name="United Bank for Africa - Nigeria",
            vision_vendor_number="2300117733",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        )


class FinancialInstitutionFactory(DjangoModelFactory):
    country = factory.SubFactory(CountryFactory)

    class Meta:
        model = FinancialInstitution
