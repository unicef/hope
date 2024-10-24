import json
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Union

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    Case,
    CharField,
    Count,
    Exists,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

import _decimal
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import to_global_id
from graphql_relay.connection.arrayconnection import connection_from_list_slice

from hct_mis_api.apps.account.permissions import (
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.schema import LogEntryNode
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.field_attributes.lookup_functions import (
    get_debit_card_issuer,
    get_debit_card_number,
)
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_permission_decorator,
    decode_id_string,
    encode_id_base64,
    to_choice_object,
)
from hct_mis_api.apps.household.models import (
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    Household,
    Individual,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.filters import (
    FinancialServiceProviderFilter,
    FinancialServiceProviderXlsxTemplateFilter,
    PaymentFilter,
    PaymentPlanFilter,
    PaymentRecordFilter,
    PaymentVerificationFilter,
    PaymentVerificationLogEntryFilter,
    PaymentVerificationPlanFilter,
    cash_plan_and_payment_plan_filter,
    cash_plan_and_payment_plan_ordering,
    payment_record_and_payment_filter,
    payment_record_and_payment_ordering,
)
from hct_mis_api.apps.payment.inputs import (
    AvailableFspsForDeliveryMechanismsInput,
    GetCashplanVerificationSampleSizeInput,
)
from hct_mis_api.apps.payment.managers import ArraySubquery
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    CashPlan,
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    GenericPayment,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
    PaymentPlanSupportingDocument,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.dashboard_service import (
    payment_verification_chart_query,
    total_cash_transferred_by_administrative_area_table_query,
)
from hct_mis_api.apps.payment.services.sampling import Sampling
from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
    does_payment_record_have_right_hoh_phone_number,
)
from hct_mis_api.apps.payment.utils import (
    get_payment_items_for_dashboard,
    get_payment_plan_object,
)
from hct_mis_api.apps.targeting.graphql_types import TargetPopulationNode
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    SectionTotalNode,
    TableTotalCashTransferred,
    TableTotalCashTransferredForPeople,
)


class RapidProFlowResult(graphene.ObjectType):
    key = graphene.String()
    name = graphene.String()
    categories = graphene.List(graphene.String)
    node_uuids = graphene.List(graphene.String)


class RapidProFlowRun(graphene.ObjectType):
    active = graphene.Int()
    completed = graphene.Int()
    interrupted = graphene.Int()
    expired = graphene.Int()


class RapidProFlow(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    type = graphene.String()
    archived = graphene.Boolean()
    labels = graphene.List(graphene.String)
    expires = graphene.Int()
    runs = graphene.List(RapidProFlowRun)
    results = graphene.List(RapidProFlowResult)
    # parent_refs
    created_on = graphene.DateTime()
    modified_on = graphene.DateTime()

    def resolve_id(parent, info: Any) -> str:
        return parent["uuid"]  # type: ignore # FIXME


class FinancialServiceProviderXlsxTemplateNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_LOCK_AND_UNLOCK_FSP),)
    columns = graphene.List(graphene.String)

    class Meta:
        model = FinancialServiceProviderXlsxTemplate
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class DeliveryMechanismNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_LOCK_AND_UNLOCK_FSP),)
    code = graphene.String()
    name = graphene.String()

    class Meta:
        model = DeliveryMechanism
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FinancialServiceProviderNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_LOCK_AND_UNLOCK_FSP),)
    full_name = graphene.String(source="name")
    is_payment_gateway = graphene.Boolean()

    def resolve_is_payment_gateway(self, info: Any) -> graphene.Boolean:
        return self.is_payment_gateway

    class Meta:
        model = FinancialServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @classmethod
    def get_queryset(cls, queryset: QuerySet, info: Any) -> QuerySet:
        business_area_slug = info.context.headers.get("Business-Area")
        return queryset.all().allowed_to(business_area_slug)


class ServiceProviderNode(DjangoObjectType):
    class Meta:
        model = ServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AgeFilterObject(graphene.ObjectType):
    min = graphene.Int()
    max = graphene.Int()


class PaymentVerificationSummaryNode(DjangoObjectType):
    class Meta:
        model = PaymentVerificationSummary
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class GetCashplanVerificationSampleSizeObject(graphene.ObjectType):
    payment_record_count = graphene.Int()
    sample_size = graphene.Int()


class ChartPaymentVerification(ChartDetailedDatasetsNode):
    households = graphene.Int()
    average_sample_size = graphene.Float()


class ApprovalNode(DjangoObjectType):
    info = graphene.String()

    class Meta:
        model = Approval
        fields = ("created_at", "comment", "info", "created_by")

    def resolve_info(self, info: Any) -> graphene.String:
        return self.info


class FilteredActionsListNode(graphene.ObjectType):
    approval = graphene.List(ApprovalNode)
    authorization = graphene.List(ApprovalNode)
    finance_release = graphene.List(ApprovalNode)
    reject = graphene.List(ApprovalNode)


class ApprovalProcessNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_VIEW_DETAILS),)
    rejected_on = graphene.String()
    actions = graphene.Field(FilteredActionsListNode)

    class Meta:
        model = ApprovalProcess
        exclude = ("approvals",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_rejected_on(self, info: Any) -> Optional[str]:
        if self.approvals.filter(type=Approval.REJECT).exists():
            if self.sent_for_finance_release_date:
                return "IN_REVIEW"
            if self.sent_for_authorization_date:
                return "IN_AUTHORIZATION"
            if self.sent_for_approval_date:
                return "IN_APPROVAL"
        return None

    def resolve_actions(self, info: Any) -> "FilteredActionsListNode":
        resp = FilteredActionsListNode(
            approval=self.approvals.filter(type=Approval.APPROVAL),
            authorization=self.approvals.filter(type=Approval.AUTHORIZATION),
            finance_release=self.approvals.filter(type=Approval.FINANCE_RELEASE),
            reject=self.approvals.filter(type=Approval.REJECT),
        )
        return resp


class PaymentConflictDataNode(graphene.ObjectType):
    payment_plan_id = graphene.String()
    payment_plan_unicef_id = graphene.String()
    payment_plan_start_date = graphene.String()
    payment_plan_end_date = graphene.String()
    payment_plan_status = graphene.String()
    payment_id = graphene.String()
    payment_unicef_id = graphene.String()

    def resolve_payment_plan_id(self, info: Any) -> Optional[str]:
        return encode_id_base64(self["payment_plan_id"], "PaymentPlan")  # type: ignore

    def resolve_payment_id(self, info: Any) -> Optional[str]:
        return encode_id_base64(self["payment_id"], "Payment")  # type: ignore


class GenericPaymentNode(graphene.ObjectType):
    """using this for GenericFK like in PaymentVerification (Payment and PaymentRecord models)"""

    id = graphene.String()
    obj_type = graphene.String()
    unicef_id = graphene.String()
    currency = graphene.String()
    delivered_quantity = graphene.Float()
    delivered_quantity_usd = graphene.Float()
    household = graphene.Field(HouseholdNode)

    def resolve_id(self, info: Any) -> str:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any) -> str:
        return self.__class__.__name__

    def resolve_unicef_id(self, info: Any) -> graphene.String:
        return self.unicef_id

    def resolve_currency(self, info: Any) -> graphene.String:
        return self.currency

    def resolve_delivered_quantity_usd(self, info: Any) -> graphene.Float:
        return self.delivered_quantity_usd

    def resolve_delivered_quantity(self, info: Any) -> graphene.Float:
        return self.delivered_quantity

    def resolve_household(self, info: Any) -> graphene.Field:
        return self.household


