import dataclasses
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from django.db.models import Q
from django.utils.timezone import now

from _decimal import Decimal
from rest_framework import serializers

from hct_mis_api.apps.core.api.mixins import BaseAPI
from hct_mis_api.apps.core.utils import chunks
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.utils import (
    get_payment_delivered_quantity_status_and_value,
    get_quantity_in_usd,
    to_decimal,
)

logger = logging.getLogger(__name__)


class FlexibleArgumentsDataclassMixin:
    @classmethod
    def create_from_dict(cls, _dict: Dict) -> Any:
        class_fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in _dict.items() if k in class_fields})


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
            "config_key": obj.payment_plan.business_area.code,  # obj.chosen_configuration,
            "delivery_mechanism": obj.delivery_mechanism.code,
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
    unicef_id = serializers.SerializerMethodField()  # type: ignore

    def get_unicef_id(self, obj: Any) -> str:
        return f"{obj.payment_plan.unicef_id}-{obj.order}"

    class Meta:
        model = PaymentPlanSplit
        fields = [
            "remote_id",
            "unicef_id",
            "fsp",
            "payload",
            "extra",
        ]


class PaymentPayloadSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    phone_no = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    destination_currency = serializers.CharField(required=True)
    service_provider_code = serializers.CharField(required=False, allow_blank=True)


class PaymentSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    record_code = serializers.CharField(source="unicef_id")
    payload = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    def get_extra_data(self, obj: Payment) -> Dict:
        return {}

    def get_payload(self, obj: Payment) -> Dict:
        snapshot = getattr(obj, "household_snapshot", None)
        if not snapshot:
            logger.error(f"Not found snapshot for Payment {obj.unicef_id}")

        snapshot_data = snapshot.snapshot_data
        collector_data = snapshot_data.get("primary_collector") or snapshot_data.get("alternate_collector") or dict()
        delivery_mech_data = collector_data.get("delivery_mechanisms_data", {}).get(obj.delivery_type.code, {})

        base_data = {
            "amount": obj.entitlement_quantity,
            "destination_currency": obj.currency,
            "phone_no": collector_data.get("phone_no", ""),
            "last_name": collector_data.get("family_name", ""),
            "first_name": collector_data.get("given_name", ""),
            "full_name": collector_data.get("full_name", ""),
        }
        if obj.delivery_type.code == "mobile_money" and not delivery_mech_data:  # this workaround need to be dropped
            base_data["service_provider_code"] = collector_data.get("flex_fields", {}).get(
                "service_provider_code_i_f", ""
            )

        payload = PaymentPayloadSerializer(data=base_data)
        if not payload.is_valid():
            raise PaymentGatewayAPI.PaymentGatewayAPIException(payload.errors)

        payload_data = payload.data

        if delivery_mech_data:
            payload_data.update(delivery_mech_data)

        return payload_data

    class Meta:
        model = Payment
        fields = [
            "remote_id",
            "record_code",
            "payload",
            "extra_data",
        ]


@dataclasses.dataclass()
class PaymentRecordData(FlexibleArgumentsDataclassMixin):
    id: int
    remote_id: str
    created: str
    modified: str
    record_code: str
    parent: str
    status: str
    auth_code: str
    fsp_code: str
    payout_amount: Optional[float] = None
    message: Optional[str] = None

    def get_hope_status(self, entitlement_quantity: Decimal) -> str:
        def get_transferred_status_based_on_delivery_amount() -> str:
            try:
                _hope_status, _quantity = get_payment_delivered_quantity_status_and_value(
                    self.payout_amount, entitlement_quantity
                )
            except Exception:
                logger.error(f"Invalid delivered_quantity {self.payout_amount} for Payment {self.remote_id}")
                _hope_status = Payment.STATUS_ERROR
            return _hope_status

        mapping = {
            "PENDING": Payment.STATUS_SENT_TO_PG,
            "TRANSFERRED_TO_FSP": Payment.STATUS_SENT_TO_FSP,
            "TRANSFERRED_TO_BENEFICIARY": lambda: get_transferred_status_based_on_delivery_amount(),
            "REFUND": Payment.STATUS_NOT_DISTRIBUTED,
            "PURGED": Payment.STATUS_NOT_DISTRIBUTED,
            "ERROR": Payment.STATUS_ERROR,
            "CANCELLED": Payment.STATUS_MANUALLY_CANCELLED,
        }

        hope_status = mapping.get(self.status)
        if not hope_status:
            logger.error(f"Invalid Payment status: {self.status}")
            hope_status = Payment.STATUS_ERROR

        return hope_status() if callable(hope_status) else hope_status


