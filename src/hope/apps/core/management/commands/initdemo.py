"""Django Management Command: initdemo.

This command initializes demo data for the application by performing the following steps:

1. **Database Setup**:
    - Waits for the default database connection to be available.
    - Optionally drops existing databases unless the `--skip-drop` flag is used.
    - Migrates the databases to apply the latest schema.
    - Flushes specified databases to remove existing data.

2. **Fixture Loading**:
    - Loads a series of JSON fixtures into the databases to populate them with initial data.
    - Rebuilds the Elasticsearch search index to ensure it's in sync with the loaded data.

3. **Data Generation**:
    - Generates additional data such as delivery mechanisms, payment plans, and reconciled payment plans.
    - Updates Financial Service Providers (FSPs) with the latest information.

4. **User Creation**:
    - Creates users based on provided email lists, assigning appropriate roles and permissions.
    - Users can be added as staff, superusers, or testers based on input.

5. **Logging and Error Handling**:
    - Logs key actions and errors to assist with debugging and monitoring the initialization process.

**Usage Examples**:

- Initialize demo data with default settings:
  ```bash
  python manage.py initdemo
  ```

- Initialize demo data without dropping existing databases:
  ```bash
  python manage.py initdemo --skip-drop
  ```

- Initialize demo data and add specific staff and tester users:
  ```bash
  python manage.py initdemo --email-list="admin@example.com,user@example.com"
   --tester-list="tester1@example.com,tester2@example.com"
  ```

**Environment Variables**:

- `INITDEMO_EMAIL_LIST`: Comma-separated list of emails to be added as staff and superusers.
- `INITDEMO_TESTER_LIST`: Comma-separated list of emails to be added as testers.
- `INITDEMO_LARGE_PAYMENT_PLAN`: When set (truthy), also generates a heavy payment plan with many payees.
"""

from argparse import ArgumentParser
from datetime import timedelta
import importlib
import logging
import os
from random import randint
import time
from typing import Any
from uuid import UUID

from constance import config
from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import Error, OperationalError, connections
from django.utils import timezone
import elasticsearch
from flags.models import FlagState

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    CommunicationMessageFactory,
    CurrencyFactory,
    DataCollectingTypeFactory,
    DocumentFactory,
    DocumentTypeFactory,
    EntitlementCardFactory,
    FeedbackFactory,
    FinancialServiceProviderFactory,
    FlexibleAttributeForPDUFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    GrievanceTicketFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    OrganizationFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    ProjectFactory,
    RegistrationDataImportFactory,
    RegistrationFactory,
    RuleCommitFactory,
    RuleFactory,
    TargetingCriteriaRuleFactory,
    TargetingCriteriaRuleFilterFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.account import create_superuser
from extras.test_utils.factories.geo import generate_area_types
from hope.apps.geo.management.commands.init_geo_fixtures import generate_areas
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import to_decimal
from hope.models import (
    MALE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    AccountType,
    Area,
    BeneficiaryGroup,
    BusinessArea,
    Country,
    CountryCodeMap,
    DataCollectingType,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FinancialInstitution,
    FinancialServiceProvider,
    FlexibleAttributeGroup,
    Household,
    Individual,
    IndividualRoleInHousehold,
    MergeStatusModel,
    Partner,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    PeriodicFieldData,
    Program,
    RegistrationDataImport,
    Role,
    RoleAssignment,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    User,
)

logger = logging.getLogger(__name__)


LARGE_PP_HOUSEHOLDS = 300
LARGE_PP_PROGRESS_STEP = 25


