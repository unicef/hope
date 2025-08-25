import pytest
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.accountability.communication import AccountabilityCommunication
from e2e.page_object.accountability.comunication_details import (
    AccountabilityCommunicationDetails,
)
from extras.test_utils.factories.accountability import CommunicationMessageFactory
from extras.test_utils.factories.payment import PaymentPlanFactory

from models.account import User
from models.accountability import Message
from models.core import BusinessArea, DataCollectingType
from hope.apps.payment.models import PaymentPlan
from models.program import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_accountability_communication_message() -> Message:
    ba = BusinessArea.objects.first()
    user = User.objects.first()
    program = Program.objects.get(name="Test Program")
    cycle = program.cycles.first()
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=ba,
        program_cycle=cycle,
    )
    return CommunicationMessageFactory(
        unicef_id="MSG-24-0666",
        title="You got credit of USD 100",
        body="Greetings, we have sent you USD 100 in your registered account on 2022-09-19 20:00:00 UTC",
        business_area=ba,
        payment_plan=payment_plan,
        created_by=user,
        program=program,
    )


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilityCommunication:
    def test_smoke_accountability_communication(
        self,
        test_program: Program,
        add_accountability_communication_message: Message,
        page_accountability_communication: AccountabilityCommunication,
    ) -> None:
        page_accountability_communication.select_global_program_filter("Test Program")
        page_accountability_communication.get_nav_accountability().click()
        assert "Communication" in page_accountability_communication.get_page_header_title().text
        assert "NEW MESSAGE" in page_accountability_communication.get_button_communication_create_new().text
        assert (
            "Target Population" in page_accountability_communication.get_filters_target_population_autocomplete().text
        )
        assert "Target Population" in page_accountability_communication.get_target_population_input().text
        assert "Created by" in page_accountability_communication.get_filters_created_by_autocomplete().text
        assert "Created by" in page_accountability_communication.get_created_by_input().text
        assert "From" in page_accountability_communication.get_filters_creation_date_from().text
        assert "To" in page_accountability_communication.get_filters_creation_date_to().text
        assert "CLEAR" in page_accountability_communication.get_button_filters_clear().text
        assert "APPLY" in page_accountability_communication.get_button_filters_apply().text
        assert "Messages List" in page_accountability_communication.get_table_title().text
        assert "Message ID" in page_accountability_communication.get_table_label()[0].text
        assert "Title" in page_accountability_communication.get_table_label()[1].text
        assert "Number of Recipients" in page_accountability_communication.get_table_label()[2].text
        assert "Created by" in page_accountability_communication.get_table_label()[3].text
        assert "Creation Date" in page_accountability_communication.get_table_label()[4].text
        assert "Rows per page: 10 1–1 of 1" in page_accountability_communication.get_table_pagination().text.replace(
            "\n", " "
        )
        assert len(page_accountability_communication.get_rows()) == 1

    def test_smoke_accountability_communication_details(
        self,
        test_program: Program,
        add_accountability_communication_message: Message,
        page_accountability_communication: AccountabilityCommunication,
        page_accountability_communication_details: AccountabilityCommunicationDetails,
    ) -> None:
        page_accountability_communication.select_global_program_filter("Test Program")
        page_accountability_communication.get_nav_accountability().click()
        page_accountability_communication.get_rows()[0].click()
        assert "MSG-24-0666" in page_accountability_communication_details.get_page_header_title().text
        created_by = add_accountability_communication_message.created_by
        assert (
            f"{created_by.first_name} {created_by.last_name}"
            in page_accountability_communication_details.get_label_created_by().text
        )

        assert (
            "You got credit of USD 100 Greetings, we have sent you USD 100 in your registered account on 2022-09-19 20:00:00 UTC"
            in page_accountability_communication_details.get_communication_message_details().text.replace("\n", " ")
        )

        assert (
            add_accountability_communication_message.created_at.strftime("%-d %b %Y")
            in page_accountability_communication_details.get_label_date_created().text
        )
        assert (
            PaymentPlan.objects.first().name
            in page_accountability_communication_details.get_label_target_population().text
        )
        assert "Recipients" in page_accountability_communication_details.get_table_title().text
        assert "Items Group ID" in page_accountability_communication_details.get_household_id().text
        assert "Status" in page_accountability_communication_details.get_status().text
        assert "Head of Items Group" in page_accountability_communication_details.get_household_head_name().text
        assert "Items Group Size" in page_accountability_communication_details.get_household_size().text
        assert "Administrative Level 2" in page_accountability_communication_details.get_household_location().text
        assert "Residence Status" in page_accountability_communication_details.get_household_residence_status().text
        assert "Registration Date" in page_accountability_communication_details.get_household_registration_date().text
        assert (
            "No results Try adjusting your search or your filters to find what you are looking for."
            in page_accountability_communication_details.get_table_row().text.replace("\n", " ")
        )
        assert (
            "Rows per page: 10 0–0 of 0"
            in page_accountability_communication_details.get_table_pagination().text.replace("\n", " ")
        )
