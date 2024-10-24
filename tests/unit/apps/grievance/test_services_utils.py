import uuid
from typing import Any
from unittest.mock import MagicMock, patch

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    handle_add_document,
    handle_add_payment_channel,
    handle_role,
    handle_update_payment_channel,
    to_phone_number_str,
    verify_flex_fields,
)
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_ticket_service,
    create_grievance_ticket_with_details,
)
from hct_mis_api.apps.grievance.utils import (
    validate_all_individuals_before_close_needs_adjudication,
    validate_individual_for_need_adjudication,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import DeduplicationEngineSimilarityPair
from hct_mis_api.apps.utils.models import MergeStatusModel


class FlexibleAttribute:
    class objects:
        @staticmethod
        def filter(type: Any) -> Any:
            return MagicMock()


class TestGrievanceUtils(TestCase):
    def test_to_phone_number_str(self) -> None:
        data = {"phone_number": 123456789}
        to_phone_number_str(data, "phone_number")
        self.assertEqual(data["phone_number"], "123456789")

        data = {"phone_number": 123456789}
        to_phone_number_str(data, "other_field_name")
        self.assertEqual(data["phone_number"], 123456789)

    @patch("hct_mis_api.apps.core.models.FlexibleAttribute.objects.filter")
    def test_cast_flex_fields(self, mock_filter: Any) -> None:
        mock_filter.side_effect = [
            MagicMock(values_list=MagicMock(return_value=["decimal_field"])),
            MagicMock(values_list=MagicMock(return_value=["integer_field"])),
        ]

        flex_fields = {
            "decimal_field": "321.11",
            "integer_field": "123",
            "string_field": "some_string",
        }
        cast_flex_fields(flex_fields)

        self.assertEqual(flex_fields["string_field"], "some_string")
        self.assertEqual(flex_fields["integer_field"], 123)
        self.assertEqual(flex_fields["decimal_field"], 321.11)

    def test_handle_add_payment_channel(self) -> None:
        business_area = BusinessAreaFactory(name="Afghanistan")
        payment_channel = {
            "type": "BANK_TRANSFER",
            "bank_name": "BankName",
            "bank_account_number": "12345678910",
        }
        individual = IndividualFactory(household=None, business_area=business_area)
        obj = handle_add_payment_channel(payment_channel, individual)

        self.assertIsInstance(obj, BankAccountInfo)

        payment_channel["type"] = "OTHER"
        resp_none = handle_add_payment_channel(payment_channel, individual)
        self.assertIsNone(resp_none)

    def test_handle_update_payment_channel(self) -> None:
        business_area = BusinessAreaFactory(name="Afghanistan")
        individual = IndividualFactory(household=None, business_area=business_area)
        bank_info = BankAccountInfoFactory(individual=individual)
        id_str = encode_id_base64_required(str(bank_info.pk), "BankAccountInfo")

        payment_channel_dict = {
            "type": "BANK_TRANSFER",
            "id": id_str,
            "bank_name": "BankName",
            "bank_account_number": "1234321",
        }

        obj = handle_update_payment_channel(payment_channel_dict)
        self.assertIsInstance(obj, BankAccountInfo)
        payment_channel_dict["type"] = "OTHER"
        resp_none = handle_update_payment_channel(payment_channel_dict)
        self.assertIsNone(resp_none)

    def test_verify_flex_fields(self) -> None:
        with pytest.raises(ValueError) as e:
            verify_flex_fields({"key": "value"}, "associated_with")
            assert str(e.value) == "associated_with argument must be one of ['household', 'individual']"

        with pytest.raises(ValueError) as e:
            verify_flex_fields({"key": "value"}, "individuals")
            assert str(e.value) == "key is not a correct `flex field"

    def test_handle_role(self) -> None:
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        household, individuals = create_household_and_individuals(
            household_data={"business_area": business_area},
            individuals_data=[{}],
        )

        self.assertEqual(IndividualRoleInHousehold.objects.all().count(), 0)
        with pytest.raises(ValidationError) as e:
            IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
            handle_role(ROLE_PRIMARY, household, individuals[0])
            assert str(e.value) == "Ticket cannot be closed, primary collector role has to be reassigned"

        # just remove exists roles
        IndividualRoleInHousehold.objects.filter(household=household).update(role=ROLE_ALTERNATE)
        handle_role("OTHER_ROLE_XD", household, individuals[0])
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=household).count(), 0)

        # create new role
        handle_role(ROLE_ALTERNATE, household, individuals[0])
        role = IndividualRoleInHousehold.objects.filter(household=household).first()
        self.assertEqual(role.role, ROLE_ALTERNATE)
        self.assertEqual(role.rdi_merge_status, MergeStatusModel.MERGED)

    def test_handle_add_document(self) -> None:
        create_afghanistan()
        country = CountryFactory(name="Afghanistan")
        document_type = DocumentTypeFactory(key="TAX", label="tax")
        business_area = BusinessArea.objects.get(slug="afghanistan")
        household, individuals = create_household_and_individuals(
            household_data={"business_area": business_area},
            individuals_data=[{}],
        )
        individual = individuals[0]
        document_data = {
            "key": "TAX",
            "country": "AFG",
            "number": "111",
            "photo": "photo",
            "photoraw": "photo_raw",
        }

        with pytest.raises(ValidationError) as e:
            DocumentFactory(
                document_number=111,
                type=document_type,
                country=country,
                program_id=individual.program_id,
                status=Document.STATUS_VALID,
            )
            handle_add_document(document_data, individual)
            assert str(e.value) == "Document with number 111 of type tax already exists"

        with pytest.raises(ValidationError) as e:
            document_type.unique_for_individual = True
            document_type.save()
            handle_add_document(document_data, individual)
            assert str(e.value) == "Document of type tax already exists for this individual"

        Document.objects.all().delete()
        self.assertEqual(Document.objects.all().count(), 0)

        document = handle_add_document(document_data, individual)
        self.assertIsInstance(document, Document)
        self.assertEqual(document.rdi_merge_status, MergeStatusModel.MERGED)

    def test_validate_individual_for_need_adjudication(self) -> None:
        area_type_level_1 = AreaTypeFactory(name="Province", area_level=1)
        area_type_level_2 = AreaTypeFactory(name="District", area_level=2, parent=area_type_level_1)
        ghazni = AreaFactory(name="Ghazni", area_type=area_type_level_1, p_code="area1")
        doshi = AreaFactory(name="Doshi", area_type=area_type_level_2, p_code="area2", parent=ghazni)
        business_area = BusinessAreaFactory(slug="afghanistan")
        program = ProgramFactory(business_area=business_area)
        grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="GrievanceTicket",
        )
        grievance.programs.add(program)

        _, individuals_1 = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": program,
                "admin2": doshi,
            },
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )

        _, individuals_2 = create_household(
            {
                "size": 1,
                "business_area": business_area,
                "program": program,
                "admin2": doshi,
            },
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )

        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=grievance,
            golden_records_individual=individuals_1[0],
            possible_duplicate=individuals_2[0],
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )

        ticket_details.ticket = grievance
        ticket_details.save()
        partner = PartnerFactory(name="other")
        partner_unicef = PartnerFactory()

        with pytest.raises(PermissionDenied) as e:
            validate_individual_for_need_adjudication(partner, individuals_1[0], ticket_details)
            assert str(e.value) == "Permission Denied: User does not have access to select individual"

        with pytest.raises(ValidationError) as e:
            _, individuals = create_household(
                {
                    "size": 1,
                    "business_area": business_area,
                    "admin2": doshi,
                    "program": program,
                },
                {
                    "given_name": "Tester",
                    "family_name": "Test",
                    "middle_name": "",
                    "full_name": "Tester Test",
                },
            )
            individuals[0].unicef_id = "IND-333"
            individuals[0].save()
            validate_individual_for_need_adjudication(partner_unicef, individuals[0], ticket_details)
            assert (
                str(e.value)
                == "The selected individual IND-333 is not valid, must be one of those attached to the ticket"
            )

        ticket_details.possible_duplicates.add(individuals[0])

        with pytest.raises(ValidationError) as e:
            individuals[0].withdraw()
            validate_individual_for_need_adjudication(partner_unicef, individuals[0], ticket_details)
            assert str(e.value) == "The selected individual IND-333 is not valid, must be not withdrawn"

            individuals[0].unwithdraw()
            validate_individual_for_need_adjudication(partner_unicef, individuals[0], ticket_details)

        ticket_details.selected_distinct.remove(individuals[0])
        individuals[0].unwithdraw()
        validate_individual_for_need_adjudication(partner_unicef, individuals[0], ticket_details)

    def test_validate_all_individuals_before_close_needs_adjudication(self) -> None:
        BusinessAreaFactory(slug="afghanistan")
        _, individuals_1 = create_household(
            {"size": 1},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )

        _, individuals_2 = create_household(
            {"size": 1},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individuals_1[0],
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )
        ticket_details.possible_duplicates.add(individuals_2[0])
        ticket_details.save()

        with pytest.raises(ValidationError) as e:
            validate_all_individuals_before_close_needs_adjudication(ticket_details)
            assert str(e.value) == "Close ticket is not possible when all Individuals are flagged as duplicates"

        with pytest.raises(ValidationError) as e:
            validate_all_individuals_before_close_needs_adjudication(ticket_details)
            assert (
                str(e.value)
                == "Close ticket is possible when at least one individual is flagged as distinct or one of the individuals is withdrawn or duplicate"
            )

        with pytest.raises(ValidationError) as e:
            ticket_details.selected_distinct.add(individuals_2[0])
            ticket_details.save()
            validate_all_individuals_before_close_needs_adjudication(ticket_details)
            assert str(e.value) == "Close ticket is possible when all active Individuals are flagged"

        ticket_details.selected_individuals.add(individuals_1[0])
        validate_all_individuals_before_close_needs_adjudication(ticket_details)

    def test_close_needs_adjudication_ticket_service(self) -> None:
        user = UserFactory()
        ba = BusinessAreaFactory(slug="afghanistan")
        program = ProgramFactory(business_area=ba)

        grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=ba,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="GrievanceTicket",
        )
        grievance.programs.add(program)
        _, individuals_1 = create_household(
            {"size": 2, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        _, individuals_2 = create_household(
            {"size": 1, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        ind_1 = individuals_1[0]
        ind_2 = individuals_2[0]

        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=grievance,
            golden_records_individual=ind_1,
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )
        ticket_details.selected_individuals.add(ind_2)
        ticket_details.possible_duplicates.add(ind_2)
        ticket_details.selected_distinct.add(ind_1)
        ticket_details.ticket = grievance
        ticket_details.save()

        close_needs_adjudication_ticket_service(grievance, user)

        ind_1.refresh_from_db()
        ind_2.refresh_from_db()

        assert ind_1.duplicate is False
        assert ind_2.duplicate is True

    def test_close_needs_adjudication_ticket_service_when_just_duplicates(self) -> None:
        user = UserFactory()
        ba = BusinessAreaFactory(slug="afghanistan")
        program = ProgramFactory(business_area=ba)

        grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=ba,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="GrievanceTicket",
        )
        grievance.programs.add(program)
        _, individuals_1 = create_household(
            {"size": 2, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        _, individuals_2 = create_household(
            {"size": 1, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        ind_1 = individuals_1[0]
        ind_2 = individuals_2[0]

        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=grievance,
            golden_records_individual=ind_1,
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )
        ticket_details.selected_individuals.add(ind_1)  # duplicate
        ticket_details.possible_duplicates.add(ind_2)  # all possible duplicates
        ticket_details.ticket = grievance
        ticket_details.save()

        ind_2.withdraw()  # make withdraw

        with pytest.raises(ValidationError) as e:
            close_needs_adjudication_ticket_service(grievance, user)
            assert str(e.value) == "Close ticket is not possible when all Individuals are flagged as duplicates"

        gr = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=ba,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="GrievanceTicket",
        )
        gr.programs.add(program)
        ticket_details_2 = TicketNeedsAdjudicationDetailsFactory(
            ticket=gr,
            golden_records_individual=ind_1,
            is_multiple_duplicates_version=False,
            selected_individual=ind_2,
            possible_duplicate=ind_1,
        )
        ticket_details_2.ticket = gr
        ticket_details_2.save()

        close_needs_adjudication_ticket_service(gr, user)

    @patch.dict(
        "os.environ",
        {
            "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
            "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
        },
    )
    @patch(
        "hct_mis_api.apps.registration_datahub.services.biometric_deduplication.BiometricDeduplicationService.report_false_positive_duplicate"
    )
    def test_close_needs_adjudication_ticket_service_for_biometrics(
        self, report_false_positive_duplicate_mock: MagicMock
    ) -> None:
        user = UserFactory()
        ba = BusinessAreaFactory(slug="afghanistan")
        deduplication_set_id = uuid.uuid4()
        program = ProgramFactory(business_area=ba, deduplication_set_id=deduplication_set_id)
        rdi = RegistrationDataImportFactory(
            program=program,
        )

        hh1, individuals_1 = create_household(
            {"size": 2, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        hh2, individuals_2 = create_household(
            {"size": 2, "business_area": ba, "program": program},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        ind_1, ind_2 = sorted([individuals_1[1], individuals_2[1]], key=lambda x: x.id)
        ind_1.photo = ContentFile(b"...", name="1.png")
        ind_2.photo = ContentFile(b"...", name="2.png")
        ind_1.save()
        ind_2.save()

        ticket, ticket_details = create_grievance_ticket_with_details(
            main_individual=ind_1,
            possible_duplicate=ind_2,
            business_area=ba,
            registration_data_import=hh1.registration_data_import,
            possible_duplicates=[ind_2],
            is_multiple_duplicates_version=True,
            issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
            dedup_engine_similarity_pair=DeduplicationEngineSimilarityPair.objects.create(
                program=program,
                individual1=ind_1,
                individual2=ind_2,
                similarity_score=90.55,
            ),
        )
        if not ticket:
            raise ValueError("Ticket not created")
        ticket.registration_data_import = rdi
        ticket.save()

        ticket_details.selected_distinct.set([ind_1])
        ticket_details.selected_individuals.set([ind_2])
        ticket_details.save()

        close_needs_adjudication_ticket_service(ticket, user)
        report_false_positive_duplicate_mock.assert_not_called()

        ticket_details.selected_distinct.set([ind_1, ind_2])
        ticket_details.selected_individuals.set([])
        ticket_details.save()

        close_needs_adjudication_ticket_service(ticket, user)
        report_false_positive_duplicate_mock.assert_called_once_with(
            str(ind_1.photo.name),
            str(ind_2.photo.name),
            str(deduplication_set_id),
        )
