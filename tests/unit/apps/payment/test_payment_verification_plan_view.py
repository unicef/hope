from io import BytesIO
from typing import Any, List, Optional

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

import pytest
from openpyxl import Workbook
from rest_framework import status

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentPlan,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    build_summary,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


def generate_valid_xlsx_file(
    name: str = "unit_test.xlsx", worksheet_title_list: Optional[List[str]] = None
) -> SimpleUploadedFile:
    if worksheet_title_list is None:
        worksheet_title_list = ["Test"]
    wb = Workbook()
    for worksheet_title in worksheet_title_list:
        wb.create_sheet(title=worksheet_title)
    ws = wb.active
    ws["A1"] = "People"
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return SimpleUploadedFile(
        name, file_stream.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


class TestPaymentVerificationViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.client = api_client(self.user)
        self.pp = PaymentPlanFactory(
            name="Payment Plan",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.FINISHED,
            created_by=self.user,
            created_at="2022-02-24",
        )
        PaymentVerificationSummary.objects.create(payment_plan=self.pp)
        build_summary(self.pp)
        self.payment = PaymentFactory(
            parent=self.pp, status=Payment.STATUS_SUCCESS, delivered_quantity=999, entitlement_quantity=112
        )
        self.pvp = PaymentVerificationPlanFactory(
            payment_plan=self.pp,
            sampling=PaymentVerificationPlan.SAMPLING_RANDOM,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
        )
        url_kwargs = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "pk": str(self.pp.pk),
        }
        url_kwargs_id = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "pk": str(self.pp.pk),
            "verification_plan_id": str(self.pvp.pk),
        }
        self.url_list = reverse(
            "api:payments:payment-verifications-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_details = reverse("api:payments:payment-verifications-detail", kwargs=url_kwargs)
        self.url_create = reverse(
            "api:payments:payment-verifications-create-payment-verification-plan", kwargs=url_kwargs
        )
        self.url_update = reverse(
            "api:payments:payment-verifications-update-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_activate = reverse(
            "api:payments:payment-verifications-activate-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_finish = reverse(
            "api:payments:payment-verifications-finish-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_discard = reverse(
            "api:payments:payment-verifications-discard-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_invalid = reverse(
            "api:payments:payment-verifications-invalid-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_delete = reverse(
            "api:payments:payment-verifications-delete-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_export_xlsx = reverse(
            "api:payments:payment-verifications-export-xlsx-payment-verification-plan", kwargs=url_kwargs_id
        )
        self.url_import_xlsx = reverse(
            "api:payments:payment-verifications-import-xlsx-payment-verification-plan", kwargs=url_kwargs_id
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_VIEW_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_get_list(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            pv = resp_data["results"][0]
            assert "PENDING" == pv["verification_status"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_details(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == resp_data["available_payment_records_count"]
            assert 1 == resp_data["eligible_payments_count"]
            assert "Pending" == resp_data["payment_verification_plans"][0]["status"]
            assert "Random sampling" == resp_data["payment_verification_plans"][0]["sampling"]
            assert (
                PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
                == resp_data["payment_verification_plans"][0]["verification_channel"]
            )
            assert "Pending" == resp_data["payment_verification_summary"]["status"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_CREATE], status.HTTP_201_CREATED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_create_pvp(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(
            self.url_create,
            {
                "sampling": "FULL_LIST",
                "full_list_arguments": {"excluded_admin_areas": []},
                "verification_channel": PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
                "rapid_pro_arguments": None,
                "random_sampling_arguments": None,
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert response.status_code == status.HTTP_201_CREATED
            resp_data = response.json()
            assert "id" in resp_data
            assert 2 == len(resp_data["payment_verification_plans"])
            pvp = resp_data["payment_verification_plans"][1]
            assert "Pending" == pvp["status"]
            assert PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX == pvp["verification_channel"]
            assert "Full list" == pvp["sampling"]
            assert pvp["excluded_admin_areas_filter"] == []
            assert "Pending" == resp_data["payment_verification_summary"]["status"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_pvp(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.patch(
            self.url_update,
            {
                "sampling": "FULL_LIST",
                "full_list_arguments": {"excluded_admin_areas": []},
                "verification_channel": "MANUAL",
                "rapid_pro_arguments": None,
                "random_sampling_arguments": None,
            },
            format="json",
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            pvp = resp_data["payment_verification_plans"][0]
            assert "Pending" == pvp["status"]
            assert "MANUAL" == pvp["verification_channel"]
            assert "Full list" == pvp["sampling"]
            assert pvp["excluded_admin_areas_filter"] == []
            assert "Pending" == resp_data["payment_verification_summary"]["status"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_ACTIVATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_activate(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(self.url_activate, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            assert resp_data["payment_verification_plans"][0]["status"] == "Active"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_FINISH], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_finish(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.pvp.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.pvp.save()
        response = self.client.post(self.url_finish, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            assert resp_data["payment_verification_plans"][0]["status"] == "Finished"

    def test_pvp_finish_validation_error(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PAYMENT_VERIFICATION_FINISH], self.afghanistan, self.program_active
        )
        response = self.client.post(self.url_finish, {"version": self.pvp.version}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You can finish only ACTIVE verification" in response.json()

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_DISCARD], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_discard(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.pvp.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.pvp.save()
        response = self.client.post(self.url_discard, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            assert resp_data["payment_verification_plans"][0]["status"] == "Pending"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_INVALID], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_invalid(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.pvp.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.pvp.verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
        self.pvp.xlsx_file_imported = True
        self.pvp.save()
        response = self.client.post(self.url_invalid, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            assert resp_data["payment_verification_plans"][0]["status"] == "Invalid"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_DELETE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_delete(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.post(self.url_delete, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 0 == len(resp_data["payment_verification_plans"])

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_EXPORT], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pvp_export_xlsx(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.pvp.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.pvp.verification_channel = PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX
        self.pvp.save()
        response = self.client.post(self.url_export_xlsx, {"version": self.pvp.version}, format="json")
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert 1 == len(resp_data["payment_verification_plans"])
            assert resp_data["payment_verification_plans"][0]["xlsx_file_exporting"] is True

    # @pytest.mark.parametrize(
    #     "permissions, expected_status",
    #     [
    #         ([Permissions.PAYMENT_VERIFICATION_IMPORT], status.HTTP_200_OK),
    #         ([], status.HTTP_403_FORBIDDEN),
    #     ],
    # )
    # def test_pvp_import_xlsx(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
    #     create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
    #     file = generate_valid_xlsx_file(worksheet_title_list=["Payment Verifications", "Meta"])
    #     response = self.client.post(self.url_import_xlsx, {"version": self.pvp.version, "file": file}, format="multipart")
    #     assert response.status_code == expected_status
    #     if expected_status == status.HTTP_200_OK:
    #         assert response.status_code == status.HTTP_200_OK
    #         resp_data = response.json()
    #         assert "id" in resp_data
    #         assert 1 == len(resp_data["payment_verification_plans"])
    #         assert resp_data["payment_verification_plans"][0]["xlsx_file_imported"] is True