class PaymentHouseholdSnapshotNode(BaseNodePermissionMixin, DjangoObjectType):
    class Meta:
        model = PaymentHouseholdSnapshot
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_VIEW_DETAILS),)
    payment_plan_hard_conflicted = graphene.Boolean()
    payment_plan_hard_conflicted_data = graphene.List(PaymentConflictDataNode)
    payment_plan_soft_conflicted = graphene.Boolean()
    payment_plan_soft_conflicted_data = graphene.List(PaymentConflictDataNode)
    full_name = graphene.String()
    target_population = graphene.Field(TargetPopulationNode)
    verification = graphene.Field("hct_mis_api.apps.payment.schema.PaymentVerificationNode")
    distribution_modality = graphene.String()
    service_provider = graphene.Field(FinancialServiceProviderNode)
    household_snapshot = graphene.Field(PaymentHouseholdSnapshotNode)
    debit_card_number = graphene.String()
    debit_card_issuer = graphene.String()
    additional_collector_name = graphene.String()
    additional_document_type = graphene.String()
    additional_document_number = graphene.String()
    total_persons_covered = graphene.Int(description="Get from Household Snapshot")
    snapshot_collector_full_name = graphene.String(description="Get from Household Snapshot")
    snapshot_collector_delivery_phone_no = graphene.String(description="Get from Household Snapshot")
    snapshot_collector_bank_name = graphene.String(description="Get from Household Snapshot")
    snapshot_collector_bank_account_number = graphene.String(description="Get from Household Snapshot")
    snapshot_collector_debit_card_number = graphene.String(description="Get from Household Snapshot")
    fsp_auth_code = graphene.String()

    class Meta:
        model = Payment
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment_plan_hard_conflicted_data(self, info: Any) -> List[Any]:
        if self.parent.status != PaymentPlan.Status.OPEN:
            return list()
        return PaymentNode._parse_pp_conflict_data(getattr(self, "payment_plan_hard_conflicted_data", []))

    def resolve_payment_plan_soft_conflicted_data(self, info: Any) -> List[Any]:
        if self.parent.status != PaymentPlan.Status.OPEN:
            return list()
        return PaymentNode._parse_pp_conflict_data(getattr(self, "payment_plan_soft_conflicted_data", []))

    def resolve_payment_plan_hard_conflicted(self, info: Any) -> Union[Any, graphene.Boolean]:
        return self.parent.status == PaymentPlan.Status.OPEN and self.payment_plan_hard_conflicted

    def resolve_payment_plan_soft_conflicted(self, info: Any) -> Union[Any, graphene.Boolean]:
        return self.parent.status == PaymentPlan.Status.OPEN and self.payment_plan_soft_conflicted

    def resolve_target_population(self, info: Any) -> TargetPopulation:
        return self.parent.target_population

    def resolve_full_name(self, info: Any) -> str:
        return self.head_of_household.full_name if self.head_of_household else ""

    def resolve_verification(self, info: Any) -> graphene.Field:
        return self.verification

    def resolve_distribution_modality(self, info: Any) -> str:
        return self.parent.unicef_id

    def resolve_service_provider(self, info: Any) -> Optional[FinancialServiceProvider]:
        return self.financial_service_provider

    def resolve_debit_card_number(self, info: Any) -> str:
        return get_debit_card_number(self.collector)

    def resolve_debit_card_issuer(self, info: Any) -> str:
        return get_debit_card_issuer(self.collector)

    def resolve_total_persons_covered(self, info: Any) -> Optional[int]:
        # TODO: migrate old data maybe?
        if household_snapshot := getattr(self, "household_snapshot", None):
            return household_snapshot.snapshot_data.get("size")
        else:
            # old Payment has only household.size, backward compatible with legacy data
            return self.household.size

    def resolve_additional_collector_name(self, info: Any) -> Optional[graphene.String]:
        return getattr(self, "additional_collector_name", None)

    def resolve_additional_document_type(self, info: Any) -> Optional[graphene.String]:
        return getattr(self, "additional_document_type", None)

    def resolve_additional_document_number(self, info: Any) -> Optional[graphene.String]:
        return getattr(self, "additional_document_number", None)

    def resolve_snapshot_collector_full_name(self, info: Any) -> Any:
        return PaymentNode.get_collector_field(self, "full_name")

    def resolve_snapshot_collector_delivery_phone_no(self, info: Any) -> Any:
        return PaymentNode.get_collector_field(self, "payment_delivery_phone_no")

    def resolve_snapshot_collector_bank_name(self, info: Any) -> Optional[str]:
        if bank_account_info := PaymentNode.get_collector_field(self, "bank_account_info"):
            return bank_account_info.get("bank_name")
        return None

    def resolve_snapshot_collector_bank_account_number(self, info: Any) -> Optional[str]:
        if bank_account_info := PaymentNode.get_collector_field(self, "bank_account_info"):
            return bank_account_info.get("bank_account_number")
        return None

    def resolve_snapshot_collector_debit_card_number(self, info: Any) -> Optional[str]:
        if bank_account_info := PaymentNode.get_collector_field(self, "bank_account_info"):
            return bank_account_info.get("debit_card_number")
        return None

    @classmethod
    def get_collector_field(cls, payment: "Payment", field_name: str) -> Union[None, str, Dict]:
        """return primary_collector or alternate_collector field value or None"""
        if household_snapshot := getattr(payment, "household_snapshot", None):
            household_snapshot_data = household_snapshot.snapshot_data
            collector_data = (
                household_snapshot_data.get("primary_collector")
                or household_snapshot_data.get("alternate_collector")
                or dict()
            )
            return collector_data.get(field_name)
        return None

    @classmethod
    def _parse_pp_conflict_data(cls, conflicts_data: List) -> List[Any]:
        """parse list of conflicted payment plans data from Payment model json annotations"""
        return [json.loads(conflict) for conflict in conflicts_data]

    def resolve_fsp_auth_code(self, info: Any) -> str:
        user = info.context.user

        if not user.has_permission(
            Permissions.PM_VIEW_FSP_AUTH_CODE.value,
            self.business_area,
            self.program_id,
        ):
            return ""
        return self.fsp_auth_code or ""  # type: ignore


