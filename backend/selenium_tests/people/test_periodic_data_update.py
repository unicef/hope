import os
from datetime import datetime
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper
from typing import Any, List

import openpyxl
import pytest
from dateutil.relativedelta import relativedelta
from django.db import transaction
from page_object.programme_population.periodic_data_update_templates import (
    PeriodicDatUpdateTemplates,
)
from page_object.programme_population.periodic_data_update_uploads import (
    PeriodicDataUpdateUploads,
)

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData, BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals, create_individual_document, \
    create_household
from hct_mis_api.apps.household.models import Individual, SEEING, HOST
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord, GenericPayment
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
    PeriodicDataUpdateUploadFactory,
)
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)
from hct_mis_api.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory
from selenium_tests.page_object.people.people import People
from selenium_tests.page_object.people.people_details import PeopleDetails
from selenium_tests.page_object.programme_population.individuals import Individuals
from selenium_tests.programme_population.test_periodic_data_update_upload import prepare_xlsx_file

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def clear_downloaded_files() -> None:
    yield
    for file in os.listdir("./report/downloads/"):
        os.remove(os.path.join("./report/downloads", file))


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
def add_program(add_people: List) -> Program:
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
    PaymentRecordFactory(
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
    return program


@pytest.mark.usefixtures("login")
class TestPeriodicDataUpdateUpload:
    def test_periodic_data_update_upload_success(
        self,
        clear_downloaded_files: None,
            pagePeople: People,
            pagePeopleDetails: PeopleDetails,
        program: Program,
        individual: Individual,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        flexible_attribute = string_attribute
        tmp_file = prepare_xlsx_file(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["Test Value", "2021-05-02"]],
            program,
        )
        pageIndividuals.selectGlobalProgramFilter(program.name)
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        pageIndividuals.getButtonImport().click()
        pageIndividuals.getDialogImport()
        assert "IMPORT" in pageIndividuals.getButtonImportSubmit().text
        pageIndividuals.upload_file(tmp_file.name)
        pageIndividuals.getButtonImportSubmit().click()
        pageIndividuals.getPduUpdates().click()
        periodic_data_update_upload = PeriodicDataUpdateUpload.objects.first()
        assert periodic_data_update_upload.status == PeriodicDataUpdateUpload.Status.SUCCESSFUL
        assert periodic_data_update_upload.error_message is None
        individual.refresh_from_db()
        assert individual.flex_fields[flexible_attribute.name]["1"]["value"] == "Test Value"
        assert individual.flex_fields[flexible_attribute.name]["1"]["collection_date"] == "2021-05-02"
        assert pageIndividuals.getUpdateStatus(periodic_data_update_upload.pk).text == "SUCCESSFUL"