business_area_short_name_code_map = {
    "Analysis,Planning & Monitoring": "456C",
    "Timor-Leste": "7060",
    "Morocco": "2910",
    "Zambia": "4980",
    "Public Partnerships Division": "456I",
    "Malaysia": "2700",
    "Paraguay": "3360",
    "Nicaragua": "3120",
    "Kazakhstan": "2390",
    "Kosovo": "8971",
    "Kenya": "2400",
    "Cote D'Ivoire": "2250",
    "Albania": "0090",
    "Guinea": "1770",
    "Rep of Uzbekistan": "4630",
    "Dominican Republic": "1260",
    "Saudi Arabia": "3780",
    "Denmark": "1200",
    "EAPRO, Thailand": "420R",
    "Thailand": "4200",
    "Armenia": "0260",
    "Ecuador": "1350",
    "Liberia": "2550",
    "Democratic Republic of Congo": "0990",
    "Barbados": "0420",
    "Lebanon": "2490",
    "Angola": "6810",
    "Nepal": "2970",
    "Tajikistan": "4150",
    "El Salvador": "1380",
    "Costa Rica": "1020",
    "Evaluation Office": "456O",
    "Gabon": "1530",
    "GSSC Project": "456Q",
    "Division of Human Resources": "456K",
    "Research Division": "456E",
    "Chad": "0810",
    "Mongolia": "2880",
    "Syria": "4140",
    "LACRO, Panama": "333R",
    "Sudan": "4020",
    "Republic of Montenegro": "8950",
    "OSEB": "456S",
    "Republic of Mozambique": "6890",
    "Ukraine": "4410",
    "Yemen": "4920",
    "Turkey": "4350",
    "Division of Communication": "456G",
    "United Rep. of Tanzania": "4550",
    "Off of Global Insight & Policy": "456R",
    "Venezuela": "4710",
    "Bulgaria": "0570",
    "Executive Director's Office": "456B",
    "Croatia": "1030",
    "Belize": "6110",
    "Eswatini": "4030",
    "Azerbaijan": "0310",
    "Sierra Leone": "3900",
    "Switzerland": "5750",
    "Cambodia": "0660",
    "Mali": "2760",
    "Sri Lanka": "0780",
    "Romania": "3660",
    "Benin": "1170",
    "Georgia": "1600",
    "ROSA, Nepal": "297R",
    "Info & Comm Technology Div": "456L",
    "Oman": "6350",
    "Guinea Bissau": "6850",
    "Argentina": "0240",
    "Madagascar": "2670",
    "Office of Global Innovation": "240B",
    "Jordan": "2340",
    "Rwanda": "3750",
    "Central African Republic": "0750",
    "Lesotho": "2520",
    "Sao Tome & Principe": "6830",
    "Senegal": "3810",
    "ECARO, Switzerland": "575R",
    "Egypt": "4500",
    "Niger": "3180",
    "Somalia": "3920",
    "Nigeria": "3210",
    "Field Sup & Coordination Off": "456P",
    "Office of Research, Italy": "2220",
    "Zimbabwe": "6260",
    "Chile": "0840",
    "Malawi": "2690",
    "Botswana": "0520",
    "Eritrea": "1420",
    "Lao People's Dem Rep.": "2460",
    "Belarus": "0630",
    "Republic of Cameroon": "0690",
    "Namibia": "6980",
    "Moldova": "5640",
    "Iraq": "2130",
    "Office of Emergency Prog.": "456F",
    "Iran": "2100",
    "Papua New Guinea": "6490",
    "Maldives": "2740",
    "Burundi": "0610",
    "Panama": "3330",
    "China": "0860",
    "Mexico": "2850",
    "Vietnam": "5200",
    "Turkmenistan": "4360",
    "ESARO, Kenya": "240R",
    "Equatorial Guinea": "1390",
    "Indonesia": "2070",
    "Procurement Services": "120X",
    "India": "2040",
    "Czech Republic": "BOCZ",
    "Colombia": "0930",
    "Mauritania": "2820",
    "Bhutan": "0490",
    "Comoros": "6620",
    "Global Shared Services Centre": "1950",
    "Ethiopia": "1410",
    "Int. Audit & Invest (OIAI)": "456N",
    "Programme Division": "456D",
    "Gov. & Multilateral Affairs": "456H",
    "WCARO, Senegal": "381R",
    "Brazil": "0540",
    "DP Republic of Korea": "5150",
    "Pakistan": "3300",
    "MENA, Jordan": "234R",
    "Bangladesh": "5070",
    "Div. of Finance & Admin Mgmt": "456J",
    "Cabo Verde": "6820",
    "Jamaica": "2280",
    "Cuba": "1050",
    "Afghanistan": "0060",
    "Haiti": "1830",
    "Gambia": "1560",
    "UNICEF Hosted Funds": "456T",
    "Djibouti": "6690",
    "Tunisia": "4320",
    "South Africa": "3930",
    "Togo": "4230",
    "South Sudan": "4040",
    "Peru": "3390",
    "Bolivia": "0510",
    "Guyana": "1800",
    "Myanmar": "0600",
    "Uganda": "4380",
    "Honduras": "1860",
    "Fiji (Pacific Islands)": "1430",
    "Libya": "2580",
    "Global": "GLOBAL",
    "Palestine, State of": "7050",
    "North Macedonia": "2660",
    "Ghana": "1620",
    "Serbia": "8970",
    "Geneva Common Services": "575C",
    "Algeria": "0120",
    "Republic of Kyrgyzstan": "2450",
    "Bosnia and Herzegovina": "0530",
    "Congo": "3380",
    "Philippines": "3420",
    "Burkina Faso": "4590",
    "Russia": "3700",
    "Guatemala": "1680",
    "Uruguay": "4620",
}