@dataclasses.dataclass()
class PaymentInstructionData(FlexibleArgumentsDataclassMixin):
    remote_id: str
    unicef_id: str
    status: str  # "DRAFT"
    fsp: str
    system: int
    payload: dict
    extra: dict
    id: Optional[int] = None


@dataclasses.dataclass()
class FspConfig(FlexibleArgumentsDataclassMixin):
    id: int
    key: str
    delivery_mechanism: int
    delivery_mechanism_name: str
    label: Optional[str] = None


@dataclasses.dataclass()
class FspData(FlexibleArgumentsDataclassMixin):
    id: int
    remote_id: str
    name: str
    vision_vendor_number: str
    configs: List[Union[FspConfig, Dict]]

    def __post_init__(self) -> None:
        if self.configs and isinstance(self.configs[0], dict):
            self.configs = [FspConfig.create_from_dict(config) for config in self.configs]  # type: ignore


@dataclasses.dataclass()
class DeliveryMechanismDataRequirements(FlexibleArgumentsDataclassMixin):
    required_fields: List[str]
    optional_fields: List[str]
    unique_fields: List[str]


@dataclasses.dataclass()
class DeliveryMechanismData(FlexibleArgumentsDataclassMixin):
    id: int
    code: str
    name: str
    requirements: Union[DeliveryMechanismDataRequirements, Dict]
    transfer_type: str

    def __post_init__(self) -> None:
        if isinstance(self.requirements, dict):
            self.requirements = DeliveryMechanismDataRequirements.create_from_dict(self.requirements)


@dataclasses.dataclass()
class AddRecordsResponseData(FlexibleArgumentsDataclassMixin):
    remote_id: str  # payment instruction id
    records: Optional[dict] = None  # {"record_code": "remote_id"}
    errors: Optional[dict] = None  # {"index": "error_message"}


class PaymentGatewayAPI(BaseAPI):
    API_KEY_ENV_NAME = "PAYMENT_GATEWAY_API_KEY"
    API_URL_ENV_NAME = "PAYMENT_GATEWAY_API_URL"

    class PaymentGatewayAPIException(Exception):
        pass

    class PaymentGatewayMissingAPICredentialsException(Exception):
        pass

    API_EXCEPTION_CLASS = PaymentGatewayAPIException
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = PaymentGatewayMissingAPICredentialsException

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
        GET_DELIVERY_MECHANISMS = "delivery_mechanisms/"

    def get_fsps(self) -> List[FspData]:
        response_data, _ = self._get(self.Endpoints.GET_FSPS)
        return [FspData.create_from_dict(fsp_data) for fsp_data in response_data]

    def get_delivery_mechanisms(self) -> List[DeliveryMechanismData]:
        response_data, _ = self._get(self.Endpoints.GET_DELIVERY_MECHANISMS)
        return [DeliveryMechanismData.create_from_dict(d) for d in response_data]

    def create_payment_instruction(self, data: dict) -> PaymentInstructionData:
        response_data, _ = self._post(self.Endpoints.CREATE_PAYMENT_INSTRUCTION, data)
        return PaymentInstructionData.create_from_dict(response_data)

    def change_payment_instruction_status(self, status: PaymentInstructionStatus, remote_id: str) -> str:
        if status.value not in [s.value for s in PaymentInstructionStatus]:
            raise self.API_EXCEPTION_CLASS(f"Can't set invalid Payment Instruction status: {status}")

        action_endpoint_map = {
            PaymentInstructionStatus.ABORTED: self.Endpoints.ABORT_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.CLOSED: self.Endpoints.CLOSE_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.OPEN: self.Endpoints.OPEN_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.PROCESSED: self.Endpoints.PROCESS_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.READY: self.Endpoints.READY_PAYMENT_INSTRUCTION_STATUS,
        }
        response_data, _ = self._post(action_endpoint_map[status].format(remote_id=remote_id))

        return response_data["status"]

    def add_records_to_payment_instruction(
        self, payment_records: List[Payment], remote_id: str, validate_response: bool = True
    ) -> AddRecordsResponseData:
        serializer = PaymentSerializer(payment_records, many=True)
        response_data, _ = self._post(
            self.Endpoints.PAYMENT_INSTRUCTION_ADD_RECORDS.format(remote_id=remote_id),
            serializer.data,
            validate_response=validate_response,
        )
        return AddRecordsResponseData.create_from_dict(response_data)

    def get_records_for_payment_instruction(self, payment_instruction_remote_id: str) -> List[PaymentRecordData]:
        response_data, _ = self._get(
            f"{self.Endpoints.GET_PAYMENT_RECORDS}?parent__remote_id={payment_instruction_remote_id}"
        )
        return [PaymentRecordData.create_from_dict(record_data) for record_data in response_data]


