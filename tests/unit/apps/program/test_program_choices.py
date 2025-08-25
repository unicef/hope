from typing import Any

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.models.core import DataCollectingType, PeriodicFieldData
from hope.apps.core.utils import to_choice_object
from hope.models.program import Program, ProgramCycle

pytestmark = pytest.mark.django_db


class TestProgramChoicesSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.choices_url = "api:programs:programs-choices"
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.ukraine = create_ukraine()

        # DCT1: Active, not deprecated, not limited to any business area
        self.dct_1 = DataCollectingType.objects.create(
            label="DCT 1",
            code="dct_1",
            description="Description for DCT 1",
            type=DataCollectingType.Type.STANDARD,
            active=True,
            deprecated=False,
        )

        # DCT2: Active, not deprecated, limited to afghanistan
        self.dct_2 = DataCollectingType.objects.create(
            label="DCT 2",
            code="dct_2",
            description="Description for DCT 2",
            type=DataCollectingType.Type.STANDARD,
            active=True,
            deprecated=False,
        )
        self.dct_2.limit_to.add(self.afghanistan)

        # DCT3: Active, not deprecated, limited to ukraine
        self.dct_3 = DataCollectingType.objects.create(
            label="DCT 3",
            code="dct_3",
            description="Description for DCT 3",
            type=DataCollectingType.Type.STANDARD,
            active=True,
            deprecated=False,
        )
        self.dct_3.limit_to.add(self.ukraine)

        # DCT4: Inactive
        self.dct_4 = DataCollectingType.objects.create(
            label="DCT 4 (Inactive)",
            code="dct_4",
            description="Description for DCT 4",
            type=DataCollectingType.Type.STANDARD,
            active=False,
            deprecated=False,
        )

        # DCT5: Deprecated
        self.dct_5 = DataCollectingType.objects.create(
            label="DCT 5 (Deprecated)",
            code="dct_5",
            description="Description for DCT 5",
            type=DataCollectingType.Type.STANDARD,
            active=True,
            deprecated=True,
        )

        # DCT6: code 'unknown'
        self.dct_6 = DataCollectingType.objects.create(
            label="DCT 6 (Unknown Code)",
            code="unknown",
            description="Description for DCT 6",
            type=DataCollectingType.Type.STANDARD,
            active=True,
            deprecated=False,
        )

    def test_get_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(reverse(self.choices_url, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "status_choices": to_choice_object(Program.STATUS_CHOICE),
            "frequency_of_payments_choices": to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE),
            "sector_choices": to_choice_object(Program.SECTOR_CHOICE),
            "scope_choices": to_choice_object(Program.SCOPE_CHOICE),
            "data_collecting_type_choices": [
                {
                    "value": self.dct_1.code,
                    "name": self.dct_1.label,
                    "description": self.dct_1.description,
                    "type": self.dct_1.type,
                },
                {
                    "value": self.dct_2.code,
                    "name": self.dct_2.label,
                    "description": self.dct_2.description,
                    "type": self.dct_2.type,
                },
            ],
            "partner_access_choices": to_choice_object(Program.PARTNER_ACCESS_CHOICE),
            "pdu_subtype_choices": to_choice_object(PeriodicFieldData.TYPE_CHOICES),
            "program_cycle_status_choices": to_choice_object(ProgramCycle.STATUS_CHOICE),
        }