class DeliveryMechanismPerPaymentPlanNode(DjangoObjectType):
    name = graphene.String()
    code = graphene.String()
    order = graphene.Int()
    fsp = graphene.Field(FinancialServiceProviderNode)
    chosen_configuration = graphene.String()

    def resolve_name(self, info: Any) -> graphene.String:
        return self.delivery_mechanism.name

    def resolve_code(self, info: Any) -> graphene.String:
        return self.delivery_mechanism.code

    def resolve_order(self, info: Any) -> graphene.Int:
        return self.delivery_mechanism_order

    def resolve_fsp(self, info: Any) -> graphene.Field:
        return self.financial_service_provider

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


def _calculate_volume(
    delivery_mechanism_per_payment_plan: "DeliveryMechanismPerPaymentPlan", field: str
) -> Optional[Decimal]:
    if not delivery_mechanism_per_payment_plan.financial_service_provider:
        return None
    # TODO simple volume calculation
    payments = delivery_mechanism_per_payment_plan.payment_plan.eligible_payments.filter(
        financial_service_provider=delivery_mechanism_per_payment_plan.financial_service_provider,
    )
    return payments.aggregate(entitlement_sum=Coalesce(Sum(field), Decimal(0.0)))["entitlement_sum"]


class VolumeByDeliveryMechanismNode(graphene.ObjectType):
    delivery_mechanism = graphene.Field(DeliveryMechanismPerPaymentPlanNode)
    volume = graphene.Float()
    volume_usd = graphene.Float()

    def resolve_delivery_mechanism(self, info: Any) -> "VolumeByDeliveryMechanismNode":
        return self  # DeliveryMechanismPerPaymentPlanNode uses the same model

    def resolve_volume(self, info: Any) -> Optional[_decimal.Decimal]:  # non-usd
        return _calculate_volume(self, "entitlement_quantity")  # type: ignore

    def resolve_volume_usd(self, info: Any) -> Optional[_decimal.Decimal]:
        return _calculate_volume(self, "entitlement_quantity_usd")  # type: ignore

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FspConfiguration(graphene.ObjectType):
    id = graphene.String()
    key = graphene.String()
    label = graphene.String()


