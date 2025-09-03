from datetime import datetime
import os
from time import sleep

from dateutil.relativedelta import relativedelta
import pytest

from e2e.page_object.people.people import People
from e2e.page_object.people.people_details import PeopleDetails
from e2e.page_object.programme_population.individuals import Individuals
from e2e.page_object.programme_population.periodic_data_update_templates import (
    PDUXlsxTemplates,
)
from e2e.page_object.programme_population.periodic_data_update_uploads import (
    PDUXlsxUploads,
)
from e2e.programme_population.test_periodic_data_update_upload import prepare_xlsx_file
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.periodic_data_update import (
    PDUXlsxTemplateFactory,
    PDUXlsxUploadFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hope.apps.household.models import HOST, SEEING, Individual
from hope.apps.payment.models import Payment
from hope.apps.periodic_data_update.models import (
    PDUXlsxTemplate,
    PDUXlsxUpload,
)
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.apps.program.models import BeneficiaryGroup, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def clear_downloaded_files(download_path: str) -> None:
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))
    yield
    for file in os.listdir(download_path):
        os.remove(os.path.join(download_path, file))


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="People").first()
    return ProgramFactory(
        name="Test Program",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def date_attribute(program: Program) -> FlexibleAttribute:
    return create_flexible_attribute(
        label="Test Date Attribute",
        subtype=FlexibleAttribute.DATE,
        number_of_rounds=1,
        rounds_names=["Test Round"],
        program=program,
    )


@pytest.fixture
def individual(add_people: Individual) -> Individual:
    program = Program.objects.filter(name="Test Program").first()
    payment_plan = PaymentPlanFactory(
        name="TEST",
        program_cycle=program.cycles.first(),
        business_area=BusinessArea.objects.first(),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
    PaymentFactory(
        household=add_people.household,
        parent=payment_plan,
        entitlement_quantity=21.36,
        delivered_quantity=21.36,
        currency="PLN",
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    add_people.total_cash_received_usd = 21.36
    add_people.save()
    return add_people


@pytest.fixture
def add_people(program: Program) -> Individual:
    business_area = program.business_area
    rdi = RegistrationDataImportFactory()
    household, individuals = create_household_and_individuals(
        household_data={
            "business_area": business_area,
            "program": program,
            "residence_status": HOST,
            "registration_data_import": rdi,
        },
        individuals_data=[
            {
                "full_name": "Stacey Freeman",
                "given_name": "Stacey",
                "middle_name": "",
                "family_name": "Freeman",
                "business_area": business_area,
                "observed_disability": [SEEING],
                "registration_data_import": rdi,
            },
        ],
    )
    return individuals[0]


def create_flexible_attribute(
    label: str,
    subtype: str,
    number_of_rounds: int,
    rounds_names: list[str],
    program: Program,
) -> FlexibleAttribute:
    name = field_label_to_field_name(label)
    flexible_attribute = FlexibleAttribute.objects.create(
        label={"English(EN)": label},
        name=name,
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


@pytest.fixture
def string_attribute() -> FlexibleAttribute:
    program = Program.objects.filter(name="Test Program").first()
    return create_flexible_attribute(
        label="Test String Attribute",
        subtype=FlexibleAttribute.STRING,
        number_of_rounds=1,
        rounds_names=["Test Round"],
        program=program,
    )


@pytest.mark.usefixtures("login")
class TestPeoplePDUXlsxUpload:
    def test_people_periodic_data_update_upload_success(
        self,
        clear_downloaded_files: None,
        page_people: People,
        page_people_details: PeopleDetails,
        individual: Individual,
        string_attribute: FlexibleAttribute,
        page_individuals: Individuals,
    ) -> None:
        program = Program.objects.filter(name="Test Program").first()
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
        page_people.select_global_program_filter(program.name)
        page_people.get_nav_people().click()
        page_individuals.get_tab_periodic_data_updates().click()
        page_individuals.get_tab_offline_edits().click()
        page_individuals.get_button_import().click()
        page_individuals.get_dialog_import()
        assert "IMPORT" in page_individuals.get_button_import_submit().text
        page_individuals.upload_file(tmp_file.name)
        page_individuals.get_button_import_submit().click()
        page_individuals.get_status_container()
        for i in range(5):
            periodic_data_update_upload = PDUXlsxUpload.objects.first()
            if periodic_data_update_upload.status == PDUXlsxUpload.Status.SUCCESSFUL:
                break
            page_individuals.screenshot(i)
            sleep(1)
        else:
            assert periodic_data_update_upload.status == PDUXlsxUpload.Status.SUCCESSFUL
        assert periodic_data_update_upload.error_message is None
        individual.refresh_from_db()
        assert individual.flex_fields[flexible_attribute.name]["1"]["value"] == "Test Value"
        assert individual.flex_fields[flexible_attribute.name]["1"]["collection_date"] == "2021-05-02"
        assert page_individuals.get_update_status(periodic_data_update_upload.pk).text == "Successful"
        page_individuals.screenshot("0")

    @pytest.mark.night
    def test_people_periodic_data_update_upload_form_error(
        self,
        clear_downloaded_files: None,
        program: Program,
        individual: Individual,
        date_attribute: FlexibleAttribute,
        page_individuals: Individuals,
        page_people: People,
        page_people_details: PeopleDetails,
    ) -> None:
        populate_pdu_with_null_values(program, individual.flex_fields)
        individual.save()
        flexible_attribute = date_attribute
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
        page_people.select_global_program_filter(program.name)
        page_people.get_nav_people().click()
        page_individuals.get_tab_periodic_data_updates().click()
        page_individuals.get_tab_offline_edits().click()
        page_individuals.get_button_import().click()
        page_individuals.get_dialog_import()
        page_individuals.upload_file(tmp_file.name)
        page_individuals.get_button_import_submit().click()
        page_individuals.get_status_container()
        periodic_data_update_upload = PDUXlsxUpload.objects.first()
        assert periodic_data_update_upload.status == PDUXlsxUpload.Status.FAILED
        assert page_individuals.get_status_container().text == "Failed"
        assert page_individuals.get_update_status(periodic_data_update_upload.pk).text == "Failed"
        page_individuals.get_update_details_btn(periodic_data_update_upload.pk).click()
        error_text = "Row: 2\ntest_date_attribute__round_value\nEnter a valid date."
        assert page_individuals.get_pdu_form_errors().text == error_text

    @pytest.mark.night
    def test_people_periodic_data_uploads_list(
        self,
        clear_downloaded_files: None,
        program: Program,
        string_attribute: FlexibleAttribute,
        page_individuals: Individuals,
        page_pdu_xlsx_templates: PDUXlsxTemplates,
        page_pdu_xlsx_uploads: PDUXlsxUploads,
        page_people: People,
        page_people_details: PeopleDetails,
    ) -> None:
        periodic_data_update_template = PDUXlsxTemplateFactory(
            program=program,
            business_area=program.business_area,
            status=PDUXlsxTemplate.Status.TO_EXPORT,
            filters={},
            rounds_data=[
                {
                    "field": string_attribute.name,
                    "round": 1,
                    "round_name": string_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
        )
        pdu_upload = PDUXlsxUploadFactory(
            template=periodic_data_update_template,
            status=PDUXlsxUpload.Status.SUCCESSFUL,
        )
        page_people.select_global_program_filter(program.name)
        page_people.get_nav_people().click()
        page_individuals.get_tab_periodic_data_updates().click()
        page_individuals.get_tab_offline_edits().click()
        index = pdu_upload.id
        assert str(index) in page_pdu_xlsx_uploads.get_update_id(index).text
        assert str(pdu_upload.template.id) in page_pdu_xlsx_uploads.get_update_template(index).text
        assert f"{pdu_upload.created_at:%-d %b %Y}" in page_pdu_xlsx_uploads.get_update_created_at(index).text
        assert pdu_upload.created_by.get_full_name() in page_pdu_xlsx_uploads.get_update_created_by(index).text
        assert "Successful" in page_pdu_xlsx_uploads.get_update_status(index).text
