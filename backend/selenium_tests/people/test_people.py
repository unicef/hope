from datetime import datetime
from typing import List

from django.db import transaction

import pytest
from dateutil.relativedelta import relativedelta
from page_object.people.people import People

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_individual_document,
)
from hct_mis_api.apps.household.models import HOST, SEEING, Individual
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import GenericPayment, PaymentRecord
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from selenium_tests.page_object.filters import Filters
from selenium_tests.page_object.people.people_details import PeopleDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def social_worker_program() -> Program:
    return get_program_with_dct_type_and_name("Worker Program", "WORK", DataCollectingType.Type.SOCIAL, Program.ACTIVE)


@pytest.fixture
def add_people(social_worker_program: Program) -> List:
    ba = social_worker_program.business_area
    with transaction.atomic():
        household, individuals = create_household(
            household_args={"business_area": ba, "program": social_worker_program, "residence_status": HOST},
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
        create_individual_document(individual)
    yield [individual, household]


@pytest.fixture
def add_people_with_payment_record(add_people: List) -> PaymentRecord:
    program = Program.objects.filter(name="Worker Program").first()

    cash_plan = CashPlanFactory(
        name="TEST",
        program=program,
        business_area=BusinessArea.objects.first(),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )

    targeting_criteria = TargetingCriteriaFactory()

    target_population = TargetPopulationFactory(
        created_by=User.objects.first(),
        targeting_criteria=targeting_criteria,
        business_area=BusinessArea.objects.first(),
    )
    payment_record = PaymentRecordFactory(
        household=add_people[1],
        parent=cash_plan,
        target_population=target_population,
        entitlement_quantity="21.36",
        delivered_quantity="21.36",
        currency="PLN",
        status=GenericPayment.STATUS_DISTRIBUTION_SUCCESS,
    )
    add_people[1].total_cash_received_usd = "21.36"
    add_people[1].save()
    return payment_record


def get_program_with_dct_type_and_name(
    name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.DRAFT
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.mark.usefixtures("login")
class TestSmokePeople:
    def test_smoke_page_people(self, social_worker_program: Program, pagePeople: People) -> None:
        pagePeople.selectGlobalProgramFilter("Worker Program").click()
        pagePeople.getNavPeople().click()
        assert "People" in pagePeople.getTableTitle().text
        assert "Individual ID" in pagePeople.getIndividualId().text
        assert "Individual" in pagePeople.getIndividualName().text
        assert "Type" in pagePeople.getIndividualAge().text
        assert "Gender" in pagePeople.getIndividualSex().text
        assert "Administrative Level 2" in pagePeople.getIndividualLocation().text
        assert "Rows per page: 10 0–0 of 0" in pagePeople.getTablePagination().text.replace("\n", " ")

    def test_smoke_page_details_people(
        self,
        add_people: None,
        pagePeople: People,
        pagePeopleDetails: PeopleDetails,
        filters: Filters,
    ) -> None:
        pagePeople.selectGlobalProgramFilter("Worker Program").click()
        pagePeople.getNavPeople().click()
        assert "People" in pagePeople.getTableTitle().text
        unicef_id = pagePeople.getIndividualTableRow(0).text.split(" ")[0]
        pagePeople.getIndividualTableRow(0).click()
        individual = Individual.objects.filter(unicef_id=unicef_id).first()
        assert f"Individual ID: {individual.unicef_id}" in pagePeopleDetails.getPageHeaderTitle().text
        assert individual.full_name in pagePeopleDetails.getLabelFullName().text
        assert individual.given_name in pagePeopleDetails.getLabelGivenName().text
        assert individual.middle_name if individual.middle_name else "-" in pagePeopleDetails.getLabelMiddleName().text
        assert individual.family_name in pagePeopleDetails.getLabelFamilyName().text
        assert individual.sex.lower() in pagePeopleDetails.getLabelGender().text.lower()
        assert pagePeopleDetails.getLabelAge().text
        assert individual.birth_date.strftime("%-d %b %Y") in pagePeopleDetails.getLabelDateOfBirth().text
        assert pagePeopleDetails.getLabelEstimatedDateOfBirth().text
        assert individual.marital_status.lower() in pagePeopleDetails.getLabelMaritalStatus().text.lower()
        assert "Not provided" in pagePeopleDetails.getLabelWorkStatus().text
        assert pagePeopleDetails.getLabelPregnant().text
        assert pagePeopleDetails.getLabelRole().text
        assert (
            individual.preferred_language
            if individual.preferred_language
            else "-" in pagePeopleDetails.getLabelPreferredLanguage().text
        )
        assert "Non-displaced | Host" in pagePeopleDetails.getLabelResidenceStatus().text
        assert (
            individual.household.country
            if individual.household.country
            else "-" in pagePeopleDetails.getLabelCountry().text
        )
        assert (
            individual.household.country_origin
            if individual.household.country_origin
            else "-" in pagePeopleDetails.getLabelCountryOfOrigin().text
        )
        assert (
            individual.household.address
            if individual.household.address
            else "-" in pagePeopleDetails.getLabelAddress().text
        )
        assert (
            individual.household.village
            if individual.household.village
            else "-" in pagePeopleDetails.getLabelVilage().text
        )
        assert (
            individual.household.zip_code
            if individual.household.zip_code
            else "-" in pagePeopleDetails.getLabelZipCode().text
        )
        assert (
            individual.household.admin1
            if individual.household.admin1
            else "-" in pagePeopleDetails.getLabelAdministrativeLevel1().text
        )
        assert (
            individual.household.admin2
            if individual.household.admin2
            else "-" in pagePeopleDetails.getLabelAdministrativeLevel2().text
        )
        assert (
            individual.household.admin3
            if individual.household.admin3
            else "-" in pagePeopleDetails.getLabelAdministrativeLevel3().text
        )
        assert (
            individual.household.admin4
            if individual.household.admin4
            else "-" in pagePeopleDetails.getLabelAdministrativeLevel4().text
        )
        assert (
            individual.household.geopoint
            if individual.household.geopoint
            else "-" in pagePeopleDetails.getLabelGeolocation().text
        )
        assert pagePeopleDetails.getLabelDataCollectingType().text
        assert pagePeopleDetails.getLabelObservedDisabilities().text
        assert pagePeopleDetails.getLabelSeeingDisabilitySeverity().text
        assert pagePeopleDetails.getLabelHearingDisabilitySeverity().text
        assert pagePeopleDetails.getLabelPhysicalDisabilitySeverity().text
        assert pagePeopleDetails.getLabelRememberingOrConcentratingDisabilitySeverity().text
        assert pagePeopleDetails.getLabelCommunicatingDisabilitySeverity().text
        assert "Not Disabled" in pagePeopleDetails.getLabelDisability().text
        assert pagePeopleDetails.getLabelIssued().text
        assert pagePeopleDetails.getLabelEmail().text
        assert pagePeopleDetails.getLabelPhoneNumber().text
        assert pagePeopleDetails.getLabelAlternativePhoneNumber().text
        assert pagePeopleDetails.getLabelDateOfLastScreeningAgainstSanctionsList().text
        assert pagePeopleDetails.getLabelLinkedGrievances().text
        assert pagePeopleDetails.getLabelWalletName().text
        assert pagePeopleDetails.getLabelBlockchainName().text
        assert pagePeopleDetails.getLabelWalletAddress().text
        assert "Rows per page: 5 0–0 of 0" in pagePeopleDetails.getTablePagination().text.replace("\n", " ")
        assert pagePeopleDetails.getLabelSource().text
        assert pagePeopleDetails.getLabelImportName().text
        assert pagePeopleDetails.getLabelRegistrationDate().text
        assert pagePeopleDetails.getLabelUserName().text

    def test_people_happy_path(
        self,
        add_people_with_payment_record: PaymentRecord,
        pagePeople: People,
        pagePeopleDetails: PeopleDetails,
    ) -> None:
        pagePeople.selectGlobalProgramFilter("Worker Program").click()
        pagePeople.getNavPeople().click()
        pagePeople.getIndividualTableRow(0).click()
        assert "21.36" in pagePeopleDetails.getLabelTotalCashReceived().text
        pagePeopleDetails.waitForRows()
        assert 1 == len(pagePeopleDetails.getRows())
        assert "21.36" in pagePeopleDetails.getRows()[0].text
        assert "DELIVERED FULLY" in pagePeopleDetails.getRows()[0].text
        assert add_people_with_payment_record.unicef_id in pagePeopleDetails.getRows()[0].text

    @pytest.mark.skip(reason="ToDo")
    def test_check_data_after_grievance_ticket_processed(self) -> None:
        pass
