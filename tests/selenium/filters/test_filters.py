from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.models import PaymentVerification as PV
from hct_mis_api.apps.payment.models import PaymentVerificationPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import ImportData, RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from tests.selenium.page_object.filters import Filters
from tests.selenium.page_object.grievance.details_grievance_page import (
    GrievanceDetailsPage,
)
from tests.selenium.page_object.grievance.grievance_tickets import GrievanceTickets
from tests.selenium.page_object.grievance.new_ticket import NewTicket
from tests.selenium.page_object.programme_details.programme_details import (
    ProgrammeDetails,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_payment_plan() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    targeting_criteria = TargetingCriteriaFactory()
    targeting_criteria_2 = TargetingCriteriaFactory()
    program_1 = ProgramFactory(business_area=ba)
    program_2 = ProgramFactory(business_area=ba)

    pp = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan 1",
        unicef_id="PP-0060-22-11223344",
        business_area=ba,
        targeting_criteria=targeting_criteria,
        start_date=datetime.now(),
        end_date=datetime.now() + relativedelta(days=30),
        currency="USD",
        dispersion_start_date=datetime.now(),
        dispersion_end_date=datetime.now() + relativedelta(days=14),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        program_cycle=program_1.cycles.first(),
    )
    pp[0].unicef_id = "PP-0060-22-11223344"
    pp[0].save()

    PaymentPlan.objects.update_or_create(
        name="Test Payment Plan 2",
        business_area=ba,
        targeting_criteria=targeting_criteria_2,
        start_date=datetime.now(),
        end_date=datetime.now() + relativedelta(days=30),
        currency="USD",
        dispersion_start_date=datetime.now(),
        dispersion_end_date=datetime.now() + relativedelta(days=14),
        status_date=datetime.now(),
        status=PaymentPlan.Status.ACCEPTED,
        created_by=User.objects.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
        program_cycle=program_2.cycles.first(),
    )


@pytest.fixture
def add_grievance_tickets() -> None:
    create_grievance("GRV-0000123")
    create_grievance("GRV-0000666")


def create_grievance(name: str, program: str = "Test Programm", business_area_slug: str = "afghanistan") -> None:
    business_area = BusinessArea.objects.get(slug=business_area_slug)
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    grievance.programs.add(Program.objects.filter(name=program).first())
    grievance.unicef_id = name
    grievance.save()


def generate_grievance(
    unicef_id: str,
    status: int = GrievanceTicket.STATUS_NEW,
    category: int = GrievanceTicket.CATEGORY_REFERRAL,
    created_by: User | None = None,
    assigned_to: User | None = None,
    business_area: BusinessArea | None = None,
    priority: int = 1,
    urgency: int = 1,
    household_unicef_id: str = "HH-20-0000.0001",
    updated_at: str = "2023-09-27T11:26:33.846Z",
    created_at: str = "2022-04-30T09:54:07.827000",
) -> None:
    created_by = User.objects.first() if created_by is None else created_by
    assigned_to = User.objects.first() if assigned_to is None else assigned_to
    business_area = BusinessArea.objects.filter(slug="afghanistan").first() if business_area is None else business_area
    GrievanceTicket.objects.create(
        **{
            "business_area": business_area,
            "unicef_id": unicef_id,
            "language": "Polish",
            "consent": True,
            "description": "grievance_ticket_1",
            "category": category,
            "status": status,
            "created_by": created_by,
            "assigned_to": assigned_to,
            "created_at": created_at,
            "updated_at": updated_at,
            "household_unicef_id": household_unicef_id,
            "priority": priority,
            "urgency": urgency,
        }
    )


@pytest.fixture
def add_household() -> None:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    household, _ = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin2": Area.objects.order_by("?").first(),
            "program": Program.objects.filter(name="Test Programm").first(),
        },
        {"registration_data_import": registration_data_import},
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()


def payment_verification_creator(
    channel: str = PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL, payment_plan_id: str = "PP-0060-22-11223344"
) -> PV:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    program = Program.objects.filter(name="Test Programm").first()
    household, individuals = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin2": Area.objects.order_by("?").first(),
            "program": program,
        },
        {"registration_data_import": registration_data_import},
    )

    payment_plan = PaymentPlanFactory(
        name="TEST",
        status=PaymentPlan.Status.FINISHED,
        program_cycle=program.cycles.first(),
        business_area=BusinessArea.objects.first(),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )

    payment_plan.unicef_id = payment_plan_id
    payment_plan.save()

    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=household.head_of_household,
        entitlement_quantity=21.36,
        delivered_quantity=21.36,
        currency="PLN",
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    pv_summary = PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    pv_summary.activation_date = datetime.now() - relativedelta(months=1)
    pv_summary.save()
    payment_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=payment_plan,
        verification_channel=channel,
    )
    pv = PaymentVerificationFactory(
        payment=payment,
        payment_verification_plan=payment_verification_plan,
        status=PV.STATUS_PENDING,
    )
    return pv


@pytest.fixture
def add_payment_verification() -> None:
    payment_verification_creator(payment_plan_id="PP-0060-22-11223344")
    payment_verification_creator(payment_plan_id="PP-0000-00-11223344")


