import graphene

from django.db.models import (
    Case,
    Count,
    DecimalField,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
    F,
    CharField,
    OuterRef,
    Exists,
    Subquery,
)
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence

from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_map_choices,
    chart_permission_decorator,
    to_choice_object,
)
from hct_mis_api.apps.payment.models import (
    PaymentVerificationPlan,
    PaymentRecord,
    GenericPayment,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    ServiceProvider, PaymentPlan
)
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.filters import ProgramFilter
from hct_mis_api.apps.payment.filters import CashPlanFilter, CashPlanPaymentPlanFilter
from hct_mis_api.apps.payment.utils import get_payment_cash_plan_items_sequence_qs
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.payment.models import CashPlan
from hct_mis_api.apps.utils.schema import ChartDetailedDatasetsNode


class ProgramNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
        ),
    )

    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    individual_data_needed = graphene.Boolean()

    class Meta:
        model = Program
        filter_fields = [
            "name",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_history(self, info):
        return self.history.all()

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households


class CashPlanNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    )

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    delivery_type = graphene.String()
    total_number_of_households = graphene.Int()
    currency = graphene.String(source="currency")
    total_delivered_quantity = graphene.Float()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()
    can_create_payment_verification_plan = graphene.Boolean()
    available_payment_records_count = graphene.Int()

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households

    def resolve_can_create_payment_verification_plan(self, info, **kwargs):
        return self.can_create_payment_verification_plan

    def resolve_available_payment_records_count(self, info, **kwargs):
        return self.payment_items.filter(
            status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()


class GenericPaymentPlanNode(ObjectType):
    # TODO: add perms
    # permission_classes = (
    #     hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
    #     hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    # )

    id = graphene.String(source="pk")


class CashPlanAndPaymentPlanNode(ObjectType):  # BaseNodePermissionMixin
    """
    for CashPlan and PaymentPlan models
    """
    # permission_classes = (
    #     hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
    #     hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    # )  # TODO: add Perms

    is_payment_plan = graphene.Boolean()
    id = graphene.String(source="pk")
    unicef_id = graphene.String(source="unicef_id")
    verification_status = graphene.String()
    fsp_names = graphene.String()
    delivery_mechanisms = graphene.String(source="delivery_type")
    delivery_types = graphene.String(source="delivery_types")
    currency = graphene.String(source="currency")
    total_delivered_quantity = graphene.Float(source="total_delivered_quantity")
    start_date = graphene.String(source="start_date")
    end_date = graphene.String(source="end_date")
    programme_name = graphene.String()
    updated_at = graphene.String(source="updated_at")

    def resolve_is_payment_plan(self, info, **kwargs):
        return self.__class__.__name__ == "PaymentPlan"

    def resolve_verification_status(self, info, **kwargs):
        return self.payment_verification_summary.status if getattr(self, "payment_verification_summary", None) else None

    def resolve_fsp_names(self, info, **kwargs):
        return self.fsp_names

    def resolve_programme_name(self, info, **kwargs):
        return self.program.name


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY),
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

    cash_plan = relay.Node.Field(CashPlanNode)
    # TODO: maybe deprecated going to use 'all_cash_plans_and_payment_plans'
    all_cash_plans = DjangoPermissionFilterConnectionField(
        CashPlanNode,
        filterset_class=CashPlanFilter,
        permission_classes=(
            hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_LIST),
            hopePermissionClass(
                Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
            ),
        ),
    )
    all_cash_plans_and_payment_plans = graphene.List(
        CashPlanAndPaymentPlanNode,
        business_area=graphene.String(required=True),
        program=graphene.String(required=False),
        search=graphene.String(required=False),
        service_provider=graphene.String(required=False),
        delivery_type=graphene.String(required=False),
        verification_status=graphene.String(required=False),
        start_date_gte=graphene.String(required=False),
        end_date_lte=graphene.String(required=False),
        order_by=graphene.String(required=False),
        first=graphene.Int(required=False),
    )
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)

    def resolve_all_programs(self, info, **kwargs):
        return (
            Program.objects.annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "start_date")
        )

    def resolve_program_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_program_frequency_of_payments_choices(self, info, **kwargs):
        return to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE)

    def resolve_program_sector_choices(self, info, **kwargs):
        return to_choice_object(Program.SECTOR_CHOICE)

    def resolve_program_scope_choices(self, info, **kwargs):
        return to_choice_object(Program.SCOPE_CHOICE)

    def resolve_cash_plan_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_all_cash_plans(self, info, **kwargs):
        return CashPlan.objects.annotate(
            custom_order=Case(
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_ACTIVE,
                    then=Value(1),
                ),
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_PENDING,
                    then=Value(2),
                ),
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_FINISHED,
                    then=Value(3),
                ),
                output_field=IntegerField(),
            )
        ).order_by("-updated_at", "custom_order")

    def resolve_all_cash_plans_and_payment_plans(self, info, **kwargs):
        qs = ExtendedQuerySetSequence(
            # TODO: added only for tests
            # PaymentPlan.objects.filter(status=PaymentPlan.Status.RECONCILED),
            PaymentPlan.objects.all(),
            CashPlan.objects.all()
        )
        print("KW== > ", kwargs)

        service_provider_qs = ServiceProvider.objects.filter(cash_plans=OuterRef("id")).distinct()
        cash_plan_qs = CashPlan.objects.filter(id=OuterRef("id")).distinct()

        delivery_mechanisms_per_payment_plan_qs = DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=OuterRef('pk'))
        fsp_ids = delivery_mechanisms_per_payment_plan_qs.values_list("financial_service_provider", flat=True)
        fsp_qs = FinancialServiceProvider.objects.filter(id__in=fsp_ids).distinct()


        qs = qs.annotate(
            custom_order=Case(
                When(
                    payment_verification_summary__isnull=True,
                    then=Value(0),
                ),
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_ACTIVE,
                    then=Value(1),
                ),
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_PENDING,
                    then=Value(2),
                ),
                When(
                    payment_verification_summary__status=PaymentVerificationPlan.STATUS_FINISHED,
                    then=Value(3),
                ),
                output_field=IntegerField(),
            ),
            fsp_names=Case(
                When(
                    Exists(service_provider_qs),
                    then=Subquery(service_provider_qs.values_list("full_name", flat=True)),
                ),
                When(
                    Exists(delivery_mechanisms_per_payment_plan_qs),
                    then=Value("FSP qs"),
                    # TODO: upd query
                    # then=Subquery(fsp_qs.values_list("name", flat=True)),
                ),
                default=Value(""),
                output_field=CharField(),
            ),
            # TODO: upd 'delivery_types'
            delivery_types=Case(
                When(
                    Exists(service_provider_qs),
                    # then=F("delivery_type"),
                    then=Value("from cash_plan"),

                ),
                When(
                    Exists(delivery_mechanisms_per_payment_plan_qs),
                    then=Value("list form delivery_mechanisms_per_payment_plan")
                    # then=Subquery(delivery_mechanisms_per_payment_plan_qs.values_list("delivery_mechanism", flat=True)),
                ),
                default=Value(""),
                output_field=CharField(),
            )

        ).order_by("-updated_at", "custom_order")

        business_area = kwargs.get("business_area")
        if business_area:
            qs = qs.filter(business_area__slug=business_area)

        order_by_value = kwargs.get("order_by")

        if order_by_value:
            reverse = order_by_value.startswith("-")
            order_by = order_by_value[1:] if reverse else order_by_value
            # unicef_id, verification_status, start_date, program__name, updated_at
            if order_by == "verification_status":
                if reverse:
                    qs = qs.order_by("-custom_order")
                else:
                    qs = qs.order_by("custom_order")

            elif order_by == "unicef_id":
                qs = sorted(qs, key=lambda o: o.unicef_id, reverse=reverse)

            else:
                if reverse:
                    qs = qs.order_by(f"-{order_by}")
                else:
                    qs = qs.order_by(order_by)

        return qs


    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_programmes_by_sector(self, info, business_area_slug, year, **kwargs):
        filters = chart_filters_decoder(kwargs)
        sector_choice_mapping = chart_map_choices(Program.SECTOR_CHOICE)
        payment_items_qs: ExtendedQuerySetSequence = get_payment_items_for_dashboard(
            year, business_area_slug, filters, True
        )

        programs_ids = payment_items_qs.values_list("parent__program__id", flat=True)
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
    def resolve_chart_total_transferred_by_month(self, info, business_area_slug, year, **kwargs):
        payment_items_qs: ExtendedQuerySetSequence = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        months_and_amounts = (
            payment_items_qs.annotate(
                delivery_month=F("delivery_date__month"),
                total_delivered_cash=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_CASH),
                    output_field=DecimalField(),
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_VOUCHER),
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
            month_index = data_dict.get("delivery_month") - 1
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