class PaymentGatewayService:
    ADD_RECORDS_CHUNK_SIZE = 500
    PENDING_UPDATE_PAYMENT_STATUSES = [
        Payment.STATUS_PENDING,
        Payment.STATUS_SENT_TO_PG,
        Payment.STATUS_SENT_TO_FSP,
    ]

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
            status = response.status
            if status == PaymentInstructionStatus.DRAFT.value:
                status = self.api.change_payment_instruction_status(
                    status=PaymentInstructionStatus.OPEN, remote_id=response.remote_id
                )
            assert status == PaymentInstructionStatus.OPEN.value, status

        if payment_plan.splits.exists():
            for split in payment_plan.splits.filter(sent_to_payment_gateway=False).order_by("order"):
                if split.financial_service_provider.is_payment_gateway:
                    _create_payment_instruction(PaymentInstructionFromSplitSerializer, split)

        else:
            # for each sfp, create payment instruction
            for delivery_mechanism in payment_plan.delivery_mechanisms.filter(sent_to_payment_gateway=False):
                if delivery_mechanism.financial_service_provider.is_payment_gateway:
                    _create_payment_instruction(
                        PaymentInstructionFromDeliveryMechanismPerPaymentPlanSerializer, delivery_mechanism
                    )

    def change_payment_instruction_status(
        self, new_status: PaymentInstructionStatus, obj: Union[DeliveryMechanismPerPaymentPlan, PaymentPlanSplit]
    ) -> Optional[str]:
        if obj.financial_service_provider.is_payment_gateway:
            response_status = self.api.change_payment_instruction_status(new_status, obj.id)
            assert new_status.value == response_status, f"{new_status.value} != {response_status}"
            return response_status
        return None

    def add_records_to_payment_instructions(self, payment_plan: PaymentPlan) -> None:
        def _handle_errors(_response: AddRecordsResponseData, _payments: List[Payment]) -> None:
            for _idx, _payment in enumerate(_payments):
                _payment.status = Payment.STATUS_ERROR
                _payment.reason_for_unsuccessful_payment = _response.errors.get(str(_idx), "")
            Payment.objects.bulk_update(_payments, ["status", "reason_for_unsuccessful_payment"])

        def _handle_success(_response: AddRecordsResponseData, _payments: List[Payment]) -> None:
            for _payment in _payments:
                _payment.status = Payment.STATUS_SENT_TO_PG
            Payment.objects.bulk_update(_payments, ["status"])

        def _add_records(
            _payments: List[Payment], _container: Union[DeliveryMechanismPerPaymentPlan, PaymentPlanSplit]
        ) -> None:
            add_records_error = False
            for payments_chunk in chunks(_payments, self.ADD_RECORDS_CHUNK_SIZE):
                response = self.api.add_records_to_payment_instruction(
                    payments_chunk, _container.id, validate_response=False
                )
                if response.errors:
                    add_records_error = True
                    _handle_errors(response, payments_chunk)
                else:
                    _handle_success(response, payments_chunk)

            if not add_records_error:
                _container.sent_to_payment_gateway = True
                _container.save(update_fields=["sent_to_payment_gateway"])
                self.change_payment_instruction_status(PaymentInstructionStatus.CLOSED, _container)
                self.change_payment_instruction_status(PaymentInstructionStatus.READY, _container)

        if payment_plan.splits.exists():
            for split in payment_plan.splits.filter(sent_to_payment_gateway=False).all().order_by("order"):
                if split.financial_service_provider.is_payment_gateway:
                    payments = list(split.payments.order_by("unicef_id"))
                    _add_records(payments, split)

        else:
            for delivery_mechanism in payment_plan.delivery_mechanisms.filter(sent_to_payment_gateway=False):
                if delivery_mechanism.financial_service_provider.is_payment_gateway:
                    payments = list(
                        payment_plan.eligible_payments.filter(
                            financial_service_provider=delivery_mechanism.financial_service_provider
                        ).order_by("unicef_id")
                    )
                    _add_records(payments, delivery_mechanism)

    def sync_fsps(self) -> None:
        fsps_data = self.api.get_fsps()
        for fsp_data in fsps_data:
            fsp, created = FinancialServiceProvider.objects.update_or_create(
                payment_gateway_id=fsp_data.id,
                defaults={
                    "vision_vendor_number": fsp_data.vision_vendor_number,
                    "name": fsp_data.name,
                    "communication_channel": FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                    "data_transfer_configuration": [dataclasses.asdict(config) for config in fsp_data.configs],
                },
            )

            if not created:
                fsp.delivery_mechanisms.clear()
            delivery_mechanisms_pg_ids = set([config.delivery_mechanism for config in fsp_data.configs])
            if delivery_mechanisms_pg_ids:
                delivery_mechanisms = DeliveryMechanism.objects.filter(
                    payment_gateway_id__in=delivery_mechanisms_pg_ids
                )
                fsp.delivery_mechanisms.set(delivery_mechanisms)

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
                logger.warning(
                    f"Payment {_payment.id} for Payment Instruction {_container.id} not found in Payment Gateway"
                )
                return

            _payment.status = matching_pg_payment.get_hope_status(_payment.entitlement_quantity)
            _payment.status_date = now()
            _payment.fsp_auth_code = matching_pg_payment.auth_code
            update_fields = ["status", "status_date", "fsp_auth_code"]

            if _payment.status in [
                Payment.STATUS_ERROR,
                Payment.STATUS_MANUALLY_CANCELLED,
            ]:
                if matching_pg_payment.message:
                    _payment.reason_for_unsuccessful_payment = matching_pg_payment.message
                elif matching_pg_payment.payout_amount:
                    _payment.reason_for_unsuccessful_payment = f"Delivered amount: {matching_pg_payment.payout_amount}"
                else:
                    _payment.reason_for_unsuccessful_payment = "Unknown error"
                update_fields.append("reason_for_unsuccessful_payment")

            delivered_quantity = matching_pg_payment.payout_amount
            if _payment.status in [
                Payment.STATUS_DISTRIBUTION_SUCCESS,
                Payment.STATUS_DISTRIBUTION_PARTIAL,
                Payment.STATUS_NOT_DISTRIBUTED,
            ]:
                if _payment.status == Payment.STATUS_NOT_DISTRIBUTED and delivered_quantity is None:
                    delivered_quantity = 0

                update_fields.extend(["delivered_quantity", "delivered_quantity_usd"])
                try:
                    _payment.delivered_quantity = to_decimal(delivered_quantity)
                    _payment.delivered_quantity_usd = get_quantity_in_usd(
                        amount=Decimal(delivered_quantity),  # type: ignore
                        currency=_payment_plan.currency,
                        exchange_rate=Decimal(_exchange_rate),
                        currency_exchange_date=_payment_plan.currency_exchange_date,
                    )
                except (ValueError, TypeError):
                    logger.warning(f"Invalid delivered_amount for Payment {_payment.id}: {delivered_quantity}")
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
                        pending_payments = split.payments.filter(
                            status__in=self.PENDING_UPDATE_PAYMENT_STATUSES
                        ).order_by("unicef_id")
                        if pending_payments.exists():
                            pg_payment_records = self.api.get_records_for_payment_instruction(split.id)
                            for payment in pending_payments:
                                update_payment(payment, pg_payment_records, split, payment_plan, exchange_rate)
                else:
                    for delivery_mechanism in payment_plan.delivery_mechanisms.filter(
                        financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                        financial_service_provider__payment_gateway_id__isnull=False,
                        sent_to_payment_gateway=True,
                    ):
                        pending_payments = payment_plan.eligible_payments.filter(
                            financial_service_provider=delivery_mechanism.financial_service_provider,
                            status__in=self.PENDING_UPDATE_PAYMENT_STATUSES,
                        ).order_by("unicef_id")
                        if pending_payments.exists():
                            pg_payment_records = self.api.get_records_for_payment_instruction(delivery_mechanism.id)
                            for payment in pending_payments:
                                update_payment(
                                    payment, pg_payment_records, delivery_mechanism, payment_plan, exchange_rate
                                )

    def sync_delivery_mechanisms(self) -> None:
        delivery_mechanisms: List[DeliveryMechanismData] = self.api.get_delivery_mechanisms()
        for dm in delivery_mechanisms:
            DeliveryMechanism.objects.update_or_create(
                code=dm.code,
                defaults={
                    "payment_gateway_id": dm.id,
                    "name": dm.name,
                    "required_fields": dm.requirements.required_fields,
                    "optional_fields": dm.requirements.optional_fields,
                    "unique_fields": dm.requirements.unique_fields,
                    "transfer_type": dm.transfer_type,
                    "is_active": True,
                },
            )
