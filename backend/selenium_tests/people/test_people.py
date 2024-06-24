from datetime import datetime

from django.db import transaction

import pytest
from dateutil.relativedelta import relativedelta
from page_object.people.people import People

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_individual_document,
)
from hct_mis_api.apps.household.models import HOST, SEEING
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from selenium_tests.page_object.people.people_details import PeopleDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def social_worker_program() -> Program:
    return get_program_with_dct_type_and_name("Worker Program", "WORK", DataCollectingType.Type.SOCIAL)


@pytest.fixture
def add_people(social_worker_program: Program) -> None:
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

    @pytest.mark.skip(reason="Waiting for add people fixture")
    def test_smoke_page_details_people(
        self,
        social_worker_program: Program,
        add_people: None,
        pagePeople: People,
        pagePeopleDetails: PeopleDetails,
    ) -> None:
        pagePeople.selectGlobalProgramFilter("Worker Program").click()
        pagePeople.getNavPeople().click()
        pagePeople.getIndividualTableRow(0).click()
        assert "Individual ID: IND-05-0000.2927" in pagePeopleDetails.getPageHeaderTitle().text
        assert "Stacey Freeman" in pagePeopleDetails.getLabelFullName().text
        assert "-" in pagePeopleDetails.getLabelGivenName().text
        assert "-" in pagePeopleDetails.getLabelMiddleName().text
        assert "Todd Adams" in pagePeopleDetails.getLabelFamilyName().text
        assert "Female" in pagePeopleDetails.getLabelGender().text
        assert "5" in pagePeopleDetails.getLabelAge().text
        assert "2 Dec 2018" in pagePeopleDetails.getLabelDateOfBirth().text
        assert "No" in pagePeopleDetails.getLabelEstimatedDateOfBirth().text
        assert "-" in pagePeopleDetails.getLabelMaritalStatus().text
        assert "Not provided" in pagePeopleDetails.getLabelWorkStatus().text
        assert "No" in pagePeopleDetails.getLabelPregnant().text
        assert "Primary collector" in pagePeopleDetails.getLabelRole().text
        assert "-" in pagePeopleDetails.getLabelPreferredLanguage().text
        assert "None" in pagePeopleDetails.getLabelResidenceStatus().text
        assert "Western Sahara" in pagePeopleDetails.getLabelCountry().text
        assert "-" in pagePeopleDetails.getLabelCountryOfOrigin().text
        assert "-" in pagePeopleDetails.getLabelAddress().text
        assert "-" in pagePeopleDetails.getLabelVilage().text
        assert "-" in pagePeopleDetails.getLabelZipCode().text
        assert "Hirat" in pagePeopleDetails.getLabelAdministrativeLevel1().text
        assert "Adraskan" in pagePeopleDetails.getLabelAdministrativeLevel2().text
        assert "-" in pagePeopleDetails.getLabelAdministrativeLevel3().text
        assert "-" in pagePeopleDetails.getLabelAdministrativeLevel4().text
        assert "-" in pagePeopleDetails.getLabelGeolocation().text
        assert "Partial" in pagePeopleDetails.getLabelDataCollectingType().text
        assert "Difficulty walking or climbing steps" in pagePeopleDetails.getLabelObservedDisabilities().text
        assert "Some difficulty" in pagePeopleDetails.getLabelSeeingDisabilitySeverity().text
        assert "A lot of difficulty" in pagePeopleDetails.getLabelHearingDisabilitySeverity().text
        assert "None" in pagePeopleDetails.getLabelPhysicalDisabilitySeverity().text
        assert "Cannot do at all" in pagePeopleDetails.getLabelRememberingOrConcentratingDisabilitySeverity().text
        assert "Some difficulty" in pagePeopleDetails.getLabelpagePeopleDetailsCareDisabilitySeverity().text
        assert "A lot of difficulty" in pagePeopleDetails.getLabelCommunicatingDisabilitySeverity().text
        assert "Not Disabled" in pagePeopleDetails.getLabelDisability().text
        assert "1427939569" in pagePeopleDetails.getLabelBirthCertificate().text
        assert "Burundi" in pagePeopleDetails.getLabelIssued().text
        assert "388855545" in pagePeopleDetails.getLabelDriverLicense().text
        assert "Saint Barthélemy" in pagePeopleDetails.getLabelIssued().text
        assert "1342079771" in pagePeopleDetails.getLabelElectoralCard().text
        assert "French Southern Territories" in pagePeopleDetails.getLabelIssued().text
        assert "1872704691" in pagePeopleDetails.getLabelNationalPassport().text
        assert "Guinea" in pagePeopleDetails.getLabelIssued().text
        assert "755043089" in pagePeopleDetails.getLabelNationalId().text
        assert "Anguilla" in pagePeopleDetails.getLabelIssued().text
        assert "771861294" in pagePeopleDetails.getLabelUnhcrId().text
        assert "Saudi Arabia" in pagePeopleDetails.getLabelIssued().text
        assert "898322765" in pagePeopleDetails.getLabelWfpId().text
        assert "Liberia" in pagePeopleDetails.getLabelIssued().text
        assert "-" in pagePeopleDetails.getLabelEmail().text
        assert "Invalid Phone Number" in pagePeopleDetails.getLabelPhoneNumber().text
        assert "-" in pagePeopleDetails.getLabelAlternativePhoneNumber().text
        assert "13 Jun 2024" in pagePeopleDetails.getLabelDateOfLastScreeningAgainstSanctionsList().text
        assert "-" in pagePeopleDetails.getLabelLinkedGrievances().text
        assert "-" in pagePeopleDetails.getLabelWalletName().text
        assert "-" in pagePeopleDetails.getLabelBlockchainName().text
        assert "-" in pagePeopleDetails.getLabelWalletAddress().text
        assert "USD 0.00 (ARS 0.00)" in pagePeopleDetails.getLabelCashReceived().text
        assert "USD 0.00" in pagePeopleDetails.getLabelTotalCashReceived().text
        assert "Payment Records" in pagePeopleDetails.getTableTitle().text
        assert "Payment ID" in pagePeopleDetails.getTableLabel().text
        assert "Status" in pagePeopleDetails.getTableLabel().text
        assert "Entitlement Quantity" in pagePeopleDetails.getTableLabel().text
        assert "Delivered Quantity" in pagePeopleDetails.getTableLabel().text
        assert "Delivery Date" in pagePeopleDetails.getTableLabel().text
        assert "PENDING" in pagePeopleDetails.getStatusContainer().text
        assert "Rows per page: 5 1–1 of 1" in pagePeopleDetails.getTablePagination().text
        assert "XLS" in pagePeopleDetails.getLabelSource().text
        assert "121321" in pagePeopleDetails.getLabelImportName().text
        assert "7 May 2005" in pagePeopleDetails.getLabelRegistrationDate().text
