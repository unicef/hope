from typing import Any, List

from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import PeriodicFieldData
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditSaveData:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.pdu_online_edit = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            status=PDUOnlineEdit.Status.NEW,
            authorized_users=[self.user],
            edit_data=[
                {
                    "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
                    "unicef_id": "IND-11",
                    "first_name": "Aaron",
                    "last_name": "Heath",
                    "pdu_fields": {
                        "vaccination_records": {
                            "round_number": 1,
                            "round_name": "January vaccination",
                            "value": None,
                            "collection_date": None,
                            "subtype": PeriodicFieldData.DECIMAL,
                            "label": "Vaccination Records",
                            "field_name": "vaccination_records",
                            "is_editable": True,
                        },
                        "health_check": {
                            "round_number": 2,
                            "round_name": "February health check",
                            "value": "value 1",  # Can be already filled out in this Edit in previous save action
                            "collection_date": "2024-01-19",
                            "subtype": PeriodicFieldData.STRING,
                            "label": "Health Check",
                            "field_name": "health_check",
                            "is_editable": True,
                        },
                        "visit_date": {
                            "round_number": 1,
                            "round_name": "January visit",
                            "value": None,
                            "collection_date": None,
                            "subtype": PeriodicFieldData.DATE,
                            "label": "Visit Date",
                            "field_name": "visit_date",
                            "is_editable": True,
                        },
                        "health_status": {
                            "round_number": 1,
                            "round_name": "January status",
                            "value": None,
                            "collection_date": None,
                            "subtype": PeriodicFieldData.BOOL,
                            "label": "Health Status",
                            "field_name": "health_status",
                            "is_editable": True,
                        },
                        "completed_vaccination": {
                            "round_number": 1,
                            "round_name": "January vaccination",
                            "value": True,
                            "collection_date": "2024-01-01",
                            "subtype": PeriodicFieldData.BOOL,
                            "label": "Completed Vaccination",
                            "field_name": "completed_vaccination",
                            "is_editable": False,  # Not editable
                        },
                    },
                }
            ],
        )

        self.initial_request_pdu_fields_data = {
            "vaccination_records": {
                "round_number": 1,
                "value": None,
                "subtype": PeriodicFieldData.DECIMAL,
                "label": "Vaccination Records",
                "field_name": "vaccination_records",
                "is_editable": True,
            },
            "health_check": {
                "round_number": 2,
                "value": "value 1",
                "subtype": PeriodicFieldData.STRING,
                "label": "Health Check",
                "field_name": "health_check",
                "is_editable": True,
            },
            "visit_date": {
                "round_number": 1,
                "value": None,
                "subtype": PeriodicFieldData.DATE,
                "label": "Visit Date",
                "field_name": "visit_date",
                "is_editable": True,
            },
            "health_status": {
                "round_number": 1,
                "value": None,
                "subtype": PeriodicFieldData.BOOL,
                "label": "Health Status",
                "field_name": "health_status",
                "is_editable": True,
            },
            "completed_vaccination": {
                "round_number": 1,
                "value": True,
                "subtype": PeriodicFieldData.BOOL,
                "label": "Completed Vaccination",
                "field_name": "completed_vaccination",
                "is_editable": False,
            },
        }

    def _get_save_data_url(self, pdu_edit_id: int) -> str:
        return reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-save-data",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": pdu_edit_id,
            },
        )

    def _create_request_data(self, pdu_fields: dict, field_name: str, new_value: Any) -> dict:
        updated_fields = pdu_fields.copy()
        updated_fields[field_name] = {**updated_fields[field_name], "value": new_value}
        return updated_fields

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_200_OK),
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_save_data_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == expected_status

    @freeze_time("2024-01-20")
    def test_save_data_success_decimal_field(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 15.5)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Edit data saved successfully."

        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]
        vaccination_field = individual_data["pdu_fields"]["vaccination_records"]
        assert vaccination_field["value"] == 15.5
        assert vaccination_field["collection_date"] == "2024-01-20"

        # Verify other fields remain unchanged
        health_check_field = individual_data["pdu_fields"]["health_check"]
        assert health_check_field["value"] == "value 1"
        assert health_check_field["collection_date"] == "2024-01-19"

    def test_save_data_success_string_field(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(
            self.initial_request_pdu_fields_data, "health_check", "Good condition"
        )

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]
        health_field = individual_data["pdu_fields"]["health_check"]
        assert health_field["value"] == "Good condition"

        # Verify other fields remain unchanged
        vaccination_field = individual_data["pdu_fields"]["vaccination_records"]
        assert vaccination_field["value"] is None

    def test_save_data_success_boolean_field(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "health_status", True)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]
        health_status_field = individual_data["pdu_fields"]["health_status"]
        assert health_status_field["value"] is True

    def test_save_data_success_date_field(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "visit_date", "2024-01-15")

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]
        visit_date_field = individual_data["pdu_fields"]["visit_date"]
        assert visit_date_field["value"] == "2024-01-15"

    def test_save_data_no_value_change(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": self.initial_request_pdu_fields_data,  # No value change
        }

        edit_data_before = self.pdu_online_edit.edit_data.copy()

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]
        assert individual_data["pdu_fields"] == edit_data_before[0]["pdu_fields"]

    def test_save_data_not_authorized_user(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Remove user from authorized users
        self.pdu_online_edit.authorized_users.remove(self.user)

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "You are not an authorized user for this PDU online edit." in response.json()["detail"]

    def test_save_data_invalid_status(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Change status to APPROVED (should not allow editing)
        self.pdu_online_edit.status = PDUOnlineEdit.Status.APPROVED
        self.pdu_online_edit.save()

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "PDU Online Edit data can only be saved when status is 'New'" in response.json()[0]

    def test_serializer_validation_missing_individual_uuid(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)

        data = {
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "individual_uuid" in response.json()

    def test_serializer_validation_invalid_individual_uuid(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)

        data = {
            "individual_uuid": "invalid-uuid",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "individual_uuid" in response.json()

    def test_serializer_validation_individual_not_found_in_edit_data(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 10.5)
        uuid_not_in_edit = "4d9a1db2-23bd-46a8-8a2c-1d51891d6f6d"

        data = {
            "individual_uuid": uuid_not_in_edit,
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            f"Individual with UUID {uuid_not_in_edit} not found in this PDU Online Edit"
            in response.json()["non_field_errors"][0]
        )

    def test_serializer_validation_pdu_fields_not_dict(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": "invalid",  # Should be dict
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Expected a dictionary of items but got type "str".' in response.json()["pdu_fields"][0]

    def test_serializer_validation_field_data_not_dict(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": {
                "vaccination_records": "invalid"  # Should be dict
            },
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            'Expected a dictionary of items but got type "str".'
            in response.json()["pdu_fields"]["vaccination_records"][0]
        )

    def test_serializer_validation_missing_required_keys(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": {
                "vaccination_records": {
                    "value": 10.5,
                    # Missing required keys: subtype, is_editable, round_number
                },
            },
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Field 'vaccination_records' must contain keys: " in response.json()["non_field_errors"][0]

    def test_serializer_validation_field_not_in_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": {
                "non_existent_field": {
                    "round_number": 1,
                    "value": 10.5,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "is_editable": True,
                },
            },
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Field 'non_existent_field' is not within fields selected for this edit"
            in response.json()["non_field_errors"][0]
        )

    def test_serializer_validation_non_editable_field_modification(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "completed_vaccination", False)

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Field 'completed_vaccination' is not editable and cannot be modified"
            in response.json()["non_field_errors"][0]
        )

    def test_serializer_validation_invalid_boolean_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        pdu_fields = self.initial_request_pdu_fields_data
        updated_fields = self._create_request_data(pdu_fields, "health_status", "invalid_bool")  # Should be boolean

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Field 'health_status' expects a boolean value, got str" in response.json()["non_field_errors"][0]

    def test_serializer_validation_invalid_decimal_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(
            self.initial_request_pdu_fields_data, "vaccination_records", "not_a_number"
        )  # Should be number

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Field 'vaccination_records' expects a number value, got str" in response.json()["non_field_errors"][0]

    def test_serializer_validation_invalid_string_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(
            self.initial_request_pdu_fields_data, "health_check", 123
        )  # Should be string

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Field 'health_check' expects a string value, got int" in response.json()["non_field_errors"][0]

    def test_serializer_validation_invalid_date_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(
            self.initial_request_pdu_fields_data, "visit_date", 20240115
        )  # Should be string

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Field 'visit_date' expects a string value for date, got int" in response.json()["non_field_errors"][0]

    def test_serializer_validation_invalid_date_format(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(
            self.initial_request_pdu_fields_data, "visit_date", "15/01/2024"
        )  # Should be YYYY-MM-DD

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }
        response = self.api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            "Field 'visit_date' has invalid date format. Expected YYYY-MM-DD" in response.json()["non_field_errors"][0]
        )

    @freeze_time("2024-02-05 14:15:30")
    def test_save_data_multiple_field_types_in_one_request(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_save_data_url(self.pdu_online_edit.id)
        updated_fields = self._create_request_data(self.initial_request_pdu_fields_data, "vaccination_records", 25.5)
        updated_fields = self._create_request_data(updated_fields, "health_check", "Excellent")
        updated_fields = self._create_request_data(updated_fields, "health_status", True)
        updated_fields = self._create_request_data(updated_fields, "visit_date", "2024-02-01")

        data = {
            "individual_uuid": "2b9a1db2-23bd-46a8-8a2c-1d51891d6f6b",
            "pdu_fields": updated_fields,
        }

        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK

        self.pdu_online_edit.refresh_from_db()
        individual_data = self.pdu_online_edit.edit_data[0]

        # Verify all fields were updated correctly
        assert individual_data["pdu_fields"]["vaccination_records"]["value"] == 25.5
        assert individual_data["pdu_fields"]["vaccination_records"]["collection_date"] == "2024-02-05"

        assert individual_data["pdu_fields"]["health_check"]["value"] == "Excellent"
        assert individual_data["pdu_fields"]["health_check"]["collection_date"] == "2024-02-05"

        assert individual_data["pdu_fields"]["health_status"]["value"] is True
        assert individual_data["pdu_fields"]["health_status"]["collection_date"] == "2024-02-05"

        assert individual_data["pdu_fields"]["visit_date"]["value"] == "2024-02-01"
        assert individual_data["pdu_fields"]["visit_date"]["collection_date"] == "2024-02-05"

        # Verify non-editable field remains unchanged
        assert individual_data["pdu_fields"]["completed_vaccination"]["value"] is True
        assert individual_data["pdu_fields"]["completed_vaccination"]["collection_date"] == "2024-01-01"
