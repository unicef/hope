import graphene
from django.db.models import Count, Q, Sum

from hct_mis_api.apps.account.permissions import (
    Permissions,
)
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.utils import (
    chart_create_filter_query,
    chart_filters_decoder,
    chart_get_filtered_qs,
    chart_map_choices,
    chart_permission_decorator,
)
from hct_mis_api.apps.core.utils import (
    sum_lists_with_values,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.models import (
    PaymentRecord,
    PaymentVerification,
)
from hct_mis_api.apps.payment.utils import get_payment_records_for_dashboard
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    SectionTotalNode,
    TableTotalCashTransferred,
)

INDIVIDUALS_CHART_LABELS = [
    "Females 0-5",
    "Females 6-11",
    "Females 12-17",
    "Females 18-59",
    "Females 60+",
    "Males 0-5",
    "Males 6-11",
    "Males 12-17",
    "Males 18-59",
    "Males 60+",
]


class ChartPaymentVerification(ChartDetailedDatasetsNode):
    households = graphene.Int()
    average_sample_size = graphene.Float()


class ChartGrievanceTicketsNode(ChartDatasetNode):
    total_number_of_grievances = graphene.Int()
    total_number_of_feedback = graphene.Int()
    total_number_of_open_sensitive = graphene.Int()


class Query(graphene.ObjectType):
    section_households_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_individuals_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_child_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_payment_verification = graphene.Field(
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
    chart_total_transferred_cash_by_country = graphene.Field(
        ChartDetailedDatasetsNode, year=graphene.Int(required=True)
    )

    chart_grievances = graphene.Field(
        ChartGrievanceTicketsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        administrative_area=graphene.String(required=False),
    )

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_households_reached(self, info, business_area_slug, year, **kwargs):
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        return {"total": payment_records_qs.values_list("household", flat=True).distinct().count()}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_individuals_reached(self, info, business_area_slug, year, **kwargs):
        households_individuals_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        individuals_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_individuals_params)
            .distinct("household__id")
        )
        return {"total": sum(sum_lists_with_values(individuals_counts, len(households_individuals_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_child_reached(self, info, business_area_slug, year, **kwargs):
        households_child_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
        ]
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        household_child_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_child_params)
            .distinct("household__id")
        )
        return {"total": sum(sum_lists_with_values(household_child_counts, len(households_child_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_reached_by_age_and_gender(self, info, business_area_slug, year, **kwargs):
        households_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]

        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        household_child_counts = (
            payment_records_qs.select_related("household").values_list(*households_params).distinct("household__id")
        )
        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_with_disability_reached_by_age(self, info, business_area_slug, year, **kwargs):
        households_params_with_disability = [
            "household__female_age_group_0_5_disabled_count",
            "household__female_age_group_6_11_disabled_count",
            "household__female_age_group_12_17_disabled_count",
            "household__female_age_group_18_59_disabled_count",
            "household__female_age_group_60_disabled_count",
            "household__male_age_group_0_5_disabled_count",
            "household__male_age_group_6_11_disabled_count",
            "household__male_age_group_12_17_disabled_count",
            "household__male_age_group_18_59_disabled_count",
            "household__male_age_group_60_disabled_count",
        ]
        households_params_total = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]

        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        # aggregate with distinct by household__id is not possible
        households_with_disability_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_params_with_disability)
            .distinct("household__id")
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_params_total)
            .distinct("household__id")
        )
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment_verification(self, info, business_area_slug, year, **kwargs):
        filters = chart_filters_decoder(kwargs)
        status_choices_mapping = chart_map_choices(PaymentVerification.STATUS_CHOICES)
        payment_verifications = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={"payment_record__business_area__slug": business_area_slug},
            additional_filters={
                **chart_create_filter_query(
                    filters,
                    program_id_path="payment_record__cash_plan__program__id",
                    administrative_area_path="payment_record__household__admin_area",
                )
            },
            year_filter_path="payment_record__delivery_date",
        )

        verifications_by_status = payment_verifications.values("status").annotate(count=Count("status"))
        verifications_by_status_dict = {x.get("status"): x.get("count") for x in verifications_by_status}
        dataset = [verifications_by_status_dict.get(status, 0) for status in status_choices_mapping.keys()]
        try:
            all_verifications = sum(dataset)
            dataset_percentage = [data / all_verifications for data in dataset]
        except ZeroDivisionError:
            dataset_percentage = [0] * len(status_choices_mapping.values())
        dataset_percentage_done = [
            {"label": status, "data": [dataset_percentage_value]}
            for (dataset_percentage_value, status) in zip(dataset_percentage, status_choices_mapping.values())
        ]

        samples_count = payment_verifications.distinct("payment_record").count()
        all_payment_records_for_created_verifications = (
            PaymentRecord.objects.filter(
                cash_plan__in=payment_verifications.distinct("cash_plan_payment_verification__cash_plan").values_list(
                    "cash_plan_payment_verification__cash_plan", flat=True
                )
            )
            .filter(status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0)
            .count()
        )
        if samples_count == 0 or all_payment_records_for_created_verifications == 0:
            average_sample_size = 0
        else:
            average_sample_size = samples_count / all_payment_records_for_created_verifications
        return {
            "labels": ["Payment Verification"],
            "datasets": dataset_percentage_done,
            "households": payment_verifications.distinct("payment_record__household").count(),
            "average_sample_size": average_sample_size,
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_volume_by_delivery_mechanism(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        volume_by_delivery_type = payment_records.values("delivery_type").annotate(volume=Sum("delivered_quantity_usd"))
        labels = []
        data = []
        for volume_dict in volume_by_delivery_type:
            if volume_dict.get("volume"):
                labels.append(volume_dict.get("delivery_type"))
                data.append(volume_dict.get("volume"))

        return {"labels": labels, "datasets": [{"data": data}]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        ).aggregate(
            successful=Count("id", filter=~Q(status=PaymentRecord.STATUS_ERROR)),
            unsuccessful=Count("id", filter=Q(status=PaymentRecord.STATUS_ERROR)),
        )

        dataset = [
            {
                "data": [
                    payment_records.get("successful", 0),
                    payment_records.get("unsuccessful", 0),
                ]
            }
        ]
        return {"labels": ["Successful Payments", "Unsuccessful Payments"], "datasets": dataset}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_total_transferred(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(year, business_area_slug, chart_filters_decoder(kwargs))
        return {"total": payment_records.aggregate(Sum("delivered_quantity_usd"))["delivered_quantity_usd__sum"]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_table_total_cash_transferred_by_administrative_area(self, info, business_area_slug, year, **kwargs):
        if business_area_slug == "global":
            return None
        order = kwargs.pop("order", None)
        order_by = kwargs.pop("order_by", None)
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        admin_areas = (
            Area.objects.filter(
                area_type__area_level=2,
                household__payment_records__in=payment_records,
            )
            .distinct()
            .annotate(total_transferred=Sum("household__payment_records__delivered_quantity_usd"))
            .annotate(num_households=Count("household", distinct=True))
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
    def resolve_chart_total_transferred_cash_by_country(self, info, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(year, "global", {}, True)

        countries_and_amounts = (
            payment_records.values("business_area__name")
            .order_by("business_area__name")
            .annotate(
                total_delivered_cash=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_CASH)
                )
            )
            .annotate(
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_VOUCHER)
                )
            )
        )

        labels = []
        cash_transferred = []
        voucher_transferred = []
        total_transferred = []
        for data_dict in countries_and_amounts:
            labels.append(data_dict.get("business_area__name"))
            cash_transferred.append(data_dict.get("total_delivered_cash") or 0)
            voucher_transferred.append(data_dict.get("total_delivered_voucher") or 0)
            total_transferred.append(cash_transferred[-1] + voucher_transferred[-1])

        datasets = [
            {"label": "Actual cash transferred", "data": cash_transferred},
            {"label": "Actual voucher transferred", "data": voucher_transferred},
            {"label": "Total transferred", "data": total_transferred},
        ]

        return {"labels": labels, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_grievances(self, info, business_area_slug, year, **kwargs):
        grievance_tickets = chart_get_filtered_qs(
            GrievanceTicket,
            year,
            business_area_slug_filter={"business_area__slug": business_area_slug},
        )

        filters = chart_filters_decoder(kwargs)
        if filters.get("administrative_area") is not None:
            try:
                grievance_tickets = grievance_tickets.filter(
                    admin2=Area.objects.get(id=filters.get("administrative_area"))
                )
            except Area.DoesNotExist:
                pass

        grievance_status_labels = [
            "Resolved",
            "Unresolved",
            "Unresolved for longer than 30 days",
            "Unresolved for longer than 60 days",
        ]

        days_30_from_now = datetime.date.today() - datetime.timedelta(days=30)
        days_60_from_now = datetime.date.today() - datetime.timedelta(days=60)

        feedback_categories = [
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        ]
        all_open_tickets = grievance_tickets.filter(~Q(status=GrievanceTicket.STATUS_CLOSED))
        all_closed_tickets = grievance_tickets.filter(status=GrievanceTicket.STATUS_CLOSED)

        datasets = [
            {
                "data": [
                    all_closed_tickets.count(),  # Resolved
                    all_open_tickets.filter(
                        created_at__gte=days_30_from_now,
                    ).count(),  # Unresolved less than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_30_from_now,
                        created_at__gte=days_60_from_now,
                    ).count(),  # Unresolved for longer than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_60_from_now
                    ).count(),  # Unresolved for longer than 60 days
                ]
            },
        ]
        return {
            "labels": grievance_status_labels,
            "datasets": datasets,
            "total_number_of_grievances": grievance_tickets.exclude(category__in=feedback_categories).count(),
            "total_number_of_feedback": grievance_tickets.filter(category__in=feedback_categories).count(),
            "total_number_of_open_sensitive": all_open_tickets.filter(
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            ).count(),
        }
