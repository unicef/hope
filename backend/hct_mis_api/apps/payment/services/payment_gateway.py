import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from django.db.models import QuerySet
from django.utils.timezone import now

from requests import Response, session
from requests.adapters import HTTPAdapter
from rest_framework import serializers
from urllib3 import Retry

from hct_mis_api.apps.payment.models import (
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
)

logger = logging.getLogger(__name__)


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args: List, **kwargs: Dict) -> Dict:
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields


class PaymentInstructionStatus(Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    READY = "READY"
    CLOSED = "CLOSED"
    ABORTED = "ABORTED"
    PROCESSED = "PROCESSED"


class PaymentGatewayPaymentInstructionSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    unicef_id = serializers.CharField(source="payment_plan.unicef_id")
    fsp = serializers.CharField(source="financial_service_provider.payment_gateway_id")
    payload = serializers.SerializerMethodField()

    def get_payload(self, obj: DeliveryMechanismPerPaymentPlan) -> Dict:
        return {
            "destination_currency": obj.payment_plan.currency,
        }

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = [
            "remote_id",
            "unicef_id",
            "fsp",
            "payload",
        ]


class PaymentGatewayPaymentSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    record_code = serializers.SerializerMethodField()
    payload = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    def get_record_code(self, obj: Payment) -> Dict:
        return obj.unicef_id

    def get_extra_data(self, obj: Payment) -> Dict:
        return {}

    def get_payload(self, obj: Payment) -> Dict:
        """
        amount: int  # 120000
        phone_no: str  # "78933211"
        last_name: str  # "Arabic"
        first_name: str  # "Angelina"
        destination_currency: str  # "USD"
        """
        return {
            "amount": int(obj.entitlement_quantity * 100),
            "phone_no": str(obj.collector.phone_no),
            "last_name": obj.collector.family_name,
            "first_name": obj.collector.given_name,
            "destination_currency": obj.currency,
        }

    class Meta:
        model = Payment
        fields = [
            "remote_id",
            "record_code",
            "payload",
            "extra_data",
        ]


@dataclass
class PaymentRecordData:
    id: int
    remote_id: str
    created: str
    modified: str
    record_code: str
    parent: str
    status: str
    hope_status: str
    success: bool
    # delivered_amount: int # TODO wait for implementation on PG side


@dataclass
class PaymentInstructionData:
    remote_id: str
    unicef_id: str
    status: str  # "DRAFT"
    fsp: str
    system: int
    payload: dict
    id: Optional[int] = None


@dataclass
class FspData:
    id: int
    remote_id: str
    name: str
    vision_vendor_number: str
    configuration: dict
    payload: dict


@dataclass
class AddRecordsResponseData:
    remote_id: str  # payment instruction id
    records: dict  # {"record_code": "remote_id"}


class PaymentGatewayAPI:
    class PaymentGatewayAPIException(Exception):
        pass

    class Endpoints:
        CREATE_PAYMENT_INSTRUCTION = "payment_instructions/"
        ABORT_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/abort/"
        CLOSE_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/close/"
        OPEN_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/open/"
        PROCESS_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/process/"
        READY_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/ready/"
        PAYMENT_INSTRUCTION_ADD_RECORDS = "payment_instructions/{remote_id}/add_records/"
        GET_FSPS = "fsp/"
        GET_PAYMENT_RECORDS = "payment_records/"

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("PAYMENT_GATEWAY_API_KEY")
        self.api_url = api_url or os.getenv("PAYMENT_GATEWAY_API_URL")

        if self.api_key is None:
            raise ValueError("Missing Payment Gateway API Key")

        self._client = session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Authorization": f"Token {self.api_key}"})

    def validate_response(self, response: Response) -> Dict:
        if not response.ok:
            raise self.PaymentGatewayAPIException(f"Invalid response: {response}, {response.content!r}, {response.url}")

        return response.json()

    def _post(self, endpoint: str, data: Optional[Union[Dict, List]] = None) -> Dict:
        response = self._client.post(self.api_url + endpoint, json=data)
        response_data = self.validate_response(response)
        return response_data

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        response = self._client.get(self.api_url + endpoint, params=params)
        response_data = self.validate_response(response)
        return response_data

    def get_fsps(self) -> List[FspData]:
        response_data = self._get(self.Endpoints.GET_FSPS)
        return [FspData(**fsp_data) for fsp_data in response_data]

    def create_payment_instruction(self, data: dict) -> PaymentInstructionData:
        response_data = self._post(self.Endpoints.CREATE_PAYMENT_INSTRUCTION, data)
        return PaymentInstructionData(**response_data)

    def change_payment_instruction_status(self, status: PaymentInstructionStatus, remote_id: str) -> str:
        if status.value not in [s.value for s in PaymentInstructionStatus]:
            raise self.PaymentGatewayAPIException(f"Can't set invalid Payment Instruction status: {status}")

        action_endpoint_map = {
            PaymentInstructionStatus.ABORTED: self.Endpoints.ABORT_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.CLOSED: self.Endpoints.CLOSE_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.OPEN: self.Endpoints.OPEN_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.PROCESSED: self.Endpoints.PROCESS_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.READY: self.Endpoints.READY_PAYMENT_INSTRUCTION_STATUS,
        }
        response_data = self._post(action_endpoint_map[status].format(remote_id=remote_id))

        return response_data["status"]

    def add_records_to_payment_instruction(
        self, payment_records: QuerySet[Payment], remote_id: str
    ) -> AddRecordsResponseData:
        data = PaymentGatewayPaymentSerializer(payment_records, many=True).data
        response_data = self._post(self.Endpoints.PAYMENT_INSTRUCTION_ADD_RECORDS.format(remote_id=remote_id), data)
        return AddRecordsResponseData(**response_data)

    def get_records_for_payment_instruction(self, payment_instruction_remote_id: str) -> List[PaymentRecordData]:
        response_data = self._get(
            f"{self.Endpoints.GET_PAYMENT_RECORDS}?parent__remote_id={payment_instruction_remote_id}"
        )
        return [PaymentRecordData(**record_data) for record_data in response_data]


class PaymentGatewayService:
    def __init__(self) -> None:
        self.api = PaymentGatewayAPI()

    def create_payment_instructions(self, payment_plan: PaymentPlan) -> None:
        # for each sfp, create payment instruction
        for delivery_mechanism in payment_plan.delivery_mechanisms.all():
            if delivery_mechanism.financial_service_provider.is_payment_gateway:
                data = PaymentGatewayPaymentInstructionSerializer(
                    delivery_mechanism,
                ).data
                response = self.api.create_payment_instruction(data)
                assert response.remote_id == str(
                    delivery_mechanism.id
                ), f"{response}, delivery_mechanism_id: {delivery_mechanism.id}"
                status = self.api.change_payment_instruction_status(
                    status=PaymentInstructionStatus.OPEN, remote_id=response.remote_id
                )
                assert status == PaymentInstructionStatus.OPEN.value, status

    def change_payment_instruction_status(
        self, new_status: PaymentInstructionStatus, delivery_mechanism: DeliveryMechanismPerPaymentPlan
    ) -> str:
        if delivery_mechanism.financial_service_provider.is_payment_gateway:
            response_status = self.api.change_payment_instruction_status(new_status, delivery_mechanism.id)
            assert new_status.value == response_status, f"{new_status} != {response_status}"
            return response_status

    def add_records_to_payment_instructions(self, payment_plan: PaymentPlan) -> None:
        for delivery_mechanism in payment_plan.delivery_mechanisms.all():
            if delivery_mechanism.financial_service_provider.is_payment_gateway:
                payments = payment_plan.eligible_payments.filter(
                    financial_service_provider=delivery_mechanism.financial_service_provider
                ).order_by("unicef_id")
                response = self.api.add_records_to_payment_instruction(payments, delivery_mechanism.id)
                assert response.remote_id == str(
                    delivery_mechanism.id
                ), f"{response}, delivery_mechanism_id: {delivery_mechanism.id}"
                assert len(response.records) == payments.count(), f"{len(response.records)} != {payments.count()}"

                status = self.change_payment_instruction_status(PaymentInstructionStatus.CLOSED, delivery_mechanism)
                assert status == PaymentInstructionStatus.CLOSED.value, status
                status = self.change_payment_instruction_status(PaymentInstructionStatus.READY, delivery_mechanism)
                assert status == PaymentInstructionStatus.READY.value, status
                delivery_mechanism.sent_to_payment_gateway = True
                delivery_mechanism.save(update_fields=["sent_to_payment_gateway"])

    def sync_fsps(self) -> None:
        fsps = self.api.get_fsps()
        for fsp in fsps:
            FinancialServiceProvider.objects.update_or_create(
                payment_gateway_id=fsp.id,
                defaults={
                    "vision_vendor_number": fsp.vision_vendor_number,
                    "name": fsp.name,
                    "communication_channel": FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                    "data_transfer_configuration": fsp.configuration,
                    "delivery_mechanisms": [Payment.DELIVERY_TYPE_TRANSFER_TO_ACCOUNT],
                },
            )

    def sync_records(self) -> None:
        payment_plans = PaymentPlan.objects.filter(
            status=PaymentPlan.Status.ACCEPTED,
            delivery_mechanisms__financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            delivery_mechanisms__financial_service_provider__payment_gateway_id__isnull=False,
            delivery_mechanisms__sent_to_payment_gateway=True,
        ).distinct()

        for payment_plan in payment_plans:
            if not payment_plan.is_reconciled:
                for delivery_mechanism in payment_plan.delivery_mechanisms.filter(
                    financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                    financial_service_provider__payment_gateway_id__isnull=False,
                    sent_to_payment_gateway=True,
                ):
                    pending_payments = payment_plan.eligible_payments.filter(
                        financial_service_provider=delivery_mechanism.financial_service_provider,
                        status=Payment.STATUS_PENDING,
                    ).order_by("unicef_id")
                    pg_payment_records = self.api.get_records_for_payment_instruction(delivery_mechanism.id)

                    for payment in pending_payments:
                        try:
                            matching_pg_payment = next(p for p in pg_payment_records if p.remote_id == str(payment.id))
                        except StopIteration:
                            logger.error(
                                f"Payment {payment.id} for Payment Instruction {delivery_mechanism.id} not found in Payment Gateway"
                            )
                            continue

                        payment.status = matching_pg_payment.hope_status
                        payment.status_date = now()
                        payment.save(update_fields=["status", "status_date"])

                        # TODO wait for implementation on PG side
                        # payment.delivered_amount = matching_pg_payment.delivered_amount / 100
                        # payment.save(update_fields=["status", "status_date", "delivered_amount"])
