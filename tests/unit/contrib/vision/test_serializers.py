from typing import Any

import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.contrib.api.serializers.vision import (
    FundsCommitmentItemSerializer,
    FundsCommitmentSerializer,
    PaymentPlanCallbackAckSerializer,
    PaymentPlanCallbackRequestSerializer,
)
from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> None:
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


@pytest.fixture
def funds_commitment_item(business_area) -> FundsCommitmentItem:
    fcg = FundsCommitmentGroup.objects.create(funds_commitment_number="FC-001")
    return FundsCommitmentItem.objects.create(
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


def test_funds_commitment_item_serializer(funds_commitment_item) -> None:
    serializer = FundsCommitmentItemSerializer(funds_commitment_item)
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


def test_payment_plan_callback_request_serializer_to_internal_value() -> None:
    serializer = PaymentPlanCallbackRequestSerializer(
        data={
            "messageId": "msg-001",
            "payplanSno": "PP001",
            "vision_payplanSno": "00000062",
            "status": "SUCCESS",
            "fc_num": "FC123",
        }
    )
    serializer.is_valid(raise_exception=True)
    assert serializer.validated_data == {
        "message_id": "msg-001",
        "payplan_sno": "PP001",
        "vision_payplan_sno": "00000062",
        "status": "SUCCESS",
        "fc_num": "FC123",
    }
    assert serializer.validated_message_id == "msg-001"


def test_payment_plan_callback_request_serializer_external_payload() -> None:
    serializer = PaymentPlanCallbackRequestSerializer(
        data={
            "messageId": "msg-001",
            "payplanSno": "PP001",
            "vision_payplanSno": "00000062",
            "status": "SUCCESS",
            "fc_num": "FC123",
        }
    )
    serializer.is_valid(raise_exception=True)
    assert serializer.external_payload == {
        "messageId": "msg-001",
        "payplanSno": "PP001",
        "vision_payplanSno": "00000062",
        "status": "SUCCESS",
        "fc_num": "FC123",
    }


def test_payment_plan_callback_request_serializer_ack_payload_uses_initial_data_before_validation() -> None:
    serializer = PaymentPlanCallbackRequestSerializer(data={"messageId": "msg-001", "payplanSno": "PP001"})
    assert serializer.ack_payload("KO") == {
        "status": "KO",
        "message_id": "msg-001",
        "payplan_sno": "PP001",
    }


def test_payment_plan_callback_ack_serializer_to_representation() -> None:
    serializer = PaymentPlanCallbackAckSerializer(
        {
            "status": "OK",
            "message_id": "msg-001",
            "payplan_sno": "PP001",
        }
    )
    assert serializer.data == {
        "status": "OK",
        "messageId": "msg-001",
        "payplanSno": "PP001",
    }
