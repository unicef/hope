import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TargetingCriteriaRuleFactory,
    UserFactory,
)
from hope.apps.targeting.services.xlsx_export_targeting_service import (
    XlsxExportTargetingService,
)
from hope.models import PaymentPlan, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(business_area):
    program = ProgramFactory(
        business_area=business_area,
        name="Program Active",
        status=Program.ACTIVE,
    )
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def registration_data_import(business_area, program):
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def payment_plan(program, user):
    return PaymentPlanFactory(
        program_cycle=program.cycles.first(),
        business_area=program.business_area,
        status=PaymentPlan.Status.TP_OPEN,
        created_by=user,
    )


@pytest.fixture
def service(payment_plan):
    return XlsxExportTargetingService(payment_plan)


@pytest.fixture
def payment_1(payment_plan, registration_data_import):
    program = payment_plan.program
    individual = IndividualFactory(program=program, registration_data_import=registration_data_import, household=None)
    hh1 = HouseholdFactory(
        business_area=payment_plan.business_area,
        program=program,
        head_of_household=individual,
        registration_data_import=registration_data_import,
        size=2,
    )
    return PaymentFactory(parent=payment_plan, household=hh1, vulnerability_score=11)


@pytest.fixture
def payment_2(payment_plan, registration_data_import):
    program = payment_plan.program
    individual = IndividualFactory(program=program, registration_data_import=registration_data_import, household=None)
    hh2 = HouseholdFactory(
        business_area=payment_plan.business_area,
        program=program,
        head_of_household=individual,
        registration_data_import=registration_data_import,
        size=2,
    )
    return PaymentFactory(parent=payment_plan, household=hh2, vulnerability_score=99)


@pytest.fixture
def individual_with_accounts(program, business_area):
    household = HouseholdFactory(business_area=business_area, program=program)
    individual = IndividualFactory(
        household=household,
        program=program,
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
    )
    bank_type = AccountTypeFactory(key="bank")
    mobile_type = AccountTypeFactory(key="mobile")
    AccountFactory(
        individual=individual,
        account_type=bank_type,
        number="123",
        data={
            "card_number": "123",
            "card_expiry_date": "2022-01-01",
            "name_of_cardholder": "Marek",
        },
    )
    AccountFactory(
        individual=individual,
        account_type=mobile_type,
        number="321",
        data={
            "service_provider_code": "ABC",
            "delivery_phone_number": "123456789",
            "provider": "Provider",
        },
    )
    return individual


def test_add_version_sets_version_cells(service):
    service._create_workbook()
    service._add_version()

    assert (
        service.ws_meta[XlsxExportTargetingService.VERSION_CELL_NAME_COORDINATES].value
        == XlsxExportTargetingService.VERSION_CELL_NAME
    )
    assert (
        service.ws_meta[XlsxExportTargetingService.VERSION_CELL_COORDINATES].value == XlsxExportTargetingService.VERSION
    )


def test_add_standard_columns_headers_creates_expected_headers(service):
    service._create_workbook()
    service._add_standard_columns_headers()
    headers = [cell.value for cell in service.ws_individuals[1]]

    assert headers == [
        "Household unicef_id",
        "unicef_id",
        "Linked Households",
        "Accounts information",
    ]


def test_households_returns_all_when_plan_open(payment_plan, business_area, payment_1, payment_2):
    TargetingCriteriaRuleFactory(
        payment_plan=payment_plan,
        household_ids=f"{payment_1.household.unicef_id}, {payment_2.household.unicef_id}",
    )
    service = XlsxExportTargetingService(payment_plan)
    assert service.households.count() == 2


def test_households_respects_vulnerability_score_when_plan_locked(payment_plan, business_area, payment_1, payment_2):
    TargetingCriteriaRuleFactory(
        payment_plan=payment_plan,
        household_ids=f"{payment_1.household.unicef_id}, {payment_2.household.unicef_id}",
    )
    payment_plan.status = PaymentPlan.Status.LOCKED
    payment_plan.vulnerability_score_min = 10
    payment_plan.vulnerability_score_max = 12
    payment_plan.save()

    service = XlsxExportTargetingService(payment_plan)
    assert payment_plan.status == PaymentPlan.Status.LOCKED
    assert service.households.count() == 1
    assert service.households.first().unicef_id == payment_1.household.unicef_id


def test_accounts_info_returns_serialized_accounts(payment_plan, business_area, individual_with_accounts):
    service = XlsxExportTargetingService(payment_plan)
    assert service._accounts_info(individual_with_accounts) == (
        "{'card_number': '123', 'card_expiry_date': '2022-01-01', "
        "'name_of_cardholder': 'Marek', 'number': '123', "
        "'financial_institution_name': '', 'financial_institution_pk': ''}, "
        "{'provider': 'Provider', 'delivery_phone_number': '123456789', "
        "'service_provider_code': 'ABC', 'number': '321', "
        "'financial_institution_name': '', 'financial_institution_pk': ''}"
    )
