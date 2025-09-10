from _decimal import Decimal
import dataclasses
from enum import Enum
import logging
from typing import Any

from django.utils.timezone import now
from rest_framework import serializers

from hope.apps.core.api.mixins import BaseAPI
from hope.apps.core.utils import chunks
from hope.apps.payment.models import (
    AccountType,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FinancialServiceProvider,
    FspNameMapping,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hope.apps.payment.models.payment import FinancialInstitutionMapping
from hope.apps.payment.utils import (
    get_payment_delivered_quantity_status_and_value,
    get_quantity_in_usd,
    to_decimal,
)

logger = logging.getLogger(__name__)


class FlexibleArgumentsDataclassMixin:
    @classmethod
    def create_from_dict(cls, _dict: dict) -> Any:
        class_fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in _dict.items() if k in class_fields})


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args: Any, **kwargs: Any) -> dict:
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
    FINALIZED = "FINALIZED"


class PaymentInstructionFromSplitSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    external_code = serializers.SerializerMethodField()
    fsp = serializers.SerializerMethodField()
    payload = serializers.SerializerMethodField()

    def get_fsp(self, obj: Any) -> str:
        return obj.financial_service_provider.payment_gateway_id

    def get_payload(self, obj: Any) -> dict:
        payload = {
            "destination_currency": obj.payment_plan.currency,
            "user": self.context["user_email"],
            "config_key": obj.payment_plan.business_area.code,
            "delivery_mechanism": obj.delivery_mechanism.code,
        }
        if obj.payment_plan.business_area.payment_countries.count() == 1:  # TODO temporary solution
            payload["destination_country_iso_code3"] = (
                obj.payment_plan.business_area.payment_countries.first().iso_code2
            )
            payload["destination_country_iso_code2"] = (
                obj.payment_plan.business_area.payment_countries.first().iso_code3
            )
        return payload

    def get_external_code(self, obj: Any) -> str:
        return str(f"{obj.payment_plan.unicef_id}-{obj.order}")

    class Meta:
        model = PaymentPlanSplit
        fields = [
            "remote_id",
            "external_code",
            "fsp",
            "payload",
        ]


class PaymentPayloadSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    phone_no = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    destination_currency = serializers.CharField(required=True)
    origination_currency = serializers.CharField(required=False)
    delivery_mechanism = serializers.CharField(required=True)
    account_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account = serializers.DictField(required=False)


class PaymentSerializer(ReadOnlyModelSerializer):
    remote_id = serializers.CharField(source="id")
    record_code = serializers.CharField(source="unicef_id")
    payload = serializers.SerializerMethodField()
    extra_data = serializers.SerializerMethodField()

    def get_extra_data(self, obj: Payment) -> dict:
        snapshot = getattr(obj, "household_snapshot", None)
        if not snapshot:
            raise PaymentGatewayAPI.PaymentGatewayAPIError(f"Not found snapshot for Payment {obj.unicef_id}")

        return snapshot.snapshot_data

    def get_payload(self, obj: Payment) -> dict:
        snapshot_data = self.get_extra_data(obj)
        collector_data = snapshot_data.get("primary_collector") or snapshot_data.get("alternate_collector") or {}
        account_data = collector_data.get("account_data", {})

        payload_data = {
            "amount": obj.entitlement_quantity,
            "destination_currency": obj.currency,
            "delivery_mechanism": obj.delivery_type.code,
            "account_type": obj.delivery_type.account_type and obj.delivery_type.account_type.key,
            "collector_id": collector_data.get("unicef_id", ""),
            "phone_no": collector_data.get("phone_no", ""),
            "last_name": collector_data.get("family_name", ""),
            "first_name": collector_data.get("given_name", ""),
            "full_name": collector_data.get("full_name", ""),
            "middle_name": collector_data.get("middle_name", ""),
        }

        if account_data:
            if financial_institution_code := account_data.get("code"):
                """
                financial_institution_code is now collected as a specific fsp code (uba_code),
                """

                try:
                    uba_fsp = FinancialServiceProvider.objects.get(name="United Bank for Africa - Nigeria")
                except FinancialServiceProvider.DoesNotExist:
                    uba_fsp = None  # pragma: no cover

                if uba_fsp and obj.financial_service_provider == uba_fsp:
                    service_provider_code = financial_institution_code

                else:
                    try:
                        uba_mapping = FinancialInstitutionMapping.objects.get(
                            code=financial_institution_code,
                            financial_service_provider=uba_fsp,
                        )
                        fsp_mapping = FinancialInstitutionMapping.objects.get(
                            financial_institution=uba_mapping.financial_institution,
                            financial_service_provider=obj.financial_service_provider,
                        )
                        service_provider_code = fsp_mapping.code

                    except FinancialInstitutionMapping.DoesNotExist:
                        raise Exception(
                            f"No Financial Institution Mapping found for"
                            f" financial_institution_code {financial_institution_code},"
                            f" fsp {obj.financial_service_provider},"
                            f" payment {obj.id},"
                            f" collector {obj.collector}."
                        )

                account_data["service_provider_code"] = service_provider_code

            payload_data["account"] = account_data

        payload = PaymentPayloadSerializer(data=payload_data)
        if not payload.is_valid():
            raise PaymentGatewayAPI.PaymentGatewayAPIError(payload.errors)

        return payload.data

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
    payout_amount: float | None = None
    message: str | None = None

    def get_hope_status(self, entitlement_quantity: Decimal) -> str:
        def get_transferred_status_based_on_delivery_amount() -> str:
            try:
                (
                    _hope_status,
                    _quantity,
                ) = get_payment_delivered_quantity_status_and_value(self.payout_amount, entitlement_quantity)
            except ValueError:
                logger.warning(f"Invalid delivered_quantity {self.payout_amount} for Payment {self.remote_id}")
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
            logger.warning(f"Invalid Payment status: {self.status}")
            hope_status = Payment.STATUS_ERROR

        return hope_status() if callable(hope_status) else hope_status


