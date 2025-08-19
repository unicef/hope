import pytest
from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan

from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem

pytestmark = pytest.mark.django_db


class TestFundsCommitmentDBTrigger(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

    def test_trigger_creates_rows(self) -> None:
        assert FundsCommitmentGroup.objects.count() == 0
        assert FundsCommitmentItem.objects.count() == 0

        FundsCommitmentFactory(funds_commitment_number="123")

        assert FundsCommitmentGroup.objects.count() == 1
        assert FundsCommitmentItem.objects.count() == 1

        FundsCommitmentFactory(funds_commitment_number="123")

        assert FundsCommitmentGroup.objects.count() == 1
        assert FundsCommitmentItem.objects.count() == 2

        FundsCommitmentFactory(funds_commitment_number="345")

        assert FundsCommitmentGroup.objects.count() == 2
        assert FundsCommitmentItem.objects.count() == 3

        fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="123")
        assert fcg.funds_commitment_items.count() == 2

        fcg = FundsCommitmentGroup.objects.get(funds_commitment_number="345")
        assert fcg.funds_commitment_items.count() == 1
