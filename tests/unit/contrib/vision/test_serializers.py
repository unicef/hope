from typing import Any

import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.contrib.api.serializers.vision import (
    FundsCommitmentItemSerializer,
    FundsCommitmentSerializer,
    PaymentPlanCallbackAckSerializer,
    PaymentPlanCallbackRequestSerializer,
)
from hope.contrib.vision.fixtures import FundsCommitmentFactory
from hope.contrib.vision.models import FundsCommitmentHeader, FundsCommitmentItem

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
        active=True,
    )


@pytest.fixture
def funds_commitment_item(business_area) -> FundsCommitmentItem:
    header = FundsCommitmentHeader.objects.create(funds_commitment_number="FC-001")
    return FundsCommitmentItem.objects.create(
        funds_commitment_header=header,
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
    header = FundsCommitmentHeader.objects.create(funds_commitment_number="FC-001")
    fci = FundsCommitmentItem.objects.create(
        funds_commitment_header=header,
        rec_serial_number=12345,
        funds_commitment_item="001",
        currency_code="USD",
        commitment_amount_local=1000.00,
        commitment_amount_usd=1000.00,
    )
    data: dict[str, Any] = {
        "id": header.pk,
        "funds_commitment_number": "FC-001",
        "funds_commitment_items": [fci],
    }
    serializer = FundsCommitmentSerializer(data)
    assert serializer.data["id"] == header.pk
    assert serializer.data["funds_commitment_number"] == "FC-001"
    items = serializer.data["funds_commitment_items"]
    assert len(items) == 1
    assert items[0]["rec_serial_number"] == 12345
    assert items[0]["funds_commitment_item"] == "001"
    assert items[0]["currency_code"] == "USD"
    assert items[0]["commitment_amount_local"] == "1000.00"
    assert items[0]["commitment_amount_usd"] == "1000.00"


@pytest.fixture
def funds_commitment_header_data(business_area) -> dict[str, Any]:
    FundsCommitmentFactory(
        rec_serial_number=200,
        funds_commitment_number="FC-002",
        vendor_id="VENDOR-2",
        posting_date="2026-09-02",
        document_reference="REFERENCE-2",
        fc_status="C",
        funds_commitment_item="002",
        currency_code="EUR",
        commitment_amount_local="250.75",
        commitment_amount_usd="300.50",
    )
    FundsCommitmentFactory(
        rec_serial_number=100,
        funds_commitment_number="FC-002",
        vendor_id="VENDOR-1",
        posting_date="2026-09-01",
        document_reference="REFERENCE-1",
        fc_status="O",
        funds_commitment_item="001",
        currency_code="USD",
        commitment_amount_local="100.25",
        commitment_amount_usd="100.50",
    )
    header = FundsCommitmentHeader.objects.with_derived_fields().get(funds_commitment_number="FC-002")
    return {
        "id": header.pk,
        "rec_serial_number": header.rec_serial_number,
        "funds_commitment_number": header.funds_commitment_number,
        "vendor_id": header.vendor_id,
        "posting_date": header.posting_date,
        "document_reference": header.document_reference,
        "fc_status": header.fc_status,
        "total_amount_usd": header.total_amount_usd,
        "total_amount_local": header.total_amount_local,
        "currency": header.currency,
        "funds_commitment_items": list(header.funds_commitment_items.all()),
    }


def test_funds_commitment_serializer_exposes_derived_header_fields(funds_commitment_header_data) -> None:
    serializer = FundsCommitmentSerializer(funds_commitment_header_data)

    assert serializer.data["rec_serial_number"] == 100
    assert serializer.data["funds_commitment_number"] == "FC-002"
    assert serializer.data["vendor_id"] == "VENDOR-1"
    assert serializer.data["posting_date"] == "2026-09-01"
    assert serializer.data["document_reference"] == "REFERENCE-1"
    assert serializer.data["fc_status"] == "O"
    assert serializer.data["total_amount_usd"] == "401.00"
    assert serializer.data["total_amount_local"] == "351.00"
    assert serializer.data["currency"] == "USD"


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


def test_payment_plan_callback_request_serializer_accepts_payment_plan_created_acknowledgement() -> None:
    serializer = PaymentPlanCallbackRequestSerializer(
        data={
            "messageId": "msg-created",
            "payplanSno": "PP-0060-24-0000002a",
            "vision_payplanSno": "00000110",
            "status": "",
            "fc_num": "",
        }
    )

    serializer.is_valid(raise_exception=True)

    assert serializer.validated_data == {
        "message_id": "msg-created",
        "payplan_sno": "PP-0060-24-0000002a",
        "vision_payplan_sno": "00000110",
        "status": "",
        "fc_num": "",
    }


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


def test_payment_plan_callback_request_serializer_ack_payload_includes_message() -> None:
    serializer = PaymentPlanCallbackRequestSerializer(data={"messageId": "msg-001", "payplanSno": "PP001"})
    assert serializer.ack_payload("KO", message="FC not found") == {
        "status": "KO",
        "message_id": "msg-001",
        "payplan_sno": "PP001",
        "message": "FC not found",
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


def test_payment_plan_callback_ack_serializer_to_representation_includes_message() -> None:
    serializer = PaymentPlanCallbackAckSerializer(
        {
            "status": "KO",
            "message_id": "msg-001",
            "payplan_sno": "PP001",
            "message": "FC not found",
        }
    )
    assert serializer.data == {
        "status": "KO",
        "messageId": "msg-001",
        "payplanSno": "PP001",
        "message": "FC not found",
    }