@dataclasses.dataclass()
class PaymentInstructionData(FlexibleArgumentsDataclassMixin):
    remote_id: str
    external_code: str
    status: str  # "DRAFT"
    fsp: str
    system: int
    payload: dict
    id: int | None = None


@dataclasses.dataclass()
class FspConfig(FlexibleArgumentsDataclassMixin):
    id: int
    key: str
    delivery_mechanism: int
    delivery_mechanism_name: str
    country: str | None = None
    label: str | None = None
    required_fields: list[str] | None = None


@dataclasses.dataclass()
class FspData(FlexibleArgumentsDataclassMixin):
    id: int
    remote_id: str
    name: str
    vendor_number: str
    configs: list[FspConfig | dict]

    def __post_init__(self) -> None:
        if self.configs and isinstance(self.configs[0], dict):
            self.configs = [FspConfig.create_from_dict(config) for config in self.configs]  # type: ignore


@dataclasses.dataclass()
class AccountTypeData(FlexibleArgumentsDataclassMixin):
    id: str
    key: str
    label: str
    unique_fields: list[str]


# Based on this response fsp.names_mappings table is created and FspConfig table is populated with required fields
@dataclasses.dataclass()
class DeliveryMechanismData(FlexibleArgumentsDataclassMixin):
    id: int
    code: str
    name: str
    transfer_type: str
    account_type: str | None = None


@dataclasses.dataclass()
class AddRecordsResponseData(FlexibleArgumentsDataclassMixin):
    remote_id: str  # payment instruction id
    records: dict | None = None  # {"record_code": "remote_id"}
    errors: dict | None = None  # {"index": "error_message"}