@pytest.fixture
def create_targeting() -> None:
    user = User.objects.first()
    business_area = BusinessArea.objects.get(slug="afghanistan")
    PaymentPlanFactory(
        name="Test",
        created_by=user,
        targeting_criteria=TargetingCriteriaFactory(),
        business_area=business_area,
        status=PaymentPlan.Status.TP_OPEN,
    )
    PaymentPlanFactory(
        name="Targeting 2",
        created_by=user,
        targeting_criteria=TargetingCriteriaFactory(),
        business_area=business_area,
        status=PaymentPlan.Status.TP_OPEN,
    )


@pytest.fixture
def create_rdi() -> None:
    business_area = BusinessArea.objects.get(slug="afghanistan")
    programme = Program.objects.filter(name="Test Programm").first()
    imported_by = User.objects.first()
    number_of_individuals = 0
    number_of_households = 0
    status = RegistrationDataImport.IMPORTING

    import_data = ImportData.objects.create(
        status=ImportData.STATUS_PENDING,
        business_area_slug=business_area.slug,
        data_type=ImportData.FLEX_REGISTRATION,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        created_by_id=imported_by.id if imported_by else None,
    )
    RegistrationDataImport.objects.create(
        name="Test",
        data_source=RegistrationDataImport.FLEX_REGISTRATION,
        imported_by=imported_by,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        business_area=business_area,
        status=status,
        program=programme,
        import_data=import_data,
    )

    RegistrationDataImport.objects.create(
        name="RDI magic",
        data_source=RegistrationDataImport.FLEX_REGISTRATION,
        imported_by=imported_by,
        number_of_individuals=number_of_individuals,
        number_of_households=number_of_households,
        business_area=business_area,
        status=status,
        program=programme,
    )


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.mark.usefixtures("login")
class TestSmokeFilters:
    @pytest.mark.xfail(reason="UNSTABLE")
    def test_filters_selected_program(self, create_programs: None, filters: Filters) -> None:
        filters.selectGlobalProgramFilter("Test Programm")

        programs = {
            "Registration Data Import": [
                filters.filterSearch,
                filters.importedByInput,
                filters.selectFilter,
                filters.filterStatus,
                filters.filterSizeMin,
                filters.filterSizeMax,
                filters.filterImportDateRangeMin,
                filters.filterImportDateRangeMax,
            ],
            "Main Menu": [
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.hhFiltersResidenceStatus,
                filters.hhFiltersAdmin2,
                filters.hhFiltersHouseholdSizeFrom,
                filters.hhFiltersHouseholdSizeTo,
                filters.selectFilter,
                filters.hhFiltersOrderBy,
                filters.selectFilter,
                filters.hhFiltersStatus,
            ],
            "Items": [
                filters.indFiltersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.indFiltersGender,
                filters.indFiltersAgeFrom,
                filters.indFiltersAgeTo,
                filters.selectFilter,
                filters.indFiltersFlags,
                filters.selectFilter,
                filters.indFiltersOrderBy,
                filters.selectFilter,
                filters.indFiltersStatus,
                filters.indFiltersRegDateFrom,
                filters.indFiltersRegDateTo,
            ],
            "Targeting": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersTotalHouseholdsCountMin,
                filters.filtersTotalHouseholdsCountMax,
                filters.datePickerFilterFrom,
                filters.datePickerFilterTo,
            ],
            "Payment Plans": [
                filters.selectFilter,
                filters.filtersTotalEntitledQuantityFrom,
                filters.filtersTotalEntitledQuantityTo,
                filters.datePickerFilterFrom,
                filters.datePickerFilterTo,
            ],
            "Payment Verification": [
                filters.filterSearch,
                filters.selectFilter,
                filters.filterStatus,
                filters.filterFsp,
                filters.selectFilter,
                filters.filterModality,
                filters.filterStartDate,
                filters.filterEndDate,
            ],
            "Grievance": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersFsp,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersCategory,
                filters.filtersAdminLevel,
                filters.filtersAssignee,
                filters.assignedToInput,
                filters.filtersCreatedByAutocomplete,
                filters.filtersRegistrationDataImport,
                filters.filtersPreferredLanguage,
                filters.filtersPriority,
                filters.filtersUrgency,
                filters.filtersActiveTickets,
            ],
            "Feedback": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersIssueType,
                filters.filtersCreatedByAutocomplete,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            "Accountability": [
                filters.filtersTargetPopulationAutocomplete,
                filters.targetPopulationInput,
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            "Surveys": [
                filters.filtersSearch,
                filters.filtersTargetPopulationAutocomplete,
                filters.targetPopulationInput,
                filters.createdByInput,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
            ],
            "Programme Users": [],
            "Programme Log": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersResidenceStatus,
                filters.userInput,
            ],
        }

        for nav_menu in programs:
            if nav_menu == "Feedback":
                filters.wait_for('[data-cy="nav-Grievance"]').click()
            if nav_menu == "Items":
                filters.wait_for('[data-cy="nav-Main Menu"]').click()
            if nav_menu == "Surveys":
                filters.wait_for('[data-cy="nav-Accountability"]').click()
            if nav_menu == "Payment Plans":
                filters.wait_for('[data-cy="nav-Payment Module"]').click()

            filters.wait_for(f'[data-cy="nav-{nav_menu}"]').click()

            for locator in programs[nav_menu]:
                try:
                    print(nav_menu, locator)
                    filters.wait_for(locator, timeout=20)
                except BaseException:
                    raise Exception(f"Element {locator} not found on the {nav_menu} page.")

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_filters_all_programs(self, create_programs: None, filters: Filters) -> None:
        all_programs = {
            "Country Dashboard": [filters.globalProgramFilter, filters.globalProgramFilterContainer],
            "Programmes": [
                filters.filtersDataCollectingType,
                filters.filtersBudgetMax,
                filters.filtersBudgetMin,
                filters.filtersNumberOfHouseholdsMin,
                filters.filtersNumberOfHouseholdsMax,
                filters.filtersSector,
                filters.filtersStartDate,
                filters.filtersEndDate,
                filters.filtersStatus,
                filters.filtersSearch,
            ],
            "Grievance": [
                filters.filtersSearch,
                filters.selectFilter,
                filters.filtersDocumentType,
                filters.filtersDocumentNumber,
                filters.filtersProgram,
                filters.programmeInput,
                filters.selectFilter,
                filters.filtersStatus,
                filters.filtersFsp,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersCategory,
                filters.filtersAdminLevel,
                filters.filtersAssignee,
                filters.assignedToInput,
                filters.filtersCreatedByAutocomplete,
                filters.filtersRegistrationDataImport,
                filters.filtersPreferredLanguage,
                filters.filtersPriority,
                filters.filtersUrgency,
                filters.filtersActiveTickets,
                filters.filtersProgramState,
            ],
            "Feedback": [
                filters.filtersSearch,
                filters.filtersProgram,
                filters.programmeInput,
                filters.selectFilter,
                filters.filtersIssueType,
                filters.filtersCreatedByAutocomplete,
                filters.filtersCreationDateFrom,
                filters.filtersCreationDateTo,
                filters.selectFilter,
                filters.filtersProgramState,
            ],
            "Activity Log": [
                filters.filtersResidenceStatus,
                filters.filtersSearch,
                filters.userInput,
                filters.selectFilter,
            ],
        }

        for nav_menu in all_programs:
            filters.wait_for(f'[data-cy="nav-{nav_menu}"]').click()
            for locator in all_programs[nav_menu]:
                try:
                    filters.wait_for(locator, timeout=20)
                except BaseException:
                    raise Exception(f"Element {locator} not found on the {nav_menu} page.")

    @pytest.mark.xfail(reason="UNSTABLE")
    @pytest.mark.parametrize(
        "module",
        [
            pytest.param([["Registration Data Import"], "filter-search", "Test"], id="Registration Data Import"),
            pytest.param([["Targeting"], "filters-search", "Test"], id="Targeting"),
            pytest.param([["Payment Verification"], "filter-search", "PP-0000-00-11223344"], id="Payment Verification"),
            pytest.param([["Grievance"], "filters-search", "GRV-0000123"], id="Grievance"),
            pytest.param(
                [["Payment Module", "Payment Plans"], "filter-search", "PP-0060-22-11223344"], id="Payment Module"
            ),
            # ToDo: uncomment after fix bug: 206395
            # pytest.param(['Main Menu', "hh-filters-search", "HH-00-0000.1380"], id="Programme Population"),
        ],
    )
    def test_filters_happy_path_search_filter(
        self,
        module: list,
        create_programs: None,
        create_targeting: None,
        create_rdi: None,
        add_payment_verification: None,
        add_household: None,
        add_grievance_tickets: None,
        filters: Filters,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        filters.selectGlobalProgramFilter("Test Programm")
        assert "Test Programm" in pageProgrammeDetails.getHeaderTitle().text

        for element in module[0]:
            filters.wait_for(f'[data-cy="nav-{element}').click()

        assert filters.waitForNumberOfRows(2)
        filters.getFilterByLocator(module[1]).send_keys("Wrong value")
        filters.getButtonFiltersApply().click()
        assert filters.waitForNumberOfRows(0)
        filters.getButtonFiltersClear().click()
        assert filters.waitForNumberOfRows(2)
        filters.getFilterByLocator(module[1]).send_keys(module[2])
        filters.getButtonFiltersApply().click()
        assert filters.waitForNumberOfRows(1)

    @pytest.mark.night
    @pytest.mark.skip("ToDo")
    def test_grievance_tickets_filters_of_households_and_individuals(
        self,
        pageGrievanceTickets: GrievanceTickets,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        filters: Filters,
    ) -> None:
        pageGrievanceTickets.getNavGrievance().click()
        assert "Grievance Tickets" in pageGrievanceTickets.getGrievanceTitle().text
        pageGrievanceTickets.getButtonNewTicket().click()

    @pytest.mark.skip("ToDo")
    def test_payment_verification_details_filters(
        self,
        pageGrievanceTickets: GrievanceTickets,
        filters: Filters,
    ) -> None:
        pageGrievanceTickets.getNavPaymentVerification().click()
