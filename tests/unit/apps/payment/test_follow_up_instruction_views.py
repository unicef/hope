from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PartnerFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import FollowUpInstruction

pytestmark = pytest.mark.django_db


def test_follow_up_instruction_detail_is_scoped_to_program(
    api_client: Callable,
    create_user_role_with_permissions: Any,
) -> None:
    business_area = BusinessAreaFactory(slug="afghanistan")
    partner = PartnerFactory(name="Test Partner")
    user = UserFactory(partner=partner)
    client = api_client(user)
    program_with_access = ProgramFactory(business_area=business_area)
    other_program = ProgramFactory(business_area=business_area)
    instruction = FollowUpInstruction.objects.create(
        business_area=business_area,
        program=other_program,
        created_by=user,
    )

    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        business_area,
        program_with_access,
    )

    url = reverse(
        "api:payments:follow-up-instructions-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_code": program_with_access.code,
            "pk": instruction.pk,
        },
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_follow_up_instruction_rejects_duplicate_group_ids(
    api_client: Callable,
    create_user_role_with_permissions: Any,
) -> None:
    business_area = BusinessAreaFactory(slug="afghanistan")
    partner = PartnerFactory(name="TestPartnerFI")
    user = UserFactory(partner=partner)
    program = ProgramFactory(business_area=business_area)
    create_user_role_with_permissions(user, [Permissions.PM_CREATE], business_area, program)
    client = api_client(user)
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanGroupFactory(cycle=cycle)
    duplicate_id = str(group.pk)
    url = reverse(
        "api:payments:follow-up-instructions-list",
        kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
    )

    response = client.post(
        url,
        {
            "dispersion_start_date": "2025-01-01",
            "dispersion_end_date": "2025-03-31",
            "payment_plan_group_ids": [duplicate_id, duplicate_id],
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Duplicate Payment Plan Group IDs are not allowed." in str(response.json()["payment_plan_group_ids"])
