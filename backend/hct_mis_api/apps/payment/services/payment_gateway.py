import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from django.db.models import Q, QuerySet
from django.utils.timezone import now

from _decimal import Decimal
from requests import Response, session
from requests.adapters import HTTPAdapter
from rest_framework import serializers
from urllib3 import Retry

from hct_mis_api.apps.payment.models import (
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.utils import get_quantity_in_usd

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


class PaymentInstructionFromDeliveryMechanismPerPaymentPlanSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    unicef_id = serializers.CharField(source="payment_plan.unicef_id")
    fsp = serializers.SerializerMethodField()
    payload = serializers.SerializerMethodField()
    extra = serializers.SerializerMethodField()

    def get_fsp(self, obj: Any) -> str:
        return obj.financial_service_provider.payment_gateway_id

    def get_extra(self, obj: Any) -> Dict:
        return {
            "user": self.context["user_email"],
            "business_area": obj.payment_plan.business_area.code,
        }

    def get_payload(self, obj: Any) -> Dict:
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
            "extra",
        ]


class PaymentInstructionFromSplitSerializer(PaymentInstructionFromDeliveryMechanismPerPaymentPlanSerializer):
    class Meta:
        model = PaymentPlanSplit
        fields = [
            "remote_id",
            "unicef_id",
            "fsp",
            "payload",
            "extra",
        ]


class PaymentSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    record_code = serializers.CharField(source="unicef_id")
    payload = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

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
    extra_data: dict


@dataclass
class PaymentInstructionData:
    remote_id: str
    unicef_id: str
    status: str  # "DRAFT"
    fsp: str
    system: int
    payload: dict
    extra: dict
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

        if not self.api_key or not self.api_url:
            raise ValueError("Missing Payment Gateway API Key/URL")

        self._client = session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Authorization": f"Token {self.api_key}"})

    def validate_response(self, response: Response) -> Dict:
        if not response.ok:
            raise self.PaymentGatewayAPIException(f"Invalid response: {response}, {response.content!r}, {response.url}")

        return response.json()

    def _post(self, endpoint: str, data: Optional[Union[Dict, List]] = None) -> Dict:
        response = self._client.post(f"{self.api_url}{endpoint}", json=data)
        response_data = self.validate_response(response)
        return response_data

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        response = self._client.get(f"{self.api_url}{endpoint}", params=params)
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
        serializer = PaymentSerializer(payment_records, many=True)
        response_data = self._post(
            self.Endpoints.PAYMENT_INSTRUCTION_ADD_RECORDS.format(remote_id=remote_id), serializer.data
        )
        return AddRecordsResponseData(**response_data)

    def get_records_for_payment_instruction(self, payment_instruction_remote_id: str) -> List[PaymentRecordData]:
        response_data = self._get(
            f"{self.Endpoints.GET_PAYMENT_RECORDS}?parent__remote_id={payment_instruction_remote_id}"
        )
        return [PaymentRecordData(**record_data) for record_data in response_data]


