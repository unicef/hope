import json
from typing import Callable

import freezegun
import pytest
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (BusinessAreaFactory,
                                               PartnerFactory, UserFactory)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import \
    RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestRegistrationDataImportViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        self.rdi1 = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program1,
            status=RegistrationDataImport.IMPORTING,
            name="RDI A 1",
        )
        self.rdi2 = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program1,
            status=RegistrationDataImport.IN_REVIEW,
            name="RDI A 2",
        )
        self.rdi3 = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program1,
            status=RegistrationDataImport.MERGED,
            name="RDI B 1",
        )
        self.rdi_program2 = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program2,
            status=RegistrationDataImport.MERGED,
            name="RDI Program 2",
        )

        self.url_list = reverse(
            "api:registration-data:registration-data-imports-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
            },
        )

    @pytest.mark.parametrize(
        "user_permissions, partner_permissions, is_permission_in_correct_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.RDI_VIEW_LIST], [], True, status.HTTP_200_OK),
            ([], [Permissions.RDI_VIEW_LIST], True, status.HTTP_200_OK),
            (
                [Permissions.RDI_VIEW_LIST],
                [Permissions.RDI_VIEW_LIST],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.RDI_VIEW_LIST], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.RDI_VIEW_LIST], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.RDI_VIEW_LIST],
                [Permissions.RDI_VIEW_LIST],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_list_registration_data_imports_permission(
        self,
        user_permissions: list,
        partner_permissions: list,
        is_permission_in_correct_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)

        if is_permission_in_correct_program:
            create_user_role_with_permissions(self.user, user_permissions, self.afghanistan, self.program1)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan, self.program1)
        else:
            # role will be created for different program
            create_user_role_with_permissions(self.user, user_permissions, self.afghanistan)
            create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    def test_list_registration_data_imports(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.RDI_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 3

        assert {
            "id": str(self.rdi1.id),
            "name": self.rdi1.name,
            "status": self.rdi1.get_status_display(),
            "imported_by": self.rdi1.imported_by.get_full_name(),
            "data_source": self.rdi1.get_data_source_display(),
            "created_at": "2022-01-01T00:00:00Z",
            "erased": self.rdi1.erased,
            "import_date": "2022-01-01T00:00:00Z",
            "number_of_households": self.rdi1.number_of_households,
            "number_of_individuals": self.rdi1.number_of_individuals,
            "biometric_deduplicated": self.rdi1.biometric_deduplicated,
        } in response_json
        assert {
            "id": str(self.rdi2.id),
            "name": self.rdi2.name,
            "status": self.rdi2.get_status_display(),
            "imported_by": self.rdi2.imported_by.get_full_name(),
            "data_source": self.rdi2.get_data_source_display(),
            "created_at": "2022-01-01T00:00:00Z",
            "erased": self.rdi2.erased,
            "import_date": "2022-01-01T00:00:00Z",
            "number_of_households": self.rdi2.number_of_households,
            "number_of_individuals": self.rdi2.number_of_individuals,
            "biometric_deduplicated": self.rdi2.biometric_deduplicated,
        } in response_json
        assert {
            "id": str(self.rdi3.id),
            "name": self.rdi3.name,
            "status": self.rdi3.get_status_display(),
            "imported_by": self.rdi3.imported_by.get_full_name(),
            "data_source": self.rdi3.get_data_source_display(),
            "created_at": "2022-01-01T00:00:00Z",
            "erased": self.rdi3.erased,
            "import_date": "2022-01-01T00:00:00Z",
            "number_of_households": self.rdi3.number_of_households,
            "number_of_individuals": self.rdi3.number_of_individuals,
            "biometric_deduplicated": self.rdi3.biometric_deduplicated,
        } in response_json
        assert {
            "id": str(self.rdi_program2.id),
            "name": self.rdi_program2.name,
            "status": self.rdi1.get_status_display(),
            "imported_by": self.rdi1.imported_by.get_full_name(),
            "data_source": self.rdi1.get_data_source_display(),
            "created_at": "2022-01-01T00:00:00Z",
            "erased": self.rdi1.erased,
            "import_date": "2022-01-01T00:00:00Z",
            "number_of_households": self.rdi1.number_of_households,
            "number_of_individuals": self.rdi1.number_of_individuals,
            "biometric_deduplicated": self.rdi1.biometric_deduplicated,
        } not in response_json

    def test_list_registration_data_imports_filter(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.RDI_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list, {"status": RegistrationDataImport.MERGED})
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 1

    def test_list_registration_data_imports_search_by_name(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.RDI_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list, {"search": "RDI A"})
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 2

    def test_list_registration_data_imports_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.RDI_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 16

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 4

            assert etag_second_call == etag

        # After update, it does not use the cached data
        self.rdi1.status = RegistrationDataImport.MERGE_ERROR
        self.rdi1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 10  # less than the first call because of cached permissions

            assert etag_call_after_update != etag

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 4

            assert etag_call_after_update_second_call == etag_call_after_update
