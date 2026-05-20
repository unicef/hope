from django.test import TestCase
import pytest

from extras.test_utils.old_factories.core import create_afghanistan
from hope.contrib.api.serializers.vision import FundsCommitmentItemSerializer
from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem

pytestmark = pytest.mark.django_db


class TestFundsCommitmentItemSerializer(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

    def test_serialize(self) -> None:
        fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
        fci = FundsCommitmentItem.objects.create(
            funds_commitment_group=fcg,
            rec_serial_number=12345,
            funds_commitment_item="001",
            wbs_element="WBS-001",
            grant_number="GR-001",
            currency_code="USD",
            commitment_amount_local=1000.00,
            commitment_amount_usd=1000.00,
            total_open_amount_local=500.00,
            total_open_amount_usd=500.00,
            sponsor="SP-001",
            sponsor_name="Sponsor One",
        )
        serializer = FundsCommitmentItemSerializer(fci)
        assert serializer.data == {
            "wbs_element": "WBS-001",
            "grant_number": "GR-001",
            "currency_code": "USD",
            "commitment_amount_local": "1000.00",
            "commitment_amount_usd": "1000.00",
            "total_open_amount_local": "500.00",
            "total_open_amount_usd": "500.00",
            "rec_serial_number": 12345,
            "funds_commitment_item": "001",
            "sponsor": "SP-001",
            "sponsor_name": "Sponsor One",
        }