def generate_unicef_partners() -> None:
    unicef_main_partner = PartnerFactory(name="UNICEF")
    PartnerFactory(name="UNICEF HQ", parent=unicef_main_partner)
    PartnerFactory(name="UNHCR")
    PartnerFactory(name="WFP")


def generate_country_codes() -> None:
    for country in Country.objects.all():
        CountryCodeMap.objects.get_or_create(country=country, defaults={"ca_code": country.iso_code3})


def generate_business_areas() -> None:
    for country_name, ba_code in business_area_short_name_code_map.items():
        if country := Country.objects.filter(short_name=country_name).first():
            business_area, _ = BusinessArea.objects.get_or_create(
                code=ba_code,
                defaults={
                    "name": country.short_name,
                    "long_name": country.name,
                    "region_code": country.iso_num,
                    "region_name": country.iso_code3,
                    "has_data_sharing_agreement": True,
                    "active": True,
                    "kobo_token": "abc_test",
                    "is_accountability_applicable": True,
                },
            )
            business_area.countries.add(country)

    # create Global
    BusinessArea.objects.get_or_create(
        code="GLOBAL",
        defaults={
            "name": "Global",
            "long_name": "Global Business Area",
            "region_code": "GLOBAL",
            "region_name": "GLOBAL",
            "has_data_sharing_agreement": True,
        },
    )


def generate_data_collecting_types() -> None:
    all_ba_id_list = BusinessArea.objects.all().values_list("id", flat=True)
    data_collecting_types = [
        {
            "label": "Partial",
            "code": "partial_individuals",
            "description": "Partial individuals collected",
            "type": DataCollectingType.Type.SOCIAL.value,
        },
        {
            "label": "Full",
            "code": "full_collection",
            "description": "Full individual collected",
            "type": DataCollectingType.Type.STANDARD.value,
        },
        {
            "label": "Size only",
            "code": "size_only",
            "description": "Size only collected",
            "type": DataCollectingType.Type.STANDARD.value,
        },
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
            "type": DataCollectingType.Type.SOCIAL.value,
        },
    ]

    for data_dict in data_collecting_types:
        dct = DataCollectingTypeFactory(
            label=data_dict["label"],
            code=data_dict["code"],
            type=data_dict["type"],
            household_filters_available=bool(data_dict["type"] == DataCollectingType.Type.STANDARD.value),
        )
        dct.limit_to.add(*all_ba_id_list)


