from typing import Any

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport

pytestmark = pytest.mark.django_db


class TestProgramDeduplicationFlagsSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.deduplication_flags_url_name = "api:programs:programs-deduplication-flags"

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )

    def test_deduplication_flags_can_run_deduplication_and_deduplication_enabled(
        self, create_user_role_with_permissions: Any
    ) -> None:
        self.program.biometric_deduplication_enabled = True
        self.program.save()
        # deduplication engine in progress - > deduplication disabled
        RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.MERGED,
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(
            reverse(
                self.deduplication_flags_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "can_run_deduplication": True,
            "is_deduplication_disabled": False,
        }

    def test_deduplication_flags_can_run_deduplication_and_deduplication_engine_in_progress(
        self, create_user_role_with_permissions: Any
    ) -> None:
        self.program.biometric_deduplication_enabled = True
        self.program.save()
        # deduplication engine in progress - > deduplication disabled
        RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(
            reverse(
                self.deduplication_flags_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "can_run_deduplication": True,
            "is_deduplication_disabled": True,
        }

    def test_deduplication_flags_can_run_deduplication_and_all_rdis_deduplicated(
        self, create_user_role_with_permissions: Any
    ) -> None:
        self.program.biometric_deduplication_enabled = True
        self.program.save()
        # deduplication engine in progress - > deduplication disabled
        RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        assert RegistrationDataImport.objects.filter(program=self.program).count() == 1
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(
            reverse(
                self.deduplication_flags_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "can_run_deduplication": True,
            "is_deduplication_disabled": True,
        }

    def test_deduplication_flags_can_run_deduplication_and_not_all_rdis_deduplicated(
        self, create_user_role_with_permissions: Any
    ) -> None:
        self.program.biometric_deduplication_enabled = True
        self.program.save()
        # deduplication engine in progress - > deduplication disabled
        RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.MERGED,
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(
            reverse(
                self.deduplication_flags_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "can_run_deduplication": True,
            "is_deduplication_disabled": False,
        }

    def test_deduplication_flags_cannot_run_deduplication_and_rdi_merge_in_progress(
        self, create_user_role_with_permissions: Any
    ) -> None:
        self.program.biometric_deduplication_enabled = False
        self.program.save()
        # deduplication engine in progress - > deduplication disabled
        RegistrationDataImportFactory(
            program=self.program,
            status=RegistrationDataImport.MERGING,
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.client.get(
            reverse(
                self.deduplication_flags_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "slug": self.program.slug,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "can_run_deduplication": False,
            "is_deduplication_disabled": True,
        }
