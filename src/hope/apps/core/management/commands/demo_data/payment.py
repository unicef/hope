from datetime import timedelta
from random import randint
from typing import Any
from uuid import UUID

from django.utils import timezone

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    CurrencyFactory,
    EntitlementCardFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PaymentFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    ProgramCycleFactory,
    RegistrationDataImportFactory,
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
)
from hope.apps.core.management.commands.demo_data.household import create_household
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import to_decimal
from hope.models import (
    MALE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    AccountType,
    Area,
    BusinessArea,
    DataCollectingType,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FinancialInstitution,
    FinancialServiceProvider,
    Household,
    Individual,
    IndividualRoleInHousehold,
    MergeStatusModel,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    Program,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    User,
)

LARGE_PP_HOUSEHOLDS = 300
LARGE_PP_PROGRESS_STEP = 25


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
    delivery_mechanisms_data: list[Any] = [
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

    generic_fis = [
        ("IBAN Provider Bank", FinancialInstitution.FinancialInstitutionType.BANK),
        ("Generic Bank", FinancialInstitution.FinancialInstitutionType.BANK),
        ("Generic Telco Company", FinancialInstitution.FinancialInstitutionType.TELCO),
    ]

    for fi_name, fi_type in generic_fis:
        FinancialInstitution.objects.get_or_create(name=fi_name, type=fi_type)


def create_tp(payment_plan: PaymentPlan) -> None:
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


def generate_payment_plan() -> None:
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
        code="t3st",
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

    usd = CurrencyFactory(code="USD", name="United States Dollar")
    payment_plan_pk = UUID("00000000-feed-beef-0000-00000badf00d")
    payment_plan = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan",
        pk=payment_plan_pk,
        business_area=afghanistan,
        currency=usd,
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        created_by=root,
        program_cycle=program_cycle,
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanism_cash,
    )[0]

    create_tp(payment_plan)

    # create primary collector role
    IndividualRoleInHouseholdFactory(household=household_1, individual=individual_1, role=ROLE_PRIMARY)
    IndividualRoleInHouseholdFactory(household=household_2, individual=individual_2, role=ROLE_PRIMARY)
    payment_1_pk = UUID("10000000-feed-beef-0000-00000badf00d")
    Payment.objects.get_or_create(
        pk=payment_1_pk,
        parent=payment_plan,
        business_area=afghanistan,
        currency=usd,
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
        currency=usd,
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
        currency=usd,
        dispersion_start_date=now,
        dispersion_end_date=now + timedelta(days=14),
        status_date=now,
        created_by=root,
        program_cycle=program_cycle,
        financial_service_provider=fsp_1,
        delivery_mechanism=delivery_mechanism_cash,
    )[0]
    PaymentPlanService(payment_plan=pp2).full_rebuild()