def generate_beneficiary_groups() -> None:
    BeneficiaryGroupFactory(
        name="Household",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    BeneficiaryGroupFactory(
        name="Social Workers",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=False,
    )


def generate_people_program() -> None:
    from hope.apps.household.const import HOST, SEEING

    ba = BusinessArea.objects.get(name="Afghanistan")
    people_program = ProgramFactory(
        name="Initial_Program_People (sw)",
        status="ACTIVE",
        start_date="2023-06-19",
        end_date="2029-12-24",
        description="qwerty",
        business_area=ba,
        budget="100000.00",
        frequency_of_payments="REGULAR",
        sector="EDUCATION",
        scope="UNICEF",
        cash_plus=False,
        data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
        code="abc1",
        beneficiary_group=BeneficiaryGroup.objects.get(name="Social Workers"),
    )
    ProgramCycleFactory(
        program=people_program,
        unicef_id="PC-23-0060-000001",
        title="Default Program Cycle 1",
        status="DRAFT",
        start_date="2023-06-19",
        end_date="2023-12-24",
    )
    # add one individual
    household, individuals = create_household(
        household_args={
            "business_area": ba,
            "program": people_program,
            "residence_status": HOST,
        },
        individual_args={
            "full_name": "Stacey Freeman",
            "given_name": "Stacey",
            "middle_name": "",
            "family_name": "Freeman",
            "business_area": ba,
            "observed_disability": [SEEING],
        },
    )
    individual = individuals[0]
    DocumentFactory(individual=individual)


def generate_rdi() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    program = Program.objects.get(name="Initial_Program_People (sw)")
    user_root = User.objects.get(username="root")
    RegistrationDataImportFactory(
        name="Test people merge",
        status="MERGED",
        import_date="2022-03-30 09:22:14.870-00:00",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=7,
        number_of_households=0,
        error_message="",
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        program=program,
    )
    RegistrationDataImportFactory(
        name="test_in_review",
        status="IN_REVIEW",
        import_date="2024-06-04T13:06:23.601Z",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=10,
        number_of_households=0,
        batch_duplicates=0,
        batch_possible_duplicates=0,
        batch_unique=10,
        golden_record_duplicates=0,
        golden_record_possible_duplicates=0,
        golden_record_unique=10,
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        excluded=False,
        program=program,
        erased=False,
        refuse_reason=None,
    )


def generate_additional_doc_types() -> None:
    for doc_type_data in [
        {
            "label": "Disability Card",
            "key": "disability_card",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Medical Certificate",
            "key": "medical_certificate",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Proof of Legal Guardianship",
            "key": "proof_legal_guardianship",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Temporary Protection Visa",
            "key": "temporary_protection_visa",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Registration Token",
            "key": "registration_token",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Receiver POI",
            "key": "receiver_poi",
            "is_identity_document": False,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
    ]:
        DocumentTypeFactory(**doc_type_data)


def generate_rule_formulas() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    rule_1 = RuleFactory(
        name="Test Formula for Targeting 011",
        definition="result.value=211",
        description="",
        language="python",
        type="TARGETING",
        flags={"individual_data_needed": False},
    )
    rule_1.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_1, definition="result.value=222", language="python")
    rule_2 = RuleFactory(
        name="Test Formula for Targeting 022",
        definition="result.value=233",
        description="",
        language="python",
        type="TARGETING",
        flags={"individual_data_needed": False},
    )
    rule_2.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_2, definition="result.value=255", language="python", version=11)
    rule_3 = RuleFactory(
        name="Test Formula for Payment Plan 033",
        definition="result.value=210",
        description="",
        language="python",
        type="PAYMENT_PLAN",
        flags={"individual_data_needed": False},
    )
    rule_3.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_3, definition="result.value=212", language="python", version=22)
    rule_4 = RuleFactory(
        name="Test Formula for Payment Plan 044",
        definition="result.value=244",
        description="",
        language="python",
        type="PAYMENT_PLAN",
        flags={"individual_data_needed": False},
    )
    rule_4.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_4, definition="result.value=244", language="python", version=33)


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


def create_household(
    household_args: dict | None = None, individual_args: dict | None = None
) -> tuple[Household, list[Individual]]:
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}

    household_args["size"] = household_args.get("size", 2)
    household = HouseholdFactory(**household_args)

    individuals = IndividualFactory.create_batch(
        household.size, household=household, program=household.program, **individual_args
    )
    household.head_of_household = individuals[0]
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individuals_to_update.append(individual)

    alternate_collector_irh, _ = IndividualRoleInHousehold.objects.get_or_create(
        individual=individuals[1],
        household=household,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    return household, individuals


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
        create_failed_payments=True,  # create failed payments
    )
    payment_plan.update_population_count_fields()