class FspChoice(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    configurations = graphene.List(FspConfiguration)

    def resolve_id(self, info: Any) -> Optional[str]:
        return encode_id_base64(self["id"], "FinancialServiceProvider")  # type: ignore


class FspChoices(graphene.ObjectType):
    delivery_mechanism = graphene.String()
    fsps = graphene.List(FspChoice)


class ReconciliationSummaryNode(graphene.ObjectType):
    delivered_fully = graphene.Int()
    delivered_partially = graphene.Int()
    not_delivered = graphene.Int()
    unsuccessful = graphene.Int()
    pending = graphene.Int()
    force_failed = graphene.Int()
    number_of_payments = graphene.Int()
    reconciled = graphene.Int()


class PaymentPlanSupportingDocumentNode(DjangoObjectType):
    class Meta:
        model = PaymentPlanSupportingDocument
        interfaces = (relay.Node,)


class PaymentPlanNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PM_VIEW_DETAILS),)
    dispersion_start_date = graphene.Date()
    dispersion_end_date = graphene.Date()
    start_date = graphene.Date()
    end_date = graphene.Date()
    currency_name = graphene.String()
    has_payment_list_export_file = graphene.Boolean()
    has_fsp_delivery_mechanism_xlsx_template = graphene.Boolean()
    imported_file_name = graphene.String()
    payments_conflicts_count = graphene.Int()
    delivery_mechanisms = graphene.List(DeliveryMechanismPerPaymentPlanNode)
    volume_by_delivery_mechanism = graphene.List(VolumeByDeliveryMechanismNode)
    split_choices = graphene.List(ChoiceObject)
    verification_plans = DjangoPermissionFilterConnectionField(
        "hct_mis_api.apps.program.schema.PaymentVerificationPlanNode",  # type: ignore
        filterset_class=PaymentVerificationPlanFilter,
    )
    payment_verification_summary = graphene.Field(
        PaymentVerificationSummaryNode,
        source="get_payment_verification_summary",
    )
    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    can_create_payment_verification_plan = graphene.Boolean()
    available_payment_records_count = graphene.Int()
    reconciliation_summary = graphene.Field(ReconciliationSummaryNode)
    excluded_households = graphene.List(HouseholdNode, description="For non-social worker DCT, returns Household IDs")
    excluded_individuals = graphene.List(IndividualNode, description="For social worker DCT, returns Individual IDs")
    can_create_follow_up = graphene.Boolean()
    total_withdrawn_households_count = graphene.Int()
    unsuccessful_payments_count = graphene.Int()
    name = graphene.String()
    can_send_to_payment_gateway = graphene.Boolean()
    can_split = graphene.Boolean()
    supporting_documents = graphene.List(PaymentPlanSupportingDocumentNode)

    class Meta:
        model = PaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_split_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlanSplit.SplitType.choices)

    def resolve_verification_plans(self, info: Any) -> graphene.List:
        return self.get_payment_verification_plans

    def resolve_payments_conflicts_count(self, info: Any) -> graphene.Int:
        return self.payment_items.filter(excluded=False, payment_plan_hard_conflicted=True).count()

    def resolve_currency_name(self, info: Any) -> graphene.String:
        return self.get_currency_display()

    def resolve_delivery_mechanisms(self, info: Any) -> graphene.List:
        return DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=self).order_by("delivery_mechanism_order")

    def resolve_has_payment_list_export_file(self, info: Any) -> graphene.Boolean:
        return self.has_export_file

    def resolve_imported_file_name(self, info: Any) -> graphene.String:
        return self.imported_file_name

    def resolve_volume_by_delivery_mechanism(self, info: Any) -> graphene.List:
        return DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=self).order_by("delivery_mechanism_order")

    def resolve_available_payment_records_count(self, info: Any, **kwargs: Any) -> graphene.Int:
        return self.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0).count()

    def resolve_has_fsp_delivery_mechanism_xlsx_template(self, info: Any) -> bool:
        if (
            not self.delivery_mechanisms.exists()
            or self.delivery_mechanisms.filter(
                Q(financial_service_provider__isnull=True) | Q(delivery_mechanism__isnull=True)
            ).exists()
        ):
            return False
        else:
            for dm_per_payment_plan in self.delivery_mechanisms.all():
                if not dm_per_payment_plan.financial_service_provider.get_xlsx_template(
                    dm_per_payment_plan.delivery_mechanism
                ):
                    return False
            return True

    def resolve_total_withdrawn_households_count(self, info: Any) -> graphene.Int:
        return (
            self.eligible_payments.filter(household__withdrawn=True)
            .exclude(
                # Exclude beneficiaries who are currently in different follow-up Payment Plan within the same cycle
                household_id__in=Payment.objects.filter(
                    is_follow_up=True,
                    parent__source_payment_plan=self,
                    parent__program_cycle=self.program_cycle,
                    excluded=False,
                )
                .exclude(parent=self)
                .values_list("household_id", flat=True)
            )
            .count()
        )

    @staticmethod
    def resolve_reconciliation_summary(parent: PaymentPlan, info: Any) -> Dict[str, int]:
        return parent.eligible_payments.aggregate(
            delivered_fully=Count("id", filter=Q(status=GenericPayment.STATUS_DISTRIBUTION_SUCCESS)),
            delivered_partially=Count("id", filter=Q(status=GenericPayment.STATUS_DISTRIBUTION_PARTIAL)),
            not_delivered=Count("id", filter=Q(status=GenericPayment.STATUS_NOT_DISTRIBUTED)),
            unsuccessful=Count(
                "id",
                filter=Q(
                    status__in=[
                        GenericPayment.STATUS_ERROR,
                        GenericPayment.STATUS_FORCE_FAILED,
                        GenericPayment.STATUS_MANUALLY_CANCELLED,
                    ]
                ),
            ),
            pending=Count("id", filter=Q(status__in=GenericPayment.PENDING_STATUSES)),
            reconciled=Count("id", filter=~Q(status__in=GenericPayment.PENDING_STATUSES)),
            number_of_payments=Count("id"),
        )

    def resolve_excluded_households(self, info: Any) -> "QuerySet":
        return (
            Household.objects.filter(unicef_id__in=self.excluded_beneficiaries_ids)
            if not self.is_social_worker_program
            else Household.objects.none()
        )

    def resolve_excluded_individuals(self, info: Any) -> "QuerySet":
        return (
            Individual.objects.filter(unicef_id__in=self.excluded_beneficiaries_ids)
            if self.is_social_worker_program
            else Individual.objects.none()
        )

    def resolve_can_create_follow_up(self, info: Any) -> bool:
        # Check there are payments in error/not distributed status and excluded withdrawn households
        if self.is_follow_up:
            return False

        qs = self.unsuccessful_payments_for_follow_up()

        # Check if all payments are used in FPPs
        follow_up_payment = self.payments_used_in_follow_payment_plans()

        return qs.exists() and set(follow_up_payment.values_list("source_payment_id", flat=True)) != set(
            qs.values_list("id", flat=True)
        )

    def resolve_unsuccessful_payments_count(self, info: Any) -> int:
        return self.unsuccessful_payments_for_follow_up().count()

    def resolve_can_send_to_payment_gateway(self, info: Any) -> bool:
        return self.can_send_to_payment_gateway  # type: ignore

    def resolve_can_split(self, info: Any) -> bool:
        if self.status != PaymentPlan.Status.ACCEPTED:
            return False

        if self.splits.filter(
            sent_to_payment_gateway=True,
        ).exists():
            return False

        return True

    def resolve_supporting_documents(self, info: Any) -> "QuerySet":
        return self.documents.all()


class PaymentVerificationNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS),)
    is_manually_editable = graphene.Boolean()
    payment = graphene.Field(GenericPaymentNode)

    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment(self, info: Any) -> graphene.Field:
        return self.get_payment


class PaymentVerificationPlanNode(AdminUrlNodeMixin, DjangoObjectType):
    excluded_admin_areas_filter = graphene.List(graphene.String)
    age_filter = graphene.Field(AgeFilterObject)
    xlsx_file_was_downloaded = graphene.Boolean()
    has_xlsx_file = graphene.Boolean()
    payment_plan = graphene.Field(PaymentPlanNode)

    class Meta:
        model = PaymentVerificationPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_xlsx_file_was_downloaded(self, info: Any) -> bool:
        return self.xlsx_payment_verification_plan_file_was_downloaded

    def resolve_has_xlsx_file(self, info: Any) -> bool:
        return self.has_xlsx_payment_verification_plan_file


class PaymentRecordNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS),)
    verification = graphene.Field(PaymentVerificationNode)
    unicef_id = graphene.String(source="ca_id")

    class Meta:
        model = PaymentRecord
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentVerificationLogEntryNode(LogEntryNode):
    content_object = graphene.Field(PaymentVerificationPlanNode)

    class Meta:
        model = LogEntry
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class CashPlanAndPaymentPlanNode(BaseNodePermissionMixin, AdminUrlNodeMixin, graphene.ObjectType):
    """
    for CashPlan and PaymentPlan models
    """

    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),
    )

    obj_type = graphene.String()
    id = graphene.String()
    unicef_id = graphene.String(source="get_unicef_id")
    verification_status = graphene.String()
    status = graphene.String()
    currency = graphene.String()
    total_delivered_quantity = graphene.Float()
    start_date = graphene.String()
    end_date = graphene.String()
    program_name = graphene.String()
    updated_at = graphene.String()
    verification_plans = graphene.List(PaymentVerificationPlanNode)
    total_number_of_households = graphene.Int()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()

    # TODO: Fields with dummy data
    assistance_measurement = graphene.String()
    dispersion_date = graphene.String()
    service_provider_full_name = graphene.String()

    def resolve_id(self, info: Any, **kwargs: Any) -> str:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any, **kwargs: Any) -> str:
        return self.__class__.__name__

    def resolve_total_number_of_households(self, info: Any, **kwargs: Any) -> int:
        return self.payment_items.count()

    def resolve_verification_status(self, info: Any, **kwargs: Any) -> Optional[graphene.String]:
        return self.get_payment_verification_summary.status if self.get_payment_verification_summary else None

    def resolve_status(self, info: Any, **kwargs: Any) -> Optional[graphene.String]:
        return self.status

    def resolve_program_name(self, info: Any, **kwargs: Any) -> graphene.String:
        return self.program.name

    def resolve_verification_plans(self, info: Any, **kwargs: Any) -> graphene.List:
        return self.payment_verification_plan.all()

    # TODO: do we need this empty fields ??
    def resolve_assistance_measurement(self, info: Any, **kwargs: Any) -> str:
        return ""

    def resolve_dispersion_date(self, info: Any, **kwargs: Any) -> str:
        return ""

    def resolve_service_provider_full_name(self, info: Any, **kwargs: Any) -> str:
        return ""


class PaymentRecordAndPaymentNode(BaseNodePermissionMixin, graphene.ObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),
    )

    obj_type = graphene.String()
    id = graphene.String()
    ca_id = graphene.String(source="unicef_id")
    status = graphene.String()
    full_name = graphene.String(source="full_name")
    parent = graphene.Field(CashPlanAndPaymentPlanNode, source="parent")
    entitlement_quantity = graphene.Float(source="entitlement_quantity")
    delivered_quantity = graphene.Float(source="delivered_quantity")
    delivered_quantity_usd = graphene.Float(source="delivered_quantity_usd")
    currency = graphene.String(source="currency")
    delivery_date = graphene.String(source="delivery_date")
    verification = graphene.Field(PaymentVerificationNode, source="verification")

    def resolve_obj_type(self, info: Any, **kwargs: Any) -> str:
        return self.__class__.__name__

    def resolve_id(self, info: Any, **kwargs: Any) -> str:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_status(self, info: Any, **kwargs: Any) -> str:
        return self.status.replace(" ", "_").upper()


class PageInfoNode(graphene.ObjectType):
    start_cursor = graphene.String()
    end_cursor = graphene.String()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()


class CashPlanAndPaymentPlanEdges(graphene.ObjectType):
    cursor = graphene.String()
    node = graphene.Field(CashPlanAndPaymentPlanNode)


class PaginatedCashPlanAndPaymentPlanNode(graphene.ObjectType):
    page_info = graphene.Field(PageInfoNode)
    edges = graphene.List(CashPlanAndPaymentPlanEdges)
    total_count = graphene.Int()


class PaymentRecordsAndPaymentsEdges(graphene.ObjectType):
    cursor = graphene.String()
    node = graphene.Field(PaymentRecordAndPaymentNode)


class PaginatedPaymentRecordsAndPaymentsNode(graphene.ObjectType):
    page_info = graphene.Field(PageInfoNode)
    edges = graphene.List(PaymentRecordsAndPaymentsEdges)
    total_count = graphene.Int()


