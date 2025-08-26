import datetime
from typing import Any, Callable

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.payment.models import PaymentPlan
from hope.models.program import Program, ProgramCycle

pytestmark = pytest.mark.django_db


class TestProgramFinish:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="Test Program For Finish",
            start_date=datetime.date(2031, 1, 1),
            end_date=datetime.date(2033, 12, 31),
        )

        self.finish_url = reverse(
            "api:programs:programs-finish",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program.slug,
            },
        )

        # There cannot be any active cycles for the program to finish
        for cycle in self.program.cycles.filter(status=ProgramCycle.ACTIVE):
            cycle.status = ProgramCycle.FINISHED
            cycle.save()

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_FINISH], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_finish_program_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Callable,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)

        assert self.program.status == Program.ACTIVE
        response = self.client.post(self.finish_url)
        assert response.status_code == expected_status

        self.program.refresh_from_db()
        if expected_status == status.HTTP_200_OK:
            assert self.program.status == Program.FINISHED
            assert response.json() == {"message": "Program Finished."}
        else:
            assert self.program.status == Program.ACTIVE  # Status should not change if permission denied

    def test_finish_program_already_finished(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        self.program.status = Program.FINISHED
        self.program.save()

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only active Program can be finished." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.FINISHED

    def test_finish_program_invalid_status_draft(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        self.program.status = Program.DRAFT
        self.program.save()

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only active Program can be finished." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.DRAFT

    def test_finish_program_without_end_date(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        self.program.end_date = None
        self.program.save()

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot finish programme without end date." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.ACTIVE

    def test_finish_program_with_active_cycles(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        ProgramCycleFactory(program=self.program, status=ProgramCycle.ACTIVE)

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot finish Program with active cycles." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.ACTIVE

    def test_finish_program_with_unreconciled_payment_plans(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.IN_REVIEW,
        )

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "All Payment Plans and Follow-Up Payment Plans have to be Reconciled." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.ACTIVE

    def test_finish_program_with_reconciled_payment_plans(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_FINISH],
            self.afghanistan,
            whole_business_area_access=True,
        )

        PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.ACCEPTED,
        )
        PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.FINISHED,
        )
        PaymentPlanFactory(
            program_cycle=self.program.cycles.first(),
            status=PaymentPlan.Status.TP_LOCKED,
        )

        response = self.client.post(self.finish_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Program Finished."}

        self.program.refresh_from_db()
        assert self.program.status == Program.FINISHED
