from unittest.mock import patch
from typing import Any, List

from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentFactory

from hope.apps.core.models import PeriodicFieldData
from hope.apps.payment.models import Payment

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory, RoleFactory, RoleAssignmentFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    PeriodicFieldDataFactory,
    FlexibleAttributeForPDUFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.apps.program.models import Program
from hope.apps.periodic_data_update.models import PDUOnlineEdit

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditCreate:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
    ) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=self.afghanistan)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.household1, individuals1 = create_household_and_individuals(
            household_data={
                "business_area": self.afghanistan,
                "program_id": self.program.pk,
            },
            individuals_data=[
                {
                    "business_area": self.afghanistan,
                    "program_id": self.program.pk,
                }
            ],
        )
        self.household2, individuals2 = create_household_and_individuals(
            household_data={
                "business_area": self.afghanistan,
                "program_id": self.program.pk,
            },
            individuals_data=[
                {
                    "business_area": self.afghanistan,
                    "program_id": self.program.pk,
                }
            ],
        )

        # self.household2 with assistance
        PaymentFactory(
            household=self.household2,
            program=self.program,
            status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        )

        pdu_data_vaccination = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=5,
            rounds_names=[
                "January vaccination",
                "February vaccination",
                "March vaccination",
                "April vaccination",
                "May vaccination",
            ],
        )
        self.pdu_field_vaccination = FlexibleAttributeForPDUFactory(
            program=self.program,
            label="Vaccination Records Update",
            pdu_data=pdu_data_vaccination,
        )

        pdu_data_health = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=5,
            rounds_names=["January", "February", "March", "April", "May"],
        )
        self.pdu_field_health = FlexibleAttributeForPDUFactory(
            program=self.program,
            label="Health Records Update",
            pdu_data=pdu_data_health,
        )
        self.individual2 = individuals2[0]
        populate_pdu_with_null_values(self.program, individuals1[0].flex_fields)
        populate_pdu_with_null_values(self.program, self.individual2.flex_fields)

        self.base_data = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
                {
                    "field": "health_records_update",
                    "round": 4,
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }

        self.url_create = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

    @patch("hope.apps.periodic_data_update.models.PDUOnlineEdit.queue")
    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_201_CREATED),
            ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_pdu_online_edit_permissions(
        self,
        task_mock: Any,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.post(self.url_create, data=self.base_data)
        assert response.status_code == expected_status

    def test_create_pdu_online_edit_base(self, create_user_role_with_permissions: Any):
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE, Permissions.PDU_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.post(self.url_create, data=self.base_data)
        assert response.status_code == status.HTTP_201_CREATED

        assert PDUOnlineEdit.objects.count() == 1
        pdu_online_edit = PDUOnlineEdit.objects.first()
        assert pdu_online_edit.name is None
        assert pdu_online_edit.business_area == self.afghanistan
        assert pdu_online_edit.program == self.program
        assert pdu_online_edit.status == PDUOnlineEdit.Status.NEW
        assert pdu_online_edit.created_by == self.user
        assert pdu_online_edit.approved_by is None
        assert pdu_online_edit.approved_at is None
        assert pdu_online_edit.number_of_records == 1
        assert pdu_online_edit.authorized_users.count() == 0
        assert pdu_online_edit.edit_data == [
            {
                "individual_uuid": str(self.household2.individuals.first().pk),
                "unicef_id": self.household2.individuals.first().unicef_id,
                "first_name": self.household2.individuals.first().given_name,
                "last_name": self.household2.individuals.first().family_name,
                "pdu_fields": {
                    "vaccination_records_update": {
                        "round_number": 2,
                        "round_name": "February vaccination",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "health_records_update": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                },
            }
        ]

        # check response
        response_json = response.json()
        assert response_json["id"] == pdu_online_edit.id
        assert response_json["name"] is None
        assert response_json["created_by"] == self.user.get_full_name()
        assert response_json["authorized_users"] == []

        # check data in detail view
        url_detail = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": pdu_online_edit.id,
            },
        )
        response_detail = self.api_client.get(url_detail)
        assert response_detail.status_code == status.HTTP_200_OK
        response_json_detail = response_detail.json()
        assert response_json_detail["id"] == pdu_online_edit.id
        assert response_json_detail["name"] is None
        assert response_json_detail["number_of_records"] == 1
        assert response_json_detail["created_by"] == self.user.get_full_name()
        assert response_json_detail["created_at"] == f"{pdu_online_edit.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"
        assert response_json_detail["status"] == PDUOnlineEdit.Status.NEW
        assert response_json_detail["status_display"] == PDUOnlineEdit.Status.NEW.label
        assert response_json_detail["is_authorized"] is False
        assert response_json_detail["approved_by"] == ""
        assert response_json_detail["approved_at"] is None
        assert response_json_detail["edit_data"] == [
            {
                "individual_uuid": str(self.household2.individuals.first().pk),
                "unicef_id": self.household2.individuals.first().unicef_id,
                "first_name": self.household2.individuals.first().given_name,
                "last_name": self.household2.individuals.first().family_name,
                "pdu_fields": {
                    "vaccination_records_update": {
                        "round_number": 2,
                        "round_name": "February vaccination",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                    "health_records_update": {
                        "round_number": 4,
                        "round_name": "April",
                        "value": None,
                        "collection_date": None,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "is_editable": True,
                    },
                },
            }
        ]
        assert response_json_detail["authorized_users"] == []
        assert response_json_detail["sent_back_comment"] is None

    def test_create_pdu_online_edit_with_name(self, create_user_role_with_permissions: Any):
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        data = {
            "name": "Test Online Edit",
            **self.base_data,
        }

        response = self.api_client.post(self.url_create, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        assert PDUOnlineEdit.objects.count() == 1
        pdu_online_edit = PDUOnlineEdit.objects.first()
        assert pdu_online_edit.name == "Test Online Edit"
        assert pdu_online_edit.status == PDUOnlineEdit.Status.NEW
        assert pdu_online_edit.number_of_records == 1

    def test_create_pdu_online_edit_with_authorized_users(self, create_user_role_with_permissions: Any):
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        partner_empty = PartnerFactory(name="EmptyPartner")
        user_can_approve = UserFactory(partner=partner_empty, first_name="Bob")
        approve_role = RoleFactory(name="Approve", permissions=[Permissions.PDU_ONLINE_APPROVE.value])
        RoleAssignmentFactory(
            user=user_can_approve,
            role=approve_role,
            business_area=self.afghanistan,
            program=self.program,
        )
        user_can_all = UserFactory(partner=partner_empty, first_name="David")
        can_all_role = RoleFactory(
            name="Can All",
            permissions=[
                Permissions.PDU_ONLINE_SAVE_DATA.value,
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
            ],
        )
        RoleAssignmentFactory(
            user=user_can_all,
            role=can_all_role,
            business_area=self.afghanistan,
            program=self.program,
        )
        can_merge_but_not_authorized = UserFactory(partner=partner_empty, first_name="Eve")
        merge_role = RoleFactory(name="Merge", permissions=[Permissions.PDU_ONLINE_MERGE.value])
        RoleAssignmentFactory(
            user=can_merge_but_not_authorized,
            role=merge_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {
            "authorized_users": [user_can_approve.pk, user_can_all.pk],
            **self.base_data,
        }

        response = self.api_client.post(self.url_create, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        assert PDUOnlineEdit.objects.count() == 1
        pdu_online_edit = PDUOnlineEdit.objects.first()
        assert pdu_online_edit.authorized_users.count() == 2
        assert pdu_online_edit.authorized_users.filter(pk=user_can_approve.pk).exists()
        assert pdu_online_edit.authorized_users.filter(pk=user_can_all.pk).exists()
        assert not pdu_online_edit.authorized_users.filter(pk=can_merge_but_not_authorized.pk).exists()

    def test_create_pdu_online_edit_duplicate_field(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        data = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
                {
                    "field": "vaccination_records_update",
                    "round": 4,
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }

        response = self.api_client.post(self.url_create, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert response_json == {"rounds_data": ["Each Field can only be used once in the template."]}

    def test_create_pdu_online_edit_already_covered_round(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        data_1 = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
                {
                    "field": "health_records_update",
                    "round": 4,
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }
        response_1 = self.api_client.post(self.url_create, data=data_1)
        assert response_1.status_code == status.HTTP_201_CREATED

        response_json_1 = response_1.json()
        assert PDUOnlineEdit.objects.filter(id=response_json_1["id"]).exists()
        self.pdu_field_vaccination.refresh_from_db()
        self.pdu_field_health.refresh_from_db()
        assert self.pdu_field_vaccination.pdu_data.rounds_covered == 2
        assert self.pdu_field_health.pdu_data.rounds_covered == 4

        # Test creating an edit with a round that is already covered by the first edit
        data_2 = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,  # This round is already covered by the first edit
                    "round_name": "February vaccination",
                },
                {
                    "field": "health_records_update",
                    "round": 5,  # This round is not covered by the first edit
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }
        response_2 = self.api_client.post(self.url_create, data=data_2)
        assert response_2.status_code == status.HTTP_400_BAD_REQUEST
        response_json_2 = response_2.json()
        assert response_json_2 == [
            "Template for round 2 of field 'Vaccination Records Update' has already been created."
        ]

    def test_create_pdu_online_edit_field_is_editable_flag(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # individual already has a value for vaccination_records_update in round 2 - value should be retrieved and is_editable should be False
        self.individual2.flex_fields["vaccination_records_update"]["2"]["value"] = 1.0
        self.individual2.save()

        data = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
                {
                    "field": "health_records_update",
                    "round": 4,
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }

        response = self.api_client.post(self.url_create, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        pdu_online_edit = PDUOnlineEdit.objects.first()
        assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["value"] == 1.0
        assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["collection_date"] is None
        assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["is_editable"] is False

        assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["value"] is None
        assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["collection_date"] is None
        assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["is_editable"] is True

    def test_create_pdu_online_edit_with_covered_individual(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # individual already has a values for all pdu fields used in the edit - should be excluded from the edit
        self.individual2.flex_fields["vaccination_records_update"]["2"]["value"] = 1.0
        self.individual2.save()

        data = {
            "rounds_data": [
                {
                    "field": "vaccination_records_update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }

        response = self.api_client.post(self.url_create, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        pdu_online_edit = PDUOnlineEdit.objects.first()
        assert pdu_online_edit.number_of_records == 0
