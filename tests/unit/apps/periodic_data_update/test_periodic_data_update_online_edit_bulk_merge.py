from typing import Any, List

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_pdu_flexible_attribute
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import PeriodicFieldData
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditBulkMerge:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.rdi = RegistrationDataImportFactory()
        self.household, self.individuals = create_household_and_individuals(
            household_data={
                "business_area": self.afghanistan,
                "program_id": self.program.pk,
                "registration_data_import": self.rdi,
            },
            individuals_data=[
                {
                    "business_area": self.afghanistan,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
                {
                    "business_area": self.afghanistan,
                    "program_id": self.program.pk,
                    "registration_data_import": self.rdi,
                },
            ],
        )
        self.individual1 = self.individuals[0]
        self.individual2 = self.individuals[1]

        # Create flexible attributes for PDU data
        self.string_attribute = create_pdu_flexible_attribute(
            label="String Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
            program=self.program,
        )
        self.decimal_attribute = create_pdu_flexible_attribute(
            label="Decimal Attribute",
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
            program=self.program,
        )
        self.boolean_attribute = create_pdu_flexible_attribute(
            label="Boolean Attribute",
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
            program=self.program,
        )
        self.date_attribute = create_pdu_flexible_attribute(
            label="Date Attribute",
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
            program=self.program,
        )

        # Initialize flex_fields with null values
        populate_pdu_with_null_values(self.program, self.individual1.flex_fields)
        populate_pdu_with_null_values(self.program, self.individual2.flex_fields)
        self.individual1.save()
        self.individual2.save()

        # Create PDU online edits with edit_data
        self.pdu_edit_approved_1 = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Approved Edit 1",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
            edit_data=[
                {
                    "individual_uuid": str(self.individual1.id),
                    "pdu_fields": {
                        self.string_attribute.name: {
                            "value": "Test String Value 1",
                            "subtype": PeriodicFieldData.STRING,
                            "round_number": 1,
                            "collection_date": "2024-01-15",
                            "is_editable": True,
                        },
                        self.decimal_attribute.name: {
                            "value": 123.45,
                            "subtype": PeriodicFieldData.DECIMAL,
                            "round_number": 1,
                            "collection_date": "2024-01-15",
                            "is_editable": True,
                        },
                    },
                }
            ],
        )

        self.pdu_edit_approved_2 = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Approved Edit 2",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
            edit_data=[
                {
                    "individual_uuid": str(self.individual2.id),
                    "pdu_fields": {
                        self.boolean_attribute.name: {
                            "value": True,
                            "subtype": PeriodicFieldData.BOOL,
                            "round_number": 1,
                            "collection_date": "2024-01-16",
                            "is_editable": True,
                        },
                        self.date_attribute.name: {
                            "value": "2024-01-20",
                            "subtype": PeriodicFieldData.DATE,
                            "round_number": 1,
                            "collection_date": "2024-01-16",
                            "is_editable": True,
                        },
                    },
                }
            ],
        )

        self.pdu_edit_approved_not_authorized = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Approved Edit Not Authorized",
            status=PDUOnlineEdit.Status.APPROVED,
            edit_data=[
                {
                    "individual_uuid": str(self.individual2.id),
                    "pdu_fields": {
                        self.boolean_attribute.name: {
                            "value": True,
                            "subtype": PeriodicFieldData.BOOL,
                            "round_number": 1,
                            "collection_date": "2024-01-16",
                            "is_editable": True,
                        },
                        self.date_attribute.name: {
                            "value": "2024-01-20",
                            "subtype": PeriodicFieldData.DATE,
                            "round_number": 1,
                            "collection_date": "2024-01-16",
                            "is_editable": True,
                        },
                    },
                }
            ],
        )

        self.pdu_edit_ready = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit",
            status=PDUOnlineEdit.Status.READY,
            authorized_users=[self.user],
        )

        self.pdu_edit_new = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="New Edit",
            status=PDUOnlineEdit.Status.NEW,
            authorized_users=[self.user],
        )

        self.pdu_edit_merged = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Already Merged Edit",
            status=PDUOnlineEdit.Status.MERGED,
            authorized_users=[self.user],
        )

        self.url_bulk_merge = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-bulk-merge",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_ONLINE_MERGE], status.HTTP_200_OK),
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_bulk_merge_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_approved_1.id, self.pdu_edit_approved_2.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)
        assert response.status_code == expected_status

    def test_bulk_merge_check_authorized_user_single_edit(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state of individual data
        self.individual1.refresh_from_db()
        initial_string_value = self.individual1.flex_fields[self.string_attribute.name]["1"]["value"]
        initial_decimal_value = self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"]
        assert initial_string_value is None
        assert initial_decimal_value is None

        # Attempt to merge an edit the user is not authorized for
        data = {"ids": [self.pdu_edit_approved_not_authorized.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert (
            f"You are not an authorized user for PDU Online Edit: {self.pdu_edit_approved_not_authorized.id}"
            in response_json["detail"]
        )

        # Verify the edit was not merged
        self.pdu_edit_approved_not_authorized.refresh_from_db()
        assert self.pdu_edit_approved_not_authorized.status == PDUOnlineEdit.Status.APPROVED

        # Verify individual data was not updated
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == initial_string_value
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] == initial_decimal_value

    def test_bulk_merge_check_authorized_user_mixed(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state of individual data for both individuals
        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()
        initial_string_value = self.individual1.flex_fields[self.string_attribute.name]["1"]["value"]
        initial_decimal_value = self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"]
        initial_boolean_value = self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"]
        initial_date_value = self.individual2.flex_fields[self.date_attribute.name]["1"]["value"]
        assert initial_string_value is None
        assert initial_decimal_value is None
        assert initial_boolean_value is None
        assert initial_date_value is None

        # Attempt to merge an edit the user is not authorized for
        data = {"ids": [self.pdu_edit_approved_not_authorized.id, self.pdu_edit_approved_1.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert (
            f"You are not an authorized user for PDU Online Edit: {self.pdu_edit_approved_not_authorized.id}"
            in response_json["detail"]
        )

        # Verify no edits were merged
        self.pdu_edit_approved_not_authorized.refresh_from_db()
        self.pdu_edit_approved_1.refresh_from_db()
        assert self.pdu_edit_approved_not_authorized.status == PDUOnlineEdit.Status.APPROVED
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.APPROVED

        # Verify individual data was not updated for both individuals
        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == initial_string_value
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] == initial_decimal_value
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"] == initial_boolean_value
        assert self.individual2.flex_fields[self.date_attribute.name]["1"]["value"] == initial_date_value

    def test_bulk_merge_success(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_approved_1.id, self.pdu_edit_approved_2.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "2 PDU Online Edits queued for merging."}

        # Verify edits status changed to PENDING_MERGE or MERGED
        self.pdu_edit_approved_1.refresh_from_db()
        self.pdu_edit_approved_2.refresh_from_db()

        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED
        assert self.pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED

    def test_bulk_merge_single_edit(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_approved_1.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "1 PDU Online Edits queued for merging."}

        self.pdu_edit_approved_1.refresh_from_db()
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED

    def test_bulk_merge_invalid_status(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state of individual data
        self.individual1.refresh_from_db()
        initial_string_value = self.individual1.flex_fields[self.string_attribute.name]["1"]["value"]
        initial_decimal_value = self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"]
        assert initial_string_value is None
        assert initial_decimal_value is None

        # Try to merge edits that are not in APPROVED status
        data = {"ids": [self.pdu_edit_approved_1.id, self.pdu_edit_ready.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Approved' status and cannot be merged." in response_json[0]

        # Verify no edits were merged
        self.pdu_edit_approved_1.refresh_from_db()
        self.pdu_edit_ready.refresh_from_db()
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.APPROVED
        assert self.pdu_edit_ready.status == PDUOnlineEdit.Status.READY

        # Verify individual data was not updated
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == initial_string_value
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] == initial_decimal_value

    def test_bulk_merge_mixed_statuses(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Try to merge mix of APPROVED, READY, NEW, and MERGED edits
        data = {
            "ids": [
                self.pdu_edit_approved_1.id,
                self.pdu_edit_ready.id,
                self.pdu_edit_new.id,
                self.pdu_edit_merged.id,
            ]
        }
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Approved' status and cannot be merged." in response_json[0]

    def test_bulk_merge_empty_ids(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": []}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_merge_non_existent_ids(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        non_existent_id = 99999
        data = {"ids": [non_existent_id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "One or more PDU online edits not found." in response_json[0]

    def test_bulk_merge_preserves_other_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Store original values
        original_name = self.pdu_edit_approved_1.name
        original_created_by = self.pdu_edit_approved_1.created_by
        original_created_at = self.pdu_edit_approved_1.created_at
        original_number_of_records = self.pdu_edit_approved_1.number_of_records
        original_approved_by = self.pdu_edit_approved_1.approved_by
        original_approved_at = self.pdu_edit_approved_1.approved_at

        data = {"ids": [self.pdu_edit_approved_1.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK

        self.pdu_edit_approved_1.refresh_from_db()

        # Verify only status changed
        assert self.pdu_edit_approved_1.name == original_name
        assert self.pdu_edit_approved_1.created_by == original_created_by
        assert self.pdu_edit_approved_1.created_at == original_created_at
        assert self.pdu_edit_approved_1.number_of_records == original_number_of_records
        assert self.pdu_edit_approved_1.approved_by == original_approved_by
        assert self.pdu_edit_approved_1.approved_at == original_approved_at

        # Verify status changed to MERGED
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED

    def test_bulk_merge_updates_individual_data_string_and_decimal(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state - flex_fields should be null/empty for these fields
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] is None
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] is None

        # Perform bulk merge
        data = {"ids": [self.pdu_edit_approved_1.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_edit_approved_1.refresh_from_db()
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED

        # Verify individual data was updated
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == "Test String Value 1"
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["collection_date"] == "2024-01-15"
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] == 123.45
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["collection_date"] == "2024-01-15"

    def test_bulk_merge_updates_individual_data_boolean_and_date(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state - flex_fields should be null/empty for these fields
        self.individual2.refresh_from_db()
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"] is None
        assert self.individual2.flex_fields[self.date_attribute.name]["1"]["value"] is None

        # Perform bulk merge
        data = {"ids": [self.pdu_edit_approved_2.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_edit_approved_2.refresh_from_db()
        assert self.pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED

        # Verify individual data was updated
        self.individual2.refresh_from_db()
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"] is True
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["collection_date"] == "2024-01-16"
        assert self.individual2.flex_fields[self.date_attribute.name]["1"]["value"] == "2024-01-20"
        assert self.individual2.flex_fields[self.date_attribute.name]["1"]["collection_date"] == "2024-01-16"

    def test_bulk_merge_multiple_edits_updates_multiple_individuals(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state
        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] is None
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"] is None

        # Perform bulk merge for both edits
        data = {"ids": [self.pdu_edit_approved_1.id, self.pdu_edit_approved_2.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK

        # Verify both edits were processed
        self.pdu_edit_approved_1.refresh_from_db()
        self.pdu_edit_approved_2.refresh_from_db()
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED
        assert self.pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED

        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == "Test String Value 1"
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] == 123.45

        self.individual2.refresh_from_db()
        assert self.individual2.flex_fields[self.boolean_attribute.name]["1"]["value"] is True
        assert self.individual2.flex_fields[self.date_attribute.name]["1"]["value"] == "2024-01-20"

    def test_bulk_merge_with_non_editable_fields_skips_update(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Create edit with non-editable field
        pdu_edit_non_editable = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Non-Editable Edit",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
            edit_data=[
                {
                    "individual_uuid": str(self.individual1.id),
                    "pdu_fields": {
                        self.string_attribute.name: {
                            "value": "Should Not Be Updated",
                            "subtype": PeriodicFieldData.STRING,
                            "round_number": 1,
                            "collection_date": "2024-01-15",
                            "is_editable": False,  # Non-editable field
                        }
                    },
                }
            ],
        )

        # Verify initial state
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] is None

        # Perform bulk merge
        data = {"ids": [pdu_edit_non_editable.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        assert response.status_code == status.HTTP_200_OK
        pdu_edit_non_editable.refresh_from_db()
        assert pdu_edit_non_editable.status == PDUOnlineEdit.Status.MERGED

        # Verify individual data was NOT updated (since field was not editable)
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] is None

    def test_bulk_merge_with_existing_data_prevents_overwrite(self, create_user_role_with_permissions: Any) -> None:
        """Test that merge fails when trying to overwrite existing data."""
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_MERGE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Pre-populate individual with existing data
        self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] = "Existing Value"
        self.individual1.flex_fields[self.string_attribute.name]["1"]["collection_date"] = "2024-01-10"
        self.individual1.save()

        # Verify initial state - individual has existing data that should not be overwritten
        initial_value = self.individual1.flex_fields[self.string_attribute.name]["1"]["value"]
        initial_collection_date = self.individual1.flex_fields[self.string_attribute.name]["1"]["collection_date"]
        assert initial_value == "Existing Value"
        assert initial_collection_date == "2024-01-10"

        # Attempt to merge edit that would overwrite existing data
        data = {"ids": [self.pdu_edit_approved_1.id]}
        response = self.api_client.post(self.url_bulk_merge, data=data)

        # Should return 200 (task queued successfully), but the task should fail
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "1 PDU Online Edits queued for merging."}
        self.pdu_edit_approved_1.refresh_from_db()
        assert self.pdu_edit_approved_1.status == PDUOnlineEdit.Status.FAILED_MERGE

        # Verify individual data was NOT updated
        self.individual1.refresh_from_db()
        assert self.individual1.flex_fields[self.string_attribute.name]["1"]["value"] == initial_value
        assert (
            self.individual1.flex_fields[self.string_attribute.name]["1"]["collection_date"] == initial_collection_date
        )
        assert self.individual1.flex_fields[self.decimal_attribute.name]["1"]["value"] is None
