from typing import Any

from django.test import TestCase
import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.contrib.api.serializers.vision import (
    FundsCommitmentItemSerializer,
    FundsCommitmentSerializer,
    PaymentPlanCallbackResponseSerializer,
)
from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem

pytestmark = pytest.mark.django_db


class TestFundsCommitmentItemSerializer(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
            kobo_token="XXX",
            active=True,
        )

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


def test_funds_commitment_serializer() -> None:
    fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_group=fcg,
        rec_serial_number=12345,
        funds_commitment_item="001",
        currency_code="USD",
        commitment_amount_local=1000.00,
        commitment_amount_usd=1000.00,
    )
    data: dict[str, Any] = {
        "funds_commitment_number": "FC-001",
        "funds_commitment_items": [fci],
    }
    serializer = FundsCommitmentSerializer(data)
    assert serializer.data["funds_commitment_number"] == "FC-001"
    items = serializer.data["funds_commitment_items"]
    assert len(items) == 1
    assert items[0]["rec_serial_number"] == 12345
    assert items[0]["funds_commitment_item"] == "001"
    assert items[0]["currency_code"] == "USD"
    assert items[0]["commitment_amount_local"] == "1000.00"
    assert items[0]["commitment_amount_usd"] == "1000.00"


class TestPaymentPlanCallbackResponseSerializer:
    def test_to_representation(self) -> None:
        serializer = PaymentPlanCallbackResponseSerializer(
            data={
                "business_area": "0060",
                "vendor_number": "V100004",
                "payplan_sno": "PP001",
                "payplan_desc": "Test Plan",
                "currency": "USD",
                "auth_amt": "10000.00",
                "auth_amt_usd": "10000.00",
                "status": "DRAFT",
                "head_vendor": "Head Vendor",
                "creation_date": "20250101",
            }
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.to_representation(serializer.validated_data)
        assert result["businessArea"] == "0060"
        assert result["vendorNumber"] == "V100004"
        assert result["payplanSno"] == "PP001"
        assert result["payplanDesc"] == "Test Plan"
        assert result["currency"] == "USD"
        assert result["authAmt"] == "10000.00"
        assert result["authAmtUsd"] == "10000.00"
        assert result["status"] == "DRAFT"
        assert result["headVendor"] == "Head Vendor"
        assert result["creationDate"] == "20250101"

    def test_to_representation_with_extra_data(self) -> None:
        data = {
            "business_area": "0060",
            "vendor_number": "V100004",
            "payplan_sno": "PP002",
            "payplan_desc": "Extra Plan",
            "currency": "EUR",
            "auth_amt": "5000.00",
            "auth_amt_usd": "5500.00",
            "status": "NEW",
            "head_vendor": "Vendor Two",
            "creation_date": "20250615",
        }
        serializer = PaymentPlanCallbackResponseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = serializer.to_representation(serializer.validated_data)
        assert result["businessArea"] == "0060"
        assert result["currency"] == "EUR"
        assert result["creationDate"] == "20250615"