def update_fsps() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    for fsp in FinancialServiceProvider.objects.all():
        fsp.allowed_business_areas.add(afghanistan)


def generate_pdu_data() -> None:
    test_program = Program.objects.get(business_area__slug="afghanistan", name="Test Program")
    group = FlexibleAttributeGroup.objects.create(name="Group 1", label={"english": "english"})
    pdu_data = PeriodicFieldData.objects.create(
        subtype="STRING",
        number_of_rounds=12,
        rounds_names=["test1", "test2", "test3..."],
    )
    FlexibleAttributeForPDUFactory(
        program=test_program,
        pdu_data=pdu_data,
        label="Test pdu 1",
        hint={"English(EN)": "Test pdu 1"},
        group=group,
    )


def generate_messages() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    user_root = User.objects.get(username="root")
    program = Program.objects.get(name="Test Program")
    households = Household.objects.filter(program=program)
    hh_1 = households.first()
    hh_2 = households.last()

    msg_data = [
        {
            "unicef_id": "MSG-22-0001",
            "title": "Hello World!",
            "body": "World is beautiful, don't mess with it!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0004",
            "title": "You got credit of USD 200",
            "body": "Greetings {recipient_full_name}, we have sent you USD 200 in your registered account on "
            "{rp_timestamp}",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 80.0,
                "confidence_interval": 0.8,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0002",
            "title": "Hello There!",
            "body": "Hey, there. Welcome to the party!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "RANDOM",
            "full_list_arguments": None,
            "random_sampling_arguments": {
                "age": {"max": 2, "min": 1},
                "sex": "any",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "sample_size": 0,
        },
        {
            "unicef_id": "MSG-22-0003",
            "title": "We hold your back!",
            "body": "Hey XYZ, don't be worry. We UNICEF are here to help to grow!",
            "created_by": user_root,
            "program": program,
            "number_of_recipients": 2,
            "business_area": ba,
            "registration_data_import": None,
            "sampling_type": "FULL_LIST",
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": None,
            "sample_size": 2,
        },
    ]
    for msg in msg_data:
        msg_obj = CommunicationMessageFactory(**msg)
        msg_obj.households.set([hh_1, hh_2])


def generate_feedback() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    feedback_data = [
        {
            "business_area": ba,
            "issue_type": "POSITIVE_FEEDBACK",
            "description": "Positive Feedback",
        },
        {
            "business_area": ba,
            "issue_type": "NEGATIVE_FEEDBACK",
            "description": "Negative Feedback",
        },
    ]
    feedback_positive = FeedbackFactory(**feedback_data[0])
    feedback_positive.unicef_id = "FED-23-0001"
    feedback_positive.save()
    feedback_negative = FeedbackFactory(**feedback_data[1])
    feedback_negative.unicef_id = "FED-23-0002"
    feedback_negative.save()


def generate_aurora_test_data() -> None:
    program = Program.objects.get(name="Test Program")
    ukr_org = OrganizationFactory(
        source_id=1,
        name="organization_ukraine",
        slug="ukraine",
        business_area=BusinessAreaFactory(name="Ukraine"),
    )

    czech_org = OrganizationFactory(
        source_id=1,
        name="organization_czech_republic",
        slug="czech-republic",
        business_area=BusinessAreaFactory(name="Czechia"),
    )
    sri_lanka_org = OrganizationFactory(
        source_id=1,
        name="organization_sri_lanka",
        slug="sri-lanka",
        business_area=BusinessAreaFactory(name="Sri Lanka"),
    )
    ukr_project = ProjectFactory(source_id=2, organization=ukr_org, programme=program, name="project_ukraine")
    czech_project = ProjectFactory(
        source_id=2,
        organization=czech_org,
        programme=program,
        name="project_czech_republic",
    )
    sri_lanka_project = ProjectFactory(
        source_id=2,
        organization=sri_lanka_org,
        programme=program,
        name="project_sri_lanka",
    )
    RegistrationFactory(source_id=2, project=ukr_project, name="registration_ukraine", slug="ukraine")
    RegistrationFactory(
        source_id=2,
        project=czech_project,
        name="registration_czech_republic",
        slug="czech-republic",
    )
    RegistrationFactory(
        source_id=2,
        project=sri_lanka_project,
        name="registration_sri_lanka",
        slug="sri-lanka",
    )


def generate_fake_grievances() -> None:
    program = Program.objects.get(name="Test Program")
    admin2 = Area.objects.filter(area_type__area_level=2).first()
    ind_qs = Individual.objects.filter(household__program=program)
    golden_records_individual = ind_qs[0]
    jan1 = ind_qs[1]
    jan2 = ind_qs[2]
    ba = program.business_area
    rdi = RegistrationDataImport.objects.filter(business_area=ba).first()
    grievance = GrievanceTicketFactory(
        unicef_id="GRV-0000001",
        status=1,
        category=8,
        issue_type=23,
        description="Test description",
        admin2=admin2,
        consent=True,
        business_area=ba,
        registration_data_import=rdi,
        extras={},
        ignored=False,
        household_unicef_id="HH-20-0000.0014",
    )
    grievance.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden_records_individual,
        is_multiple_duplicates_version=True,
        possible_duplicate=golden_records_individual,
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak1",
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                },
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan2.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak2",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": True,
                },
            ],
        },
        score_min=9.0,
        score_max=9.0,
    )
    ticket_details.possible_duplicates.set([jan1, jan2])
    ticket_details.selected_individuals.set([jan2])
    ticket_details.selected_distinct.set([golden_records_individual])


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
    from hope.models import ROLE_ALTERNATE, IndividualRoleInHousehold

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