class PaymentGatewayService:
    def __init__(self) -> None:
        self.api = PaymentGatewayAPI()

    def create_payment_instructions(self, payment_plan: PaymentPlan, user_email: str) -> None:
        def _create_payment_instruction(
            _serializer: Callable,
            _object: Union[PaymentPlanSplit, DeliveryMechanismPerPaymentPlan],
        ) -> None:
            data = _serializer(_object, context={"user_email": user_email}).data
            response = self.api.create_payment_instruction(data)
            assert response.remote_id == str(_object.id), f"{response}, _object_id: {_object.id}"
            status = self.api.change_payment_instruction_status(
                status=PaymentInstructionStatus.OPEN, remote_id=response.remote_id
            )
            assert status == PaymentInstructionStatus.OPEN.value, status

        if payment_plan.splits.exists():
            for split in payment_plan.splits.all():
                if split.financial_service_provider.is_payment_gateway:
                    _create_payment_instruction(PaymentInstructionFromSplitSerializer, split)

        else:
            # for each sfp, create payment instruction
            for delivery_mechanism in payment_plan.delivery_mechanisms.all():
                if delivery_mechanism.financial_service_provider.is_payment_gateway:
                    _create_payment_instruction(
                        PaymentInstructionFromDeliveryMechanismPerPaymentPlanSerializer, delivery_mechanism
                    )

    def change_payment_instruction_status(
        self, new_status: PaymentInstructionStatus, obj: Union[DeliveryMechanismPerPaymentPlan, PaymentPlanSplit]
    ) -> Optional[str]:
        if obj.financial_service_provider.is_payment_gateway:
            response_status = self.api.change_payment_instruction_status(new_status, obj.id)
            assert new_status.value == response_status, f"{new_status} != {response_status}"
            return response_status
        return None

    def add_records_to_payment_instructions(self, payment_plan: PaymentPlan) -> None:
        def handle_response(
            resp: AddRecordsResponseData,
            obj: Union[DeliveryMechanismPerPaymentPlan, PaymentPlanSplit],
            payments_count: int,
        ) -> None:
            assert resp.remote_id == str(obj.id), f"{resp}, {obj} {obj.id}"
            assert len(resp.records) == payments_count, f"{len(resp.records)} != {payments_count}"

            status = self.change_payment_instruction_status(PaymentInstructionStatus.CLOSED, obj)
            assert status == PaymentInstructionStatus.CLOSED.value, status
            status = self.change_payment_instruction_status(PaymentInstructionStatus.READY, obj)
            assert status == PaymentInstructionStatus.READY.value, status
            obj.sent_to_payment_gateway = True
            obj.save(update_fields=["sent_to_payment_gateway"])

        if payment_plan.splits.exists():
            for split in payment_plan.splits.all():
                if split.financial_service_provider.is_payment_gateway:
                    payments = split.payments.order_by("unicef_id")
                    response = self.api.add_records_to_payment_instruction(payments, split.id)
                    handle_response(response, split, payments.count())

        else:
            for delivery_mechanism in payment_plan.delivery_mechanisms.all():
                if delivery_mechanism.financial_service_provider.is_payment_gateway:
                    payments = payment_plan.eligible_payments.filter(
                        financial_service_provider=delivery_mechanism.financial_service_provider
                    ).order_by("unicef_id")
                    response = self.api.add_records_to_payment_instruction(payments, delivery_mechanism.id)
                    handle_response(response, delivery_mechanism, payments.count())

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
        def update_payment(
            _payment: Payment,
            _pg_payment_records: List[PaymentRecordData],
            _container: Union[DeliveryMechanismPerPaymentPlan, PaymentPlanSplit],
            _payment_plan: PaymentPlan,
            _exchange_rate: Decimal,
        ) -> None:
            try:
                matching_pg_payment = next(p for p in _pg_payment_records if p.remote_id == str(_payment.id))
            except StopIteration:
                logger.error(
                    f"Payment {_payment.id} for Payment Instruction {_container.id} not found in Payment Gateway"
                )
                return

            _payment.status = matching_pg_payment.hope_status
            _payment.status_date = now()
            update_fields = ["status", "status_date"]

            delivered_quantity = matching_pg_payment.extra_data.get("delivered_quantity", None)
            if _payment.status in [
                Payment.STATUS_SUCCESS,
                Payment.STATUS_DISTRIBUTION_SUCCESS,
                Payment.STATUS_DISTRIBUTION_PARTIAL,
            ]:
                update_fields.extend(["delivered_quantity", "delivered_quantity_usd"])
                try:
                    delivered_quantity = int(delivered_quantity) / 100
                    _payment.delivered_quantity = delivered_quantity
                    _payment.delivered_quantity_usd = get_quantity_in_usd(
                        amount=Decimal(delivered_quantity),
                        currency=_payment_plan.currency,
                        exchange_rate=Decimal(exchange_rate),
                        currency_exchange_date=_payment_plan.currency_exchange_date,
                    )
                except (ValueError, TypeError):
                    logger.error(f"Invalid delivered_amount for Payment {_payment.id}: {delivered_quantity}")
                    _payment.delivered_quantity = None
                    _payment.delivered_quantity_usd = None

            _payment.save(update_fields=update_fields)

        payment_plans = PaymentPlan.objects.filter(
            Q(delivery_mechanisms__sent_to_payment_gateway=True) | Q(splits__sent_to_payment_gateway=True),
            status=PaymentPlan.Status.ACCEPTED,
            delivery_mechanisms__financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            delivery_mechanisms__financial_service_provider__payment_gateway_id__isnull=False,
        ).distinct()

        for payment_plan in payment_plans:
            exchange_rate = payment_plan.get_exchange_rate()

            if not payment_plan.is_reconciled:
                if payment_plan.splits.exists():
                    for split in payment_plan.splits.filter(sent_to_payment_gateway=True):
                        pg_payment_records = self.api.get_records_for_payment_instruction(split.id)
                        for payment in split.payments.filter(status=Payment.STATUS_PENDING).order_by("unicef_id"):
                            update_payment(payment, pg_payment_records, split, payment_plan, exchange_rate)
                else:
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
                            update_payment(payment, pg_payment_records, delivery_mechanism, payment_plan, exchange_rate)
