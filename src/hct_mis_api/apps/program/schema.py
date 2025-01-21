from typing import Any, Dict, List

from django.db.models import (
    Case,
    Count,
    DecimalField,
    F,
    IntegerField,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.account.schema import PartnerNode
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.schema import (
    ChoiceObject,
    DataCollectingTypeNode,
    PeriodicFieldNode,
)
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_permission_decorator,
    get_program_id_from_headers,
    to_choice_object,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism, PaymentPlan
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.filters import ProgramCycleFilter, ProgramFilter
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.schema import ChartDetailedDatasetsNode


class ProgramCycleNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
        ),
    )
    total_delivered_quantity_usd = graphene.Float()
    total_entitled_quantity_usd = graphene.Float()
    total_undelivered_quantity_usd = graphene.Float()

    def resolve_total_delivered_quantity_usd(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_delivered_quantity_usd

    def resolve_total_entitled_quantity_usd(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_entitled_quantity_usd

    def resolve_total_undelivered_quantity_usd(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_undelivered_quantity_usd

    class Meta:
        model = ProgramCycle
        filter_fields = [
            "status",
        ]
        exclude = [
            "unicef_id",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class BeneficiaryGroupNode(DjangoObjectType):
    class Meta:
        model = BeneficiaryGroup
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ProgramNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        ),
    )

    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    total_number_of_households_with_tp_in_program = graphene.Int()
    data_collecting_type = graphene.Field(DataCollectingTypeNode, source="data_collecting_type")
    beneficiary_group = graphene.Field(BeneficiaryGroupNode, source="beneficiary_group")
    partners = graphene.List(PartnerNode)
    is_social_worker_program = graphene.Boolean()
    pdu_fields = graphene.List(PeriodicFieldNode)
    target_populations_count = graphene.Int()
    cycles = DjangoFilterConnectionField(ProgramCycleNode, filterset_class=ProgramCycleFilter)
    can_finish = graphene.Boolean()

    class Meta:
        model = Program
        filter_fields = [
            "name",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_total_number_of_households(program: Program, info: Any, **kwargs: Any) -> int:
        return program.household_count

    @staticmethod
    def resolve_total_number_of_households_with_tp_in_program(program: Program, info: Any, **kwargs: Any) -> int:
        return program.households_with_payments_in_program.count()

    @staticmethod
    def resolve_partners(program: Program, info: Any, **kwargs: Any) -> QuerySet[Partner]:
        return (
            Partner.objects.filter(
                program_partner_through__program=program,
            )
            .annotate(partner_program=Value(program.id))
            .order_by("name")
            .distinct()
        )

    @staticmethod
    def resolve_is_social_worker_program(program: Program, info: Any, **kwargs: Any) -> bool:
        return program.is_social_worker_program

    @staticmethod
    def resolve_pdu_fields(program: Program, info: Any, **kwargs: Any) -> QuerySet:
        return program.pdu_fields.order_by("name")

    @staticmethod
    def resolve_target_populations_count(program: Program, info: Any, **kwargs: Any) -> int:
        return PaymentPlan.objects.filter(program_cycle__program=program).count()

    @staticmethod
    def resolve_can_finish(program: Program, info: Any, **kwargs: Any) -> bool:
        return program.can_finish


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY),
        ),
    )
    chart_programmes_by_sector = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_total_transferred_by_month = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    program_status_choices = graphene.List(ChoiceObject)
    program_cycle_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)
    data_collecting_type_choices = graphene.List(ChoiceObject)

    all_active_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST, Permissions.RDI_IMPORT_DATA),
        ),
    )
    # ProgramCycle
    program_cycle = relay.Node.Field(ProgramCycleNode)

    can_run_deduplication = graphene.Boolean()
    is_deduplication_disabled = graphene.Boolean()

    def resolve_can_run_deduplication(self, info: Any, **kwargs: Any) -> bool:
        program_id = get_program_id_from_headers(info.context.headers)
        if not program_id:
            return False

        program = Program.objects.only("biometric_deduplication_enabled").get(id=program_id)
        return program.biometric_deduplication_enabled

    def resolve_is_deduplication_disabled(self, info: Any, **kwargs: Any) -> bool:
        program_id = get_program_id_from_headers(info.context.headers)
        if not program_id:
            return True

        program = Program.objects.only("id").get(id=program_id)
        # deduplication engine in progress
        is_still_processing = RegistrationDataImport.objects.filter(
            program=program,
            deduplication_engine_status__in=[
                RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
            ],
        ).exists()
        # all rdis are deduplicated
        all_rdis_deduplicated = (
            RegistrationDataImport.objects.filter(program=program).all().count()
            == RegistrationDataImport.objects.filter(
                deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
                program=program,
            ).count()
        )
        # rdi merge in progress
        rdi_merging = RegistrationDataImport.objects.filter(
            program=program,
            status__in=[
                RegistrationDataImport.MERGE_SCHEDULED,
                RegistrationDataImport.MERGING,
                RegistrationDataImport.MERGE_ERROR,
            ],
        ).exists()
        return is_still_processing or all_rdis_deduplicated or rdi_merging

    def resolve_all_programs(self, info: Any, **kwargs: Any) -> QuerySet[Program]:
        if not info.context.headers.get("Business-Area"):
            raise GraphQLError("Not found header Business-Area")
        user = info.context.user
        filters = {
            "business_area__slug": info.context.headers.get("Business-Area").lower(),
            "data_collecting_type__deprecated": False,
            "data_collecting_type__isnull": False,
        }
        if not user.partner.is_unicef:
            filters.update({"id__in": user.partner.programs.values_list("id", flat=True)})
        return (
            Program.objects.filter(**filters)
            .exclude(data_collecting_type__code="unknown")
            .annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "start_date")
        )

    def resolve_program_cycle_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(ProgramCycle.STATUS_CHOICE)

    def resolve_program_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_program_frequency_of_payments_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE)

    def resolve_program_sector_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.SECTOR_CHOICE)

    def resolve_program_scope_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.SCOPE_CHOICE)

    def resolve_cash_plan_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_data_collecting_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return list(
            DataCollectingType.objects.filter(
                Q(
                    Q(
                        limit_to__slug=info.context.headers.get("Business-Area").lower(),
                    )
                    | Q(limit_to__isnull=True)
                ),
                active=True,
                deprecated=False,
            )
            .exclude(code__iexact="unknown")
            .annotate(name=F("label"))
            .annotate(value=F("code"))
            .values("name", "value")
            .order_by("name")
        )

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_programmes_by_sector(self, info: Any, business_area_slug: str, year: int, **kwargs: Any) -> Dict:
        filters = chart_filters_decoder(kwargs)
        sector_choice_mapping = dict(Program.SECTOR_CHOICE)
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(year, business_area_slug, filters, True)

        programs_ids = payment_items_qs.values_list("parent__program_cycle__program__id", flat=True)
        programs = Program.objects.filter(id__in=programs_ids).distinct()

        programmes_by_sector = (
            programs.values("sector")
            .order_by("sector")
            .annotate(total_count_without_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=False)))
            .annotate(total_count_with_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=True)))
        )
        labels = []
        programmes_wo_cash_plus = []
        programmes_with_cash_plus = []
        programmes_total = []
        for programme in programmes_by_sector:
            labels.append(sector_choice_mapping.get(programme.get("sector")))
            programmes_wo_cash_plus.append(programme.get("total_count_without_cash_plus") or 0)
            programmes_with_cash_plus.append(programme.get("total_count_with_cash_plus") or 0)
            programmes_total.append(programmes_wo_cash_plus[-1] + programmes_with_cash_plus[-1])

        datasets = [
            {"label": "Programmes", "data": programmes_wo_cash_plus},
            {"label": "Programmes with Cash+", "data": programmes_with_cash_plus},
            {"label": "Total Programmes", "data": programmes_total},
        ]

        return {"labels": labels, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_total_transferred_by_month(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        months_and_amounts = (
            payment_items_qs.annotate(
                delivery_month=F("delivery_date__month"),
                total_delivered_cash=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.CASH.value),
                    output_field=DecimalField(),
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__transfer_type=DeliveryMechanism.TransferType.VOUCHER.value),
                    output_field=DecimalField(),
                ),
            )
            .values("delivery_month", "total_delivered_cash", "total_delivered_voucher")
            .order_by("delivery_month")
        )

        months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        previous_transfers = [0] * 12
        cash_transfers = [0] * 12
        voucher_transfers = [0] * 12

        for data_dict in months_and_amounts:
            month_index = data_dict["delivery_month"] - 1
            cash_transfers[month_index] += data_dict.get("total_delivered_cash") or 0
            voucher_transfers[month_index] += data_dict.get("total_delivered_voucher") or 0

        for index in range(1, len(months_labels)):
            previous_transfers[index] = (
                previous_transfers[index - 1] + cash_transfers[index - 1] + voucher_transfers[index - 1]
            )
        datasets = [
            {"label": "Previous Transfers", "data": previous_transfers},
            {"label": "Voucher Transferred", "data": voucher_transfers},
            {"label": "Cash Transferred", "data": cash_transfers},
        ]

        return {"labels": months_labels, "datasets": datasets}

    def resolve_all_active_programs(self, info: Any, **kwargs: Any) -> QuerySet[Program]:
        return Program.objects.filter(
            status=Program.ACTIVE,
            business_area__slug=info.context.headers.get("Business-Area").lower(),
            data_collecting_type__isnull=False,
            data_collecting_type__deprecated=False,
        ).exclude(data_collecting_type__code="unknown")
