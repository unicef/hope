import json
from typing import Callable

from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import connection
from django.http import FileResponse
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import freezegun
import pytest
from flaky import flaky
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
)
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestPeriodicDataUpdateTemplateViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        self.pdu_template1 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template2 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template3 = PeriodicDataUpdateTemplateFactory(program=self.program1, created_by=self.user)
        self.pdu_template_program2 = PeriodicDataUpdateTemplateFactory(program=self.program2)
        self.url_list = reverse(
            "api:periodic-data-update:periodic-data-update-templates-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
            },
        )
        self.url_detail_pdu_template_program2 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program2.slug,
                "pk": self.pdu_template_program2.id,
            },
        )
        self.url_detail_pdu_template1 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
                "pk": self.pdu_template1.id,
            },
        )
        self.url_create_pdu_template_program1 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
            },
        )
        self.url_create_pdu_template_program2 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program2.slug,
            },
        )
        self.url_export_pdu_template_program1 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-export",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
                "pk": self.pdu_template1.id,
            },
        )
        self.url_export_pdu_template_program2 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-export",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program2.slug,
                "pk": self.pdu_template_program2.id,
            },
        )
        self.url_download_pdu_template_program1 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-download",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
                "pk": self.pdu_template1.id,
            },
        )
        self.url_download_pdu_template_program2 = reverse(
            "api:periodic-data-update:periodic-data-update-templates-download",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program2.slug,
                "pk": self.pdu_template_program2.id,
            },
        )

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_list_periodic_data_update_templates_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        if access_to_program:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program1)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program1)
        else:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    def test_list_periodic_data_update_templates(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 3
        assert {
            "id": self.pdu_template1.id,
            "status_display": self.pdu_template1.combined_status_display,
            "status": self.pdu_template1.combined_status,
            "number_of_records": self.pdu_template1.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template1.created_by.get_full_name(),
            "can_export": self.pdu_template1.can_export,
        } in response_json
        assert {
            "id": self.pdu_template2.id,
            "status_display": self.pdu_template2.combined_status_display,
            "status": self.pdu_template2.combined_status,
            "number_of_records": self.pdu_template2.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template2.created_by.get_full_name(),
            "can_export": self.pdu_template2.can_export,
        } in response_json
        assert {
            "id": self.pdu_template3.id,
            "status_display": self.pdu_template3.combined_status_display,
            "status": self.pdu_template3.combined_status,
            "number_of_records": self.pdu_template3.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template3.created_by.get_full_name(),
            "can_export": self.pdu_template3.can_export,
        } in response_json
        assert {
            "id": self.pdu_template_program2.id,
            "status_display": self.pdu_template_program2.combined_status_display,
            "status": self.pdu_template_program2.combined_status,
            "number_of_records": self.pdu_template_program2.number_of_records,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_template_program2.created_by.get_full_name(),
            "can_export": self.pdu_template_program2.can_export,
        } not in response_json

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_detail_periodic_data_update_template_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        if access_to_program:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program2)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program2)
        else:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        response = self.client.get(self.url_detail_pdu_template_program2)
        assert response.status_code == expected_status

        # no access to pdu_template1 for any case as it is in Program1 and user has access to Program2
        response_forbidden = self.client.get(self.url_detail_pdu_template1)
        assert response_forbidden.status_code == 403

    def test_detail_periodic_data_update_templates(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program2,
        )

        response = self.client.get(self.url_detail_pdu_template_program2)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        assert {
            "id": self.pdu_template_program2.id,
            "rounds_data": self.pdu_template_program2.rounds_data,
        } == response_json

    @pytest.mark.skip("Caching is disabled for now")
    def test_list_periodic_data_update_templates_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program1,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 12

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 5

            assert etag_second_call == etag

    @flaky(max_runs=3, min_passes=1)
    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_CREATE], [], True, status.HTTP_201_CREATED),
            ([], [Permissions.PDU_TEMPLATE_CREATE], True, status.HTTP_201_CREATED),
            (
                [Permissions.PDU_TEMPLATE_CREATE],
                [Permissions.PDU_TEMPLATE_CREATE],
                True,
                status.HTTP_201_CREATED,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_CREATE], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_TEMPLATE_CREATE], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_TEMPLATE_CREATE],
                [Permissions.PDU_TEMPLATE_CREATE],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_create_periodic_data_update_template_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        if access_to_program:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program1)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program1)
        else:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        data = {
            "rounds_data": [
                {
                    "field": "Vaccination Records Update",
                    "round": 2,
                    "round_name": "February vaccination",
                },
                {
                    "field": "Health Records Update",
                    "round": 4,
                    "round_name": "April",
                },
            ],
            "filters": {
                "received_assistance": True,
            },
        }
        response = self.client.post(self.url_create_pdu_template_program1, data=data)
        assert response.status_code == expected_status

        # no access to Program2
        response_forbidden = self.client.post(self.url_create_pdu_template_program2, data=data)
        assert response_forbidden.status_code == 403

    def test_create_periodic_data_update_template(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_CREATE],
            self.afghanistan,
            self.program1,
        )
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
        expected_result = [
            {
                "field": "vaccination_records_update",
                "round": 2,
                "round_name": "February vaccination",
                "number_of_records": 0,
            },
            {"field": "health_records_update", "round": 4, "round_name": "April", "number_of_records": 0},
        ]
        response = self.client.post(self.url_create_pdu_template_program1, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        response_json = response.json()
        assert PeriodicDataUpdateTemplate.objects.filter(id=response_json["id"]).exists()
        template = PeriodicDataUpdateTemplate.objects.get(id=response_json["id"])
        assert template.program == self.program1
        assert template.business_area == self.afghanistan
        assert template.rounds_data == expected_result
        assert template.filters == data["filters"]
        assert template.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert PeriodicDataUpdateTemplate.objects.filter(id=response_json["id"]).first().file is not None

    def test_create_periodic_data_update_template_duplicate_field(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_CREATE],
            self.afghanistan,
            self.program1,
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
        response = self.client.post(self.url_create_pdu_template_program1, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == {"rounds_data": ["Each Field can only be used once in the template."]}

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_CREATE], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_TEMPLATE_CREATE], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_TEMPLATE_CREATE],
                [Permissions.PDU_TEMPLATE_CREATE],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_CREATE], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_TEMPLATE_CREATE], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_TEMPLATE_CREATE],
                [Permissions.PDU_TEMPLATE_CREATE],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_export_periodic_data_update_template_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        if access_to_program:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program1)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program1)
        else:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.TO_EXPORT
        self.pdu_template1.save()

        response = self.client.post(self.url_export_pdu_template_program1)
        assert response.status_code == expected_status

        # no access to Program2
        response_forbidden = self.client.post(self.url_export_pdu_template_program2)
        assert response_forbidden.status_code == 403

    def test_export_periodic_data_update_template(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_CREATE],
            self.afghanistan,
            self.program1,
        )

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.TO_EXPORT
        self.pdu_template1.file = None
        self.pdu_template1.save()

        response = self.client.post(self.url_export_pdu_template_program1)
        assert response.status_code == status.HTTP_200_OK

        self.pdu_template1.refresh_from_db()
        assert self.pdu_template1.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert self.pdu_template1.file is not None

    def test_export_periodic_data_update_template_already_exporting(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_CREATE],
            self.afghanistan,
            self.program1,
        )

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTING
        self.pdu_template1.file = None
        self.pdu_template1.save()

        response = self.client.post(self.url_export_pdu_template_program1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == ["Template is already being exported"]

    def test_export_periodic_data_update_template_already_exported(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_CREATE],
            self.afghanistan,
            self.program1,
        )

        file = FileTemp.objects.create(
            object_id=self.pdu_template1.pk,
            content_type=get_content_type_for_model(self.pdu_template1),
            created=timezone.now(),
            file=ContentFile(b"Test content", f"Test File {self.pdu_template1.pk}.xlsx"),
        )
        self.pdu_template1.file = file
        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        self.pdu_template1.save()

        response = self.client.post(self.url_export_pdu_template_program1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == ["Template is already exported"]

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_DOWNLOAD], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_TEMPLATE_DOWNLOAD], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_TEMPLATE_DOWNLOAD],
                [Permissions.PDU_TEMPLATE_DOWNLOAD],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_TEMPLATE_DOWNLOAD], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_TEMPLATE_DOWNLOAD], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_TEMPLATE_DOWNLOAD],
                [Permissions.PDU_TEMPLATE_DOWNLOAD],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_download_periodic_data_update_template_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        if access_to_program:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program1)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program1)
        else:
            create_user_role_with_permissions(self.user, permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED

        file = FileTemp.objects.create(
            object_id=self.pdu_template1.pk,
            content_type=get_content_type_for_model(self.pdu_template1),
            created=timezone.now(),
            file=ContentFile(b"Test content", f"Test File {self.pdu_template1.pk}.xlsx"),
        )
        self.pdu_template1.file = file
        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        self.pdu_template1.save()

        response = self.client.get(self.url_download_pdu_template_program1)
        assert response.status_code == expected_status

        # no access to Program2
        response_forbidden = self.client.get(self.url_download_pdu_template_program2)
        assert response_forbidden.status_code == 403

    def test_download_periodic_data_update_template(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            self.afghanistan,
            self.program1,
        )

        file = FileTemp.objects.create(
            object_id=self.pdu_template1.pk,
            content_type=get_content_type_for_model(self.pdu_template1),
            created=timezone.now(),
            file=ContentFile(b"Test content", f"Test File {self.pdu_template1.pk}.xlsx"),
        )
        self.pdu_template1.file = file
        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        self.pdu_template1.save()

        response = self.client.get(self.url_download_pdu_template_program1)
        assert response.status_code == status.HTTP_200_OK

        self.pdu_template1.refresh_from_db()
        assert self.pdu_template1.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert isinstance(response, FileResponse) is True
        assert f'filename="{file.file.name}"' in response["Content-Disposition"]
        assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert response.getvalue() == b"Test content"

    def test_download_periodic_data_update_template_not_exported(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            self.afghanistan,
            self.program1,
        )

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.TO_EXPORT
        self.pdu_template1.save()

        response = self.client.get(self.url_download_pdu_template_program1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == ["Template is not exported yet"]

    def test_download_periodic_data_update_template_no_records(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            self.afghanistan,
            self.program1,
        )

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        self.pdu_template1.number_of_records = 0
        self.pdu_template1.save()

        response = self.client.get(self.url_download_pdu_template_program1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == ["Template has no records"]

    def test_download_periodic_data_update_template_no_file(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_TEMPLATE_DOWNLOAD],
            self.afghanistan,
            self.program1,
        )

        self.pdu_template1.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        self.pdu_template1.number_of_records = 1
        self.pdu_template1.file = None
        self.pdu_template1.save()

        response = self.client.get(self.url_download_pdu_template_program1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response_json = response.json()
        assert response_json == ["Template file is missing"]