class GenericPaymentPlanNode(graphene.ObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),
    )

    id = graphene.String()
    obj_type = graphene.String()
    payment_verification_summary = graphene.Field(PaymentVerificationSummaryNode)
    available_payment_records_count = graphene.Int()
    verification_plans = DjangoPermissionFilterConnectionField(
        PaymentVerificationPlanNode,
        filterset_class=PaymentVerificationPlanFilter,
    )
    status_date = graphene.DateTime()
    status = graphene.String()

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    delivery_type = graphene.String()
    total_number_of_households = graphene.Int()
    currency = graphene.String(source="currency")
    total_delivered_quantity = graphene.Float()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()
    can_create_payment_verification_plan = graphene.Boolean()

    def resolve_id(self, info: Any, **kwargs: Any) -> graphene.String:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any, **kwargs: Any) -> str:
        return self.__class__.__name__

    def resolve_payment_verification_summary(self, info: Any, **kwargs: Any) -> graphene.Field:
        return self.get_payment_verification_summary

    def resolve_available_payment_records_count(self, info: Any, **kwargs: Any) -> graphene.Int:
        return self.payment_items.filter(
            status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    def resolve_verification_plans(self, info: Any, **kwargs: Any) -> DjangoPermissionFilterConnectionField:
        return self.get_payment_verification_plans

    def resolve_total_entitled_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_entitled_quantity

    def resolve_total_delivered_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_delivered_quantity

    def resolve_total_undelivered_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_undelivered_quantity

    def resolve_can_create_payment_verification_plan(self, info: Any, **kwargs: Any) -> graphene.Boolean:
        return self.can_create_payment_verification_plan

    def resolve_status_date(self, info: Any, **kwargs: Any) -> graphene.DateTime:
        return self.status_date

    def resolve_status(self, info: Any, **kwargs: Any) -> graphene.String:
        return self.status


class Query(graphene.ObjectType):
    payment = relay.Node.Field(PaymentNode)
    all_payments = DjangoPermissionFilterConnectionField(
        PaymentNode,
        filterset_class=PaymentFilter,
        permission_classes=(hopePermissionClass(Permissions.PM_VIEW_LIST),),
    )
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoPermissionFilterConnectionField(
        PaymentRecordNode,
        filterset_class=PaymentRecordFilter,
        permission_classes=(hopePermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),),
    )

    all_payment_records_and_payments = graphene.Field(
        PaginatedPaymentRecordsAndPaymentsNode,
        business_area=graphene.String(required=True),
        program=graphene.String(),
        household=graphene.ID(),
        order_by=graphene.String(),
        first=graphene.Int(),
        last=graphene.Int(),
        before=graphene.String(),
        after=graphene.String(),
    )

    financial_service_provider_xlsx_template = relay.Node.Field(FinancialServiceProviderXlsxTemplateNode)
    all_financial_service_provider_xlsx_templates = DjangoPermissionFilterConnectionField(
        FinancialServiceProviderXlsxTemplateNode,
        filterset_class=FinancialServiceProviderXlsxTemplateFilter,
    )
    financial_service_provider = relay.Node.Field(FinancialServiceProviderNode)
    all_financial_service_providers = DjangoPermissionFilterConnectionField(
        FinancialServiceProviderNode,
        filterset_class=FinancialServiceProviderFilter,
    )

    payment_record_verification = relay.Node.Field(PaymentVerificationNode)
    all_payment_verifications = DjangoPermissionFilterConnectionField(
        PaymentVerificationNode,
        filterset_class=PaymentVerificationFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )

    payment_verification_plan = relay.Node.Field(PaymentVerificationPlanNode)
    all_payment_verification_plan = DjangoPermissionFilterConnectionField(
        PaymentVerificationPlanNode,
        filterset_class=PaymentVerificationPlanFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )

    chart_payment_verification = graphene.Field(
        ChartPaymentVerification,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_payment_verification_for_people = graphene.Field(
        ChartPaymentVerification,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_volume_by_delivery_mechanism = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_payment = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_total_transferred = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    table_total_cash_transferred_by_administrative_area = graphene.Field(
        TableTotalCashTransferred,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
        order=graphene.String(required=False),
        order_by=graphene.String(required=False),
    )
    table_total_cash_transferred_by_administrative_area_for_people = graphene.Field(
        TableTotalCashTransferredForPeople,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
        order=graphene.String(required=False),
        order_by=graphene.String(required=False),
    )
    chart_total_transferred_cash_by_country = graphene.Field(
        ChartDetailedDatasetsNode, year=graphene.Int(required=True)
    )

    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_channel_choices = graphene.List(ChoiceObject)
    payment_verification_status_choices = graphene.List(ChoiceObject)

    all_rapid_pro_flows = graphene.List(
        RapidProFlow,
        business_area_slug=graphene.String(required=True),
    )
    sample_size = graphene.Field(
        GetCashplanVerificationSampleSizeObject,
        input=GetCashplanVerificationSampleSizeInput(),
    )

    all_payment_verification_log_entries = DjangoPermissionFilterConnectionField(
        PaymentVerificationLogEntryNode,
        filterset_class=PaymentVerificationLogEntryFilter,
        permission_classes=(hopePermissionClass(Permissions.ACTIVITY_LOG_VIEW),),
    )

    payment_plan = relay.Node.Field(PaymentPlanNode)
    all_payment_plans = DjangoPermissionFilterConnectionField(
        PaymentPlanNode,
        filterset_class=PaymentPlanFilter,
        permission_classes=(hopePermissionClass(Permissions.PM_VIEW_LIST),),
    )
    payment_plan_status_choices = graphene.List(ChoiceObject)
    currency_choices = graphene.List(ChoiceObject)
    all_delivery_mechanisms = graphene.List(ChoiceObject)
    payment_plan_background_action_status_choices = graphene.List(ChoiceObject)
    available_fsps_for_delivery_mechanisms = graphene.List(
        FspChoices,
        input=AvailableFspsForDeliveryMechanismsInput(),
    )
    all_cash_plans_and_payment_plans = graphene.Field(
        PaginatedCashPlanAndPaymentPlanNode,
        business_area=graphene.String(required=True),
        program=graphene.String(),
        search=graphene.String(),
        service_provider=graphene.String(),
        delivery_type=graphene.List(graphene.String),
        verification_status=graphene.List(graphene.String),
        start_date_gte=graphene.String(),
        end_date_lte=graphene.String(),
        order_by=graphene.String(),
        first=graphene.Int(),
        last=graphene.Int(),
        before=graphene.String(),
        after=graphene.String(),
        is_payment_verification_page=graphene.Boolean(),
    )

    def resolve_available_fsps_for_delivery_mechanisms(self, info: Any, input: Dict, **kwargs: Any) -> List:
        business_area_slug = info.context.headers.get("Business-Area")
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(input["payment_plan_id"]))
        delivery_mechanisms = (
            DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=payment_plan)
            .values_list("delivery_mechanism__name", flat=True)
            .order_by("delivery_mechanism_order")
        )

        def get_fsps_for_delivery_mechanism(mechanism_name: str) -> List:
            fsps = FinancialServiceProvider.objects.filter(
                Q(fsp_xlsx_template_per_delivery_mechanisms__delivery_mechanism__name=mechanism_name)
                | Q(fsp_xlsx_template_per_delivery_mechanisms__isnull=True),
                delivery_mechanisms__name=mechanism_name,
                allowed_business_areas__slug=business_area_slug,
            ).distinct()

            return (
                [
                    # This basically checks if FSP can accept ANY additional volume,
                    # more strict validation is performed in AssignFspToDeliveryMechanismMutation
                    {"id": fsp.id, "name": fsp.name, "configurations": fsp.configurations}
                    for fsp in fsps
                    if fsp.can_accept_any_volume()
                ]
                if fsps
                else []
            )

        return [
            {"delivery_mechanism": mechanism, "fsps": get_fsps_for_delivery_mechanism(mechanism)}
            for mechanism in delivery_mechanisms
        ]

    def resolve_all_payment_verifications(self, info: Any, **kwargs: Any) -> QuerySet:
        payment_qs = Payment.objects.filter(id=OuterRef("payment_object_id"), household__withdrawn=True)
        payment_record_qs = Payment.objects.filter(id=OuterRef("payment_object_id"), household__withdrawn=True)

        return (
            PaymentVerification.objects.filter(
                Q(payment_verification_plan__status=PaymentVerificationPlan.STATUS_ACTIVE)
                | Q(payment_verification_plan__status=PaymentVerificationPlan.STATUS_FINISHED)
            )
            .annotate(
                payment_obj__household__status=Case(
                    When(Exists(payment_qs), then=Value(STATUS_INACTIVE)),
                    When(Exists(payment_record_qs), then=Value(STATUS_INACTIVE)),
                    default=Value(STATUS_ACTIVE),
                    output_field=CharField(),
                ),
            )
            .distinct()
        )

    def resolve_sample_size(self, info: Any, input: Dict, **kwargs: Any) -> Dict[str, int]:
        payment_plan_object: Union["CashPlan", "PaymentPlan"] = get_payment_plan_object(
            input["cash_or_payment_plan_id"]
        )

        def get_payment_records(
            obj: Union["PaymentPlan", "CashPlan"],
            payment_verification_plan: Optional[PaymentVerificationPlan],
            verification_channel: str,
        ) -> QuerySet:
            kw: Dict = {}
            if payment_verification_plan:
                kw["payment_verification_plan"] = payment_verification_plan
            if verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO:
                kw["extra_validation"] = does_payment_record_have_right_hoh_phone_number
            return obj.available_payment_records(**kw)

        payment_verification_plan = None
        if payment_verification_plan_id := decode_id_string(input.get("payment_verification_plan_id")):
            payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        payment_records = get_payment_records(
            payment_plan_object, payment_verification_plan, input["verification_channel"]
        )
        if not payment_records:
            return {
                "sample_size": 0,
                "payment_record_count": 0,
            }

        sampling = Sampling(input, payment_plan_object, payment_records)
        payment_record_count, payment_records_sample_count = sampling.generate_sampling()

        return {
            "payment_record_count": payment_record_count,
            "sample_size": payment_records_sample_count,
        }

    def resolve_all_rapid_pro_flows(self, info: Any, business_area_slug: str, **kwargs: Any) -> List[RapidProFlow]:
        api = RapidProAPI(business_area_slug, RapidProAPI.MODE_VERIFICATION)
        return api.get_flows()

    def resolve_payment_record_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentRecord.STATUS_CHOICE)

    def resolve_payment_record_entitlement_card_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE)

    def resolve_payment_record_delivery_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(DeliveryMechanism.get_choices())

    def resolve_cash_plan_verification_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.STATUS_CHOICES)

    def resolve_cash_plan_verification_sampling_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.SAMPLING_CHOICES)

    def resolve_cash_plan_verification_verification_channel_choices(
        self, info: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.VERIFICATION_CHANNEL_CHOICES)

    def resolve_payment_verification_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerification.STATUS_CHOICES)

    def resolve_all_delivery_mechanisms(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(DeliveryMechanism.get_choices())

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment_verification(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        filters = chart_filters_decoder(kwargs)
        result = payment_verification_chart_query(
            year,
            business_area_slug,
            Household.CollectType.STANDARD.value,
            filters.get("program"),
            filters.get("administrative_area"),
        )
        return {
            "labels": result["labels"],
            "datasets": result["datasets"],
            "households": result["number_of_records"],
            "average_sample_size": result["average_sample_size"],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment_verification_for_people(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        filters = chart_filters_decoder(kwargs)
        result = payment_verification_chart_query(
            year,
            business_area_slug,
            Household.CollectType.SINGLE.value,
            filters.get("program"),
            filters.get("administrative_area"),
        )
        return {
            "labels": result["labels"],
            "datasets": result["datasets"],
            "households": result["number_of_records"],
            "average_sample_size": result["average_sample_size"],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_volume_by_delivery_mechanism(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        volume_by_delivery_type = (
            payment_items_qs.values("delivery_type")
            .order_by("delivery_type")
            .annotate(volume=Sum("delivered_quantity_usd"))
            .merge_by(
                "delivery_type",
                aggregated_fields=["volume"],
            )
        )

        labels = []
        data = []
        for volume_dict in volume_by_delivery_type:
            if volume_dict.get("volume"):
                dm = DeliveryMechanism.objects.get(id=volume_dict.get("delivery_type"))
                labels.append(dm.name)
                data.append(volume_dict.get("volume"))

        return {"labels": labels, "datasets": [{"data": data}]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment(self, info: Any, business_area_slug: str, year: int, **kwargs: Any) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        )
        payment_items_dict = payment_items_qs.aggregate(
            successful=Count("id", filter=~Q(status=GenericPayment.STATUS_ERROR)),
            unsuccessful=Count("id", filter=Q(status=GenericPayment.STATUS_ERROR)),
        )

        dataset = [
            {
                "data": [
                    payment_items_dict.get("successful", 0),
                    payment_items_dict.get("unsuccessful", 0),
                ]
            }
        ]

        return {"labels": ["Successful Payments", "Unsuccessful Payments"], "datasets": dataset}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_total_transferred(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        )
        return {"total": payment_items_qs.aggregate(Sum("delivered_quantity_usd"))["delivered_quantity_usd__sum"]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_table_total_cash_transferred_by_administrative_area(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        order = kwargs.pop("order", None)
        order_by = kwargs.pop("order_by", None)
        admin_areas = total_cash_transferred_by_administrative_area_table_query(
            year, business_area_slug, chart_filters_decoder(kwargs), Household.CollectType.STANDARD.value
        )

        if order_by:
            order_by_arg = None
            if order_by == "admin2":
                order_by_arg = "name"
            elif order_by == "totalCashTransferred":
                order_by_arg = "total_transferred"
            elif order_by == "totalHouseholds":
                order_by_arg = "num_households"
            if order_by_arg:
                admin_areas = admin_areas.order_by(f"{'-' if order == 'desc' else ''}{order_by_arg}")

        data = [
            {
                "id": item.id,
                "admin2": item.name,
                "total_cash_transferred": item.total_transferred,
                "total_households": item.num_households,
            }
            for item in admin_areas
        ]

        return {"data": data}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_table_total_cash_transferred_by_administrative_area_for_people(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        order = kwargs.pop("order", None)
        order_by = kwargs.pop("order_by", None)
        admin_areas = total_cash_transferred_by_administrative_area_table_query(
            year, business_area_slug, chart_filters_decoder(kwargs), Household.CollectType.SINGLE.value
        )

        if order_by:
            order_by_arg = None
            if order_by == "admin2":
                order_by_arg = "name"
            elif order_by == "totalCashTransferred":
                order_by_arg = "total_transferred"
            elif order_by == "totalHouseholds":
                order_by_arg = "num_households"
            if order_by_arg:
                admin_areas = admin_areas.order_by(f"{'-' if order == 'desc' else ''}{order_by_arg}")

        data = [
            {
                "id": item.id,
                "admin2": item.name,
                "total_cash_transferred": item.total_transferred,
                "total_people": item.num_households,
            }
            for item in admin_areas
        ]

        return {"data": data}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_total_transferred_cash_by_country(self, info: Any, year: int, **kwargs: Any) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(year, "global", {}, True)

        countries_and_amounts: dict = (
            payment_items_qs.select_related("business_area")
            .values("business_area")
            .order_by("business_area")
            .annotate(
                total_delivered_cash=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.CASH.value),
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.VOUCHER.value),
                ),
                business_area_name=F("business_area__name"),
            )
            .order_by("business_area_name")
            .merge_by("business_area_name", aggregated_fields=["total_delivered_cash", "total_delivered_voucher"])
        )

        labels = []
        cash_transferred = []
        voucher_transferred = []
        total_transferred = []
        for data_dict in countries_and_amounts:
            labels.append(data_dict.get("business_area_name"))
            cash_transferred.append(data_dict.get("total_delivered_cash") or 0)
            voucher_transferred.append(data_dict.get("total_delivered_voucher") or 0)
            total_transferred.append(cash_transferred[-1] + voucher_transferred[-1])

        datasets = [
            {"label": "Actual cash transferred", "data": cash_transferred},
            {"label": "Actual voucher transferred", "data": voucher_transferred},
            {"label": "Total transferred", "data": total_transferred},
        ]

        return {"labels": labels, "datasets": datasets}

    def resolve_currency_choices(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object([c for c in CURRENCY_CHOICES if c[0] != ""])

    def resolve_payment_plan_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlan.Status.choices)

    def resolve_payment_plan_background_action_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlan.BackgroundActionStatus.choices)

    def resolve_all_cash_plans_and_payment_plans(self, info: Any, **kwargs: Any) -> Dict[str, Any]:
        service_provider_qs = ServiceProvider.objects.filter(cash_plans=OuterRef("pk")).distinct()
        fsp_qs = FinancialServiceProvider.objects.filter(
            delivery_mechanisms_per_payment_plan__payment_plan=OuterRef("pk")
        ).distinct()
        delivery_mechanisms_per_pp_qs = DeliveryMechanismPerPaymentPlan.objects.filter(
            payment_plan=OuterRef("pk")
        ).distinct("delivery_mechanism")
        payment_verification_summary_qs = PaymentVerificationSummary.objects.filter(
            payment_plan_object_id=OuterRef("id")
        )

        if "is_payment_verification_page" in kwargs and kwargs.get("is_payment_verification_page"):
            payment_plan_qs = PaymentPlan.objects.filter(status=PaymentPlan.Status.FINISHED)
        else:
            payment_plan_qs = PaymentPlan.objects.all()

        payment_plan_qs = payment_plan_qs.annotate(
            fsp_names=ArraySubquery(fsp_qs.values_list("name", flat=True)),
            delivery_types=ArraySubquery(
                delivery_mechanisms_per_pp_qs.values_list("delivery_mechanism__name", flat=True)
            ),
            currency_order=F("currency"),
        )
        cash_plan_qs = CashPlan.objects.all().annotate(
            unicef_id=F("ca_id"),
            fsp_names=ArraySubquery(service_provider_qs.values_list("full_name", flat=True)),
            delivery_types=Func(
                [],
                F("delivery_type"),
                function="array_append",
                output_field=ArrayField(CharField(null=True)),
            ),
            currency_order=PaymentRecord.objects.filter(parent_id=OuterRef("id")).values("currency")[:1],
        )
        qs = (
            ExtendedQuerySetSequence(payment_plan_qs, cash_plan_qs)
            .annotate(
                custom_order=Case(
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_ACTIVE)),
                        then=Value(1),
                    ),
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_PENDING)),
                        then=Value(2),
                    ),
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_FINISHED)),
                        then=Value(3),
                    ),
                    output_field=IntegerField(),
                    default=Value(0),
                ),
                total_number_of_households=Count("payment_items"),
                total_entitled_quantity_order=Coalesce(
                    "total_entitled_quantity", 0, output_field=models.DecimalField()
                ),
                total_delivered_quantity_order=Coalesce(
                    "total_delivered_quantity", 0, output_field=models.DecimalField()
                ),
                total_undelivered_quantity_order=Coalesce(
                    "total_undelivered_quantity", 0, output_field=models.DecimalField()
                ),
            )
            .order_by("-updated_at", "custom_order")
        )

        # filtering
        qs: Iterable = cash_plan_and_payment_plan_filter(qs, **kwargs)  # type: ignore

        # ordering
        if order_by_value := kwargs.get("order_by"):
            qs = cash_plan_and_payment_plan_ordering(qs, order_by_value)

        # add qraphql pagination
        resp = connection_from_list_slice(
            qs,
            args=kwargs,
            connection_type=PaginatedCashPlanAndPaymentPlanNode,
            edge_type=CashPlanAndPaymentPlanEdges,
            pageinfo_type=PageInfoNode,
            list_length=len(qs),
        )
        resp.total_count = len(qs)

        return resp

    def resolve_all_payment_records_and_payments(self, info: Any, **kwargs: Any) -> Dict[str, Any]:
        """used in Household Page > Payment Records"""
        qs = ExtendedQuerySetSequence(
            PaymentRecord.objects.all(), Payment.objects.eligible().exclude(parent__is_removed=True)
        ).order_by("-updated_at")

        qs: Iterable = payment_record_and_payment_filter(qs, **kwargs)  # type: ignore

        if order_by_value := kwargs.get("order_by"):
            qs = payment_record_and_payment_ordering(qs, order_by_value)

        resp = connection_from_list_slice(
            qs,
            args=kwargs,
            connection_type=PaginatedPaymentRecordsAndPaymentsNode,
            edge_type=PaymentRecordsAndPaymentsEdges,
            pageinfo_type=PageInfoNode,
            list_length=len(qs),
        )
        resp.total_count = len(qs)
        return resp