def create_payment_verification_plan_with_status(
    payment_plan: PaymentPlan,
    user: "User",
    business_area: BusinessArea,
    program: Program,
    status: str,
    **kwargs: Any,
) -> PaymentVerificationPlan:
    verification_channel = (kwargs.get("verification_channel"),)
    create_failed_payments = kwargs.get("create_failed_payments", False)

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

        currency = payment_plan.currency
        if currency is None:
            currency = CurrencyFactory(code="PLN", name="Polish Zloty")

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
    usd = CurrencyFactory(code="USD", name="United States Dollar")
    payment_plan = PaymentPlan.objects.update_or_create(
        name="Reconciled Payment Plan",
        unicef_id="PP-0060-22-11223344",
        business_area=afghanistan,
        currency=usd,
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
    flow = PaymentPlanFlow(payment_plan)
    flow.status_finished()
    payment_plan.save()

    create_payment_verification_plan_with_status(
        payment_plan,
        root,
        afghanistan,
        program,
        PaymentVerificationPlan.STATUS_ACTIVE,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        create_failed_payments=True,
    )
    payment_plan.update_population_count_fields()


def update_fsps() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    for fsp in FinancialServiceProvider.objects.all():
        fsp.allowed_business_areas.add(afghanistan)


def _create_hh_for_large_pp(
    program: Program,
    rdi: Any,
    size: int,
) -> tuple[Household, list[Individual]]:
    """Create one Household with ``size`` members + primary/alternate collectors, all bound to the given program/rdi.

    Bypasses ``create_household`` because that helper's collector-individual
    calls omit ``registration_data_import`` and ``IndividualFactory``'s default
    SubFactory chain would create a new RDI and Program per collector — which
    at 300 households blows past the local ES 1000-shard cap.
    """
    business_area = rdi.business_area
    household: Household = HouseholdFactory(
        program=program,
        business_area=business_area,
        registration_data_import=rdi,
        size=size,
    )
    members: list[Individual] = IndividualFactory.create_batch(
        size,
        household=household,
        program=program,
        registration_data_import=rdi,
        business_area=business_area,
    )
    members[0].relationship = "HEAD"
    members[0].save(update_fields=["relationship"])
    household.head_of_household = members[0]
    household.save(update_fields=["head_of_household"])

    primary = IndividualFactory(
        household=None,
        program=program,
        registration_data_import=rdi,
        business_area=business_area,
        relationship="NON_BENEFICIARY",
    )
    alternate = IndividualFactory(
        household=None,
        program=program,
        registration_data_import=rdi,
        business_area=business_area,
        relationship="NON_BENEFICIARY",
    )
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=primary,
        role=ROLE_PRIMARY,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    IndividualRoleInHousehold.objects.create(
        household=household,
        individual=alternate,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    return household, [*members, primary, alternate]


def generate_payment_plan_large() -> None:
    """Seed a 300-household payment plan for locally reproducing ticket 311246 (payee-list slowness)."""
    from extras.test_utils.factories import DocumentFactory
    from hope.apps.payment.services.payment_household_snapshot_service import (
        create_payment_plan_snapshot_data,
    )

    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    root = User.objects.get(username="root")
    now = timezone.now()

    data_collecting_type = DataCollectingType.objects.get(code="full_collection")
    if data_collecting_type.type == DataCollectingType.Type.SOCIAL:
        beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)
    else:
        beneficiary_group = BeneficiaryGroupFactory(name="Household", master_detail=True)

    program = Program.objects.update_or_create(
        pk=UUID("00000000-0000-0000-0000-311246000000"),
        defaults={
            "business_area": afghanistan,
            "name": "Large PP (311246 repro)",
            "start_date": now,
            "end_date": now + timedelta(days=365),
            "budget": pow(10, 6),
            "cash_plus": True,
            "population_goal": LARGE_PP_HOUSEHOLDS,
            "status": Program.ACTIVE,
            "frequency_of_payments": Program.ONE_OFF,
            "sector": Program.MULTI_PURPOSE,
            "scope": Program.SCOPE_UNICEF,
            "data_collecting_type": data_collecting_type,
            "code": "big1",
            "beneficiary_group": beneficiary_group,
        },
    )[0]
    program_cycle = ProgramCycleFactory(program=program, title="Large PP Cycle")

    rdi = RegistrationDataImportFactory(
        name="Large PP RDI (311246)",
        number_of_individuals=LARGE_PP_HOUSEHOLDS * 5,
        number_of_households=LARGE_PP_HOUSEHOLDS,
        business_area=afghanistan,
        program=program,
    )

    existing_hh = Household.objects.filter(program=program).count()
    to_seed = max(0, LARGE_PP_HOUSEHOLDS - existing_hh)
    for i in range(to_seed):
        _, individuals = _create_hh_for_large_pp(program=program, rdi=rdi, size=randint(3, 5))  # noqa: S311
        for individual in individuals:
            DocumentFactory(individual=individual, program=program)
        if (i + 1) % LARGE_PP_PROGRESS_STEP == 0 or (i + 1) == to_seed:
            pass

    dm_cash = DeliveryMechanism.objects.get(code="cash")
    fsp = FinancialServiceProvider.objects.get(name="Test FSP 1")
    usd = CurrencyFactory(code="USD", name="United States Dollar")
    payment_plan = PaymentPlan.objects.update_or_create(
        pk=UUID("bbbbbbbb-0000-0000-0000-000000311246"),
        defaults={
            "name": "Large Payment Plan (311246)",
            "business_area": afghanistan,
            "currency": usd,
            "dispersion_start_date": now,
            "dispersion_end_date": now + timedelta(days=14),
            "status_date": now,
            "created_by": root,
            "program_cycle": program_cycle,
            "financial_service_provider": fsp,
            "delivery_mechanism": dm_cash,
            "status": PaymentPlan.Status.LOCKED,
        },
    )[0]

    paid_household_ids = set(payment_plan.payment_items.values_list("household_id", flat=True))
    unpaid = Household.objects.filter(program=program).exclude(id__in=paid_household_ids)
    to_create = [
        Payment(
            parent=payment_plan,
            business_area=afghanistan,
            currency=usd,
            household=hh,
            head_of_household=hh.head_of_household,
            collector=hh.primary_collector,
            delivery_type=dm_cash,
            financial_service_provider=fsp,
            status_date=now,
            status=Payment.STATUS_PENDING,
            program=program,
        )
        for hh in unpaid
        if hh.primary_collector is not None
    ]
    if to_create:
        Payment.objects.bulk_create(to_create)
        payment_plan.update_population_count_fields()

    create_payment_plan_snapshot_data(payment_plan)