class Command(BaseCommand):
    help = "Initialize demo data for the application."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            default=False,
            help="Skip migrating - just reload the data",
        )
        parser.add_argument(
            "--email-list",
            type=str,
            help="Comma-separated list of emails to be added as staff and superusers",
        )
        parser.add_argument(
            "--tester-list",
            type=str,
            help="Comma-separated list of emails to be added as testers",
        )

    def _wait_for_database(self) -> None:
        db_connection = connections["default"]
        connected = False
        self.stdout.write("Waiting for database connection...")
        while not connected:
            try:
                db_connection.cursor()
                connected = True
            except OperationalError:
                connected = False
                time.sleep(0.5)

    def _setup_base_fixtures(self) -> User:
        self.stdout.write("Loading fixtures...")
        self.stdout.write("Seeding currencies...")
        migration = importlib.import_module("hope.apps.core.migrations.0020_migration")
        migration.seed_currencies(apps, None)
        call_command("generateroles")
        generate_unicef_partners()
        call_command("loadcountries")
        generate_country_codes()
        generate_business_areas()
        self.stdout.write("Creating superuser...")
        user = create_superuser()
        call_command("generatedocumenttypes")
        role_with_all_perms = Role.objects.get(name="Role with all permissions")
        for ba_name in ["Global", "Afghanistan"]:
            RoleAssignment.objects.get_or_create(
                user=user,
                role=role_with_all_perms,
                business_area=BusinessArea.objects.get(name=ba_name),
            )
        return user

    def _generate_demo_data(self) -> None:
        self.stdout.write("Generating programs...")
        generate_people_program()
        self.stdout.write("Generating RDIs...")
        generate_rdi()
        self.stdout.write("Generating additional document types...")
        generate_additional_doc_types()
        self.stdout.write("Generating Engine core ...")
        generate_rule_formulas()
        try:
            self.stdout.write("Rebuilding search index...")
            call_command("search_index", "--rebuild", "-f")
        except elasticsearch.exceptions.RequestError as e:
            logger.warning(f"Elasticsearch RequestError: {e}")
        self.stdout.write("Generating delivery mechanisms...")
        generate_delivery_mechanisms()
        self.stdout.write("Generating payment plan...")
        generate_payment_plan()
        self.stdout.write("Generating real cash plans...")
        self.stdout.write("Generating reconciled payment plan...")
        generate_reconciled_payment_plan()
        if os.getenv("INITDEMO_LARGE_PAYMENT_PLAN"):
            self.stdout.write("Generating large payment plan...")
            generate_payment_plan_large()
        self.stdout.write("Updating FSPs...")
        update_fsps()
        self.stdout.write("Loading additional fixtures...")
        generate_pdu_data()
        self.stdout.write("Generating messages...")
        generate_messages()
        generate_feedback()
        self.stdout.write("Generating aurora test data...")
        generate_aurora_test_data()
        self.stdout.write("Generating grievances...")
        generate_fake_grievances()

    def _create_users_from_email_lists(
        self, email_list: list[str], tester_list: list[str], role_with_all_perms: Role
    ) -> None:
        if not email_list and not tester_list:
            self.stdout.write("No email lists provided. Skipping user creation.")
            return

        afghanistan = BusinessArea.objects.get(slug="afghanistan")
        partner = Partner.objects.get(name="UNICEF")
        unicef_hq = Partner.objects.get(name=settings.UNICEF_HQ_PARTNER, parent=partner)
        combined_email_list: list[str] = [email.strip() for email in email_list + tester_list if email.strip()]

        if combined_email_list:
            self.stdout.write("Creating users...")
            for email in combined_email_list:
                try:
                    user = User.objects.create_user(email, email, "password", partner=unicef_hq)
                    RoleAssignment.objects.create(
                        user=user,
                        role=role_with_all_perms,
                        business_area=afghanistan,
                    )
                    if email in email_list:
                        user.is_staff = True
                        user.is_superuser = True
                    user.set_unusable_password()
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Created user: {email}"))
                except Error as e:
                    logger.warning(f"Failed to create user {email}: {e}")

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = timezone.now()

        self._wait_for_database()

        config.IS_ELASTICSEARCH_ENABLED = True

        if not options["skip_drop"]:
            self.stdout.write("Dropping existing databases...")
            call_command("dropalldb")
            self.stdout.write("Migrating database...")
            call_command("migrate")

        self.stdout.write("Flushing databases...")
        call_command("flush", "--noinput")

        self._setup_base_fixtures()
        role_with_all_perms = Role.objects.get(name="Role with all permissions")

        # Create role for WFP and UNHCR in Afghanistan
        role_planner = Role.objects.get(name="Planner")
        wfp_partner = Partner.objects.get(name="WFP")
        unhcr_partner = Partner.objects.get(name="UNHCR")
        afghanistan = BusinessArea.objects.get(slug="afghanistan")
        for partner in [wfp_partner, unhcr_partner]:
            partner.allowed_business_areas.add(afghanistan)
            RoleAssignment.objects.get_or_create(partner=partner, role=role_planner, business_area=afghanistan)

        # Geo app
        generate_area_types()
        generate_areas(country_names=["Afghanistan", "Croatia", "Ukraine"])
        # Core app
        generate_data_collecting_types()
        FlagState.objects.get_or_create(
            name="ALLOW_ACCOUNTABILITY_MODULE",
            condition="boolean",
            value="True",
            required=False,
        )
        generate_beneficiary_groups()

        self._generate_demo_data()

        email_list_env = os.getenv("INITDEMO_EMAIL_LIST")
        tester_list_env = os.getenv("INITDEMO_TESTER_LIST")
        email_list = (
            options["email_list"].split(",")
            if options.get("email_list")
            else email_list_env.split(",")
            if email_list_env
            else []
        )
        tester_list = (
            options["tester_list"].split(",")
            if options.get("tester_list")
            else tester_list_env.split(",")
            if tester_list_env
            else []
        )
        self._create_users_from_email_lists(email_list, tester_list, role_with_all_perms)

        self.stdout.write(self.style.SUCCESS(f"Done in {timezone.now() - start_time}"))