class PaymentGatewayAPI(BaseAPI):
    API_KEY_ENV_NAME = "PAYMENT_GATEWAY_API_KEY"
    API_URL_ENV_NAME = "PAYMENT_GATEWAY_API_URL"

    class PaymentGatewayAPIError(Exception):
        pass

    class PaymentGatewayMissingAPICredentialsError(Exception):
        pass

    API_EXCEPTION_CLASS = PaymentGatewayAPIError
    API_MISSING_CREDENTIALS_EXCEPTION_CLASS = PaymentGatewayMissingAPICredentialsError

    class Endpoints:
        CREATE_PAYMENT_INSTRUCTION = "payment_instructions/"
        ABORT_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/abort/"
        CLOSE_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/close/"
        OPEN_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/open/"
        PROCESS_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/process/"
        READY_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/ready/"
        FINALIZE_PAYMENT_INSTRUCTION_STATUS = "payment_instructions/{remote_id}/finalize/"
        PAYMENT_INSTRUCTION_ADD_RECORDS = "payment_instructions/{remote_id}/add_records/"
        GET_FSPS = "fsp/"
        GET_PAYMENT_RECORDS = "payment_records/"
        GET_DELIVERY_MECHANISMS = "delivery_mechanisms/"
        GET_ACCOUNT_TYPES = "account_types/"

    def get_fsps(self) -> list[FspData]:
        response_data, _ = self._get(self.Endpoints.GET_FSPS)
        return [FspData.create_from_dict(fsp_data) for fsp_data in response_data]

    def get_delivery_mechanisms(self) -> list[DeliveryMechanismData]:
        response_data, _ = self._get(self.Endpoints.GET_DELIVERY_MECHANISMS)
        return [DeliveryMechanismData.create_from_dict(d) for d in response_data]

    def get_account_types(self) -> list[AccountTypeData]:
        response_data, _ = self._get(self.Endpoints.GET_ACCOUNT_TYPES)
        return [AccountTypeData.create_from_dict(fsp_data) for fsp_data in response_data]

    def create_payment_instruction(self, data: dict) -> PaymentInstructionData:
        response_data, _ = self._post(self.Endpoints.CREATE_PAYMENT_INSTRUCTION, data)
        return PaymentInstructionData.create_from_dict(response_data)

    def change_payment_instruction_status(
        self,
        status: PaymentInstructionStatus,
        remote_id: str,
        validate_response: bool = True,
    ) -> str:
        if status.value not in [s.value for s in PaymentInstructionStatus]:
            raise self.API_EXCEPTION_CLASS(f"Can't set invalid Payment Instruction status: {status}")

        action_endpoint_map = {
            PaymentInstructionStatus.ABORTED: self.Endpoints.ABORT_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.CLOSED: self.Endpoints.CLOSE_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.OPEN: self.Endpoints.OPEN_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.PROCESSED: self.Endpoints.PROCESS_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.READY: self.Endpoints.READY_PAYMENT_INSTRUCTION_STATUS,
            PaymentInstructionStatus.FINALIZED: self.Endpoints.FINALIZE_PAYMENT_INSTRUCTION_STATUS,
        }
        response_data, _ = self._post(
            action_endpoint_map[status].format(remote_id=remote_id),
            validate_response=validate_response,
        )

        return response_data.get("status", "")

    def add_records_to_payment_instruction(
        self,
        payment_records: list[Payment],
        remote_id: str,
        validate_response: bool = True,
    ) -> AddRecordsResponseData:
        serializer = PaymentSerializer(payment_records, many=True)
        response_data, _ = self._post(
            self.Endpoints.PAYMENT_INSTRUCTION_ADD_RECORDS.format(remote_id=remote_id),
            serializer.data,
            validate_response=validate_response,
        )
        return AddRecordsResponseData.create_from_dict(response_data)

    def get_records_for_payment_instruction(self, payment_instruction_remote_id: str) -> list[PaymentRecordData]:
        response_data, _ = self._get(
            f"{self.Endpoints.GET_PAYMENT_RECORDS}?parent__remote_id={payment_instruction_remote_id}"
        )
        return [PaymentRecordData.create_from_dict(record_data) for record_data in response_data]

    def get_record(self, payment_id: str) -> PaymentRecordData | None:
        response_data, _ = self._get(f"{self.Endpoints.GET_PAYMENT_RECORDS}?remote_id={payment_id}")
        return PaymentRecordData.create_from_dict(response_data[0]) if response_data else None


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
        if payment_plan.is_payment_gateway:
            for split in payment_plan.splits.filter(sent_to_payment_gateway=False).order_by("order"):
                data = PaymentInstructionFromSplitSerializer(split, context={"user_email": user_email}).data
                response = self.api.create_payment_instruction(data)
                if response.remote_id != str(split.id):
                    raise ValueError(f"Mismatch with remote object: {response}, _object_id: {split.id}")
                status = response.status
                if status == PaymentInstructionStatus.DRAFT.value:
                    self.api.change_payment_instruction_status(
                        status=PaymentInstructionStatus.OPEN,
                        remote_id=response.remote_id,
                    )

    def change_payment_instruction_status(
        self,
        new_status: PaymentInstructionStatus,
        obj: PaymentPlanSplit,
        validate_response: bool = True,
    ) -> str | None:
        if obj.is_payment_gateway:
            response_status = self.api.change_payment_instruction_status(
                new_status, obj.id, validate_response=validate_response
            )
            if validate_response and new_status.value != response_status:
                raise ValueError(f"Mismatch with: {new_status.value} != {response_status}")
            return response_status
        return None  # pragma: no cover

    def add_records_to_payment_instructions(
        self, payment_plan: PaymentPlan, id_filters: list[str] | None = None
    ) -> None:
        if id_filters is None:
            id_filters = []

        def _handle_errors(_response: AddRecordsResponseData, _payments: list[Payment]) -> None:
            for _idx, _payment in enumerate(_payments):
                _payment.status = Payment.STATUS_ERROR
                _payment.reason_for_unsuccessful_payment = _response.errors.get(str(_idx), "")
            Payment.objects.bulk_update(_payments, ["status", "reason_for_unsuccessful_payment"])

        def _handle_success(_response: AddRecordsResponseData, _payments: list[Payment]) -> None:
            for _payment in _payments:
                _payment.status = Payment.STATUS_SENT_TO_PG
            Payment.objects.bulk_update(_payments, ["status"])

        def _add_records(_payments: list[Payment], _container: PaymentPlanSplit) -> None:
            add_records_error = None
            for payments_chunk in chunks(_payments, self.ADD_RECORDS_CHUNK_SIZE):
                response = self.api.add_records_to_payment_instruction(
                    payments_chunk, _container.id, validate_response=True
                )
                if response.errors:
                    add_records_error = response.errors
                    _handle_errors(response, payments_chunk)
                else:
                    _handle_success(response, payments_chunk)

            if add_records_error:
                logger.error(f"Sent to Payment Gateway add records error: {add_records_error}")

            elif _payments:
                _container.sent_to_payment_gateway = True
                _container.save(update_fields=["sent_to_payment_gateway"])
                self.change_payment_instruction_status(PaymentInstructionStatus.CLOSED, _container)
                self.change_payment_instruction_status(PaymentInstructionStatus.READY, _container)

        if payment_plan.is_payment_gateway:
            for split in payment_plan.splits.filter(sent_to_payment_gateway=False).all().order_by("order"):
                payments_qs = split.split_payment_items.eligible().filter(
                    status__in=[Payment.STATUS_PENDING, Payment.STATUS_ERROR]
                )
                if id_filters:
                    # filter by id to add missing records to payment instructions
                    payments_qs = payments_qs.filter(id__in=id_filters)
                payments = list(payments_qs.order_by("unicef_id"))
                _add_records(payments, split)

    def sync_fsps(self) -> None:
        fsps_data = self.api.get_fsps()
        for fsp_data in fsps_data:
            fsp, created = FinancialServiceProvider.objects.update_or_create(
                payment_gateway_id=fsp_data.id,
                defaults={
                    "vision_vendor_number": fsp_data.vendor_number,
                    "name": fsp_data.name,
                    "communication_channel": FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
                    "data_transfer_configuration": [dataclasses.asdict(config) for config in fsp_data.configs],
                },
            )

            if not created:
                fsp.delivery_mechanisms.clear()
            delivery_mechanisms_pg_ids = {config.delivery_mechanism for config in fsp_data.configs}
            if delivery_mechanisms_pg_ids:
                delivery_mechanisms = DeliveryMechanism.objects.filter(
                    payment_gateway_id__in=delivery_mechanisms_pg_ids
                )
                fsp.delivery_mechanisms.set(delivery_mechanisms)

            # get last config for dm which doesn't have country assigned
            dm_required_fields = {}
            for config in fsp_data.configs:
                if not config.country:
                    dm_required_fields[config.delivery_mechanism] = config.required_fields

            for dm_id, required_fields in dm_required_fields.items():
                DeliveryMechanismConfig.objects.update_or_create(
                    delivery_mechanism=DeliveryMechanism.objects.get(payment_gateway_id=dm_id),
                    fsp=fsp,
                    country=None,  # TODO create config for each country in configs data?
                    defaults={"required_fields": required_fields},
                )

                for required_field in required_fields:
                    FspNameMapping.objects.get_or_create(
                        external_name=required_field,
                        fsp=fsp,
                        defaults={
                            "hope_name": required_field,
                            "source": FspNameMapping.SourceModel.ACCOUNT,
                        },
                    )

    def sync_account_types(self) -> None:
        account_types_data = self.api.get_account_types()
        for account_type_data in account_types_data:
            AccountType.objects.update_or_create(
                payment_gateway_id=account_type_data.id,
                defaults={
                    "key": account_type_data.key,
                    "label": account_type_data.label,
                    "unique_fields": account_type_data.unique_fields or [],
                },
            )

    @staticmethod
    def update_payment(
        payment: Payment,
        pg_payment_records: list[PaymentRecordData],
        container: PaymentPlanSplit,
        payment_plan: PaymentPlan,
        exchange_rate: float,
    ) -> None:
        try:
            matching_pg_payment = next(p for p in pg_payment_records if p.remote_id == str(payment.id))
        except StopIteration:
            logger.warning(f"Payment {payment.id} for Payment Instruction {container.id} not found in Payment Gateway")
            return

        payment.status = matching_pg_payment.get_hope_status(payment.entitlement_quantity)
        payment.status_date = now()
        payment.fsp_auth_code = matching_pg_payment.auth_code
        payment.reason_for_unsuccessful_payment = matching_pg_payment.message
        update_fields = [
            "status",
            "status_date",
            "fsp_auth_code",
            "reason_for_unsuccessful_payment",
        ]

        delivered_quantity = matching_pg_payment.payout_amount
        if payment.status in [
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Payment.STATUS_NOT_DISTRIBUTED,
        ]:
            if payment.status == Payment.STATUS_NOT_DISTRIBUTED and delivered_quantity is None:
                delivered_quantity = 0

            update_fields.extend(["delivered_quantity", "delivered_quantity_usd"])
            payment.delivered_quantity = to_decimal(delivered_quantity)
            payment.delivered_quantity_usd = get_quantity_in_usd(
                amount=Decimal(delivered_quantity),  # type: ignore
                currency=payment_plan.currency,
                exchange_rate=Decimal(exchange_rate),
                currency_exchange_date=payment_plan.currency_exchange_date,
            )

        payment.save(update_fields=update_fields)

    def sync_records(self) -> None:
        payment_plans = PaymentPlan.objects.filter(
            splits__sent_to_payment_gateway=True,
            status=PaymentPlan.Status.ACCEPTED,
            financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            financial_service_provider__payment_gateway_id__isnull=False,
        ).distinct()

        for payment_plan in payment_plans:
            exchange_rate = payment_plan.exchange_rate

            if not payment_plan.is_reconciled and payment_plan.is_payment_gateway:
                payment_instructions = payment_plan.splits.filter(sent_to_payment_gateway=True)
                for instruction in payment_instructions:
                    pending_payments = (
                        instruction.split_payment_items.eligible()
                        .filter(status__in=self.PENDING_UPDATE_PAYMENT_STATUSES)
                        .order_by("unicef_id")
                    )
                    if pending_payments.exists():
                        pg_payment_records = self.api.get_records_for_payment_instruction(instruction.id)
                        for payment in pending_payments:
                            self.update_payment(
                                payment,
                                pg_payment_records,
                                instruction,
                                payment_plan,
                                exchange_rate,
                            )
                        payment_plan.update_money_fields()

                if payment_plan.is_reconciled:
                    payment_plan.status_finished()
                    payment_plan.save()
                    for instruction in payment_instructions:
                        self.change_payment_instruction_status(PaymentInstructionStatus.FINALIZED, instruction)

    def sync_record(self, payment: Payment) -> None:
        if not payment.parent.is_payment_gateway:
            return  # pragma: no cover

        pg_payment_record = self.api.get_record(payment.id)
        if pg_payment_record:
            self.update_payment(
                payment,
                [pg_payment_record],
                payment.parent_split,
                payment.parent,
                payment.parent.exchange_rate,
            )

    def sync_payment_plan(self, payment_plan: PaymentPlan) -> None:
        exchange_rate = payment_plan.exchange_rate

        if not payment_plan.is_payment_gateway:
            return  # pragma: no cover

        payment_instructions = payment_plan.splits.filter(sent_to_payment_gateway=True)

        for instruction in payment_instructions:
            payments = instruction.split_payment_items.eligible().all().order_by("unicef_id")
            pg_payment_records = self.api.get_records_for_payment_instruction(instruction.id)
            for payment in payments:
                self.update_payment(
                    payment,
                    pg_payment_records,
                    instruction,
                    payment_plan,
                    exchange_rate,
                )

        if payment_plan.is_reconciled:
            payment_plan.status_finished()
            payment_plan.save()
            for instruction in payment_instructions:
                self.change_payment_instruction_status(
                    PaymentInstructionStatus.FINALIZED,
                    instruction,
                    validate_response=False,
                )

    def sync_delivery_mechanisms(self) -> None:
        delivery_mechanisms: list[DeliveryMechanismData] = self.api.get_delivery_mechanisms()
        for dm in delivery_mechanisms:
            DeliveryMechanism.objects.update_or_create(
                payment_gateway_id=dm.id,
                defaults={
                    "code": dm.code,
                    "name": dm.name,
                    "transfer_type": dm.transfer_type,
                    "is_active": True,
                    "account_type": (
                        AccountType.objects.get(payment_gateway_id=dm.account_type) if dm.account_type else None
                    ),
                },
            )

    def add_missing_records_to_payment_instructions(self, payment_plan: PaymentPlan) -> None:
        record_ids: list[str] = []
        for payment in payment_plan.eligible_payments.all():
            pg_payment_record = self.api.get_record(payment.id)
            if not pg_payment_record:
                record_ids.append(str(payment.pk))

        if record_ids:
            self.add_records_to_payment_instructions(payment_plan, record_ids)
