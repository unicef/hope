from collections import defaultdict
from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetPopulation,
)

TP_MIGRATION_MAPPING = {
    # tp.field: payment_plan.field
    # if value has internal_data__ will story into json
    "name": "name",
    "created_by": "created_by",
    "change_date": "status_date",
    "business_area": "business_area",
    "status": "status",
    "build_status": "build_status",
    "built_at": "built_at",
    "program": "program",
    "program_cycle": "program_cycle",
    "targeting_criteria": "targeting_criteria",
    "steficon_rule": "steficon_rule_targeting",
    "steficon_applied_date": "steficon_targeting_applied_date",
    "vulnerability_score_min": "vulnerability_score_min",
    "vulnerability_score_max": "vulnerability_score_max",
    "excluded_ids": "excluded_ids",
    "exclusion_reason": "exclusion_reason",
    "total_households_count": "total_households_count",
    "total_individuals_count": "total_individuals_count",
    "child_male_count": "male_children_count",
    "child_female_count": "female_children_count",
    "adult_male_count": "male_adults_count",
    "adult_female_count": "female_adults_count",
    "storage_file": "storage_file",
}
INTERNAL_DATA_FIELDS = {
    "ca_id": "internal_data__ca_id",
    "ca_hash_id": "internal_data__ca_hash_id",
    "sent_to_datahub": "internal_data__sent_to_datahub",
}

ALL_TP_MIGRATION_MAPPING = TP_MIGRATION_MAPPING.update(INTERNAL_DATA_FIELDS)


def map_tp_to_pp(tp: TargetPopulation) -> Dict[str, Any]:
    """helper function to map TargetPopulation to PaymentPlan fields"""
    payment_plan_data = defaultdict(dict)
    internal_data = defaultdict(dict)
    for tp_field, pp_field in ALL_TP_MIGRATION_MAPPING.items():
        tp_value = getattr(tp, tp_field, None)
        if tp_value:
            pp_field_list = pp_field.split("__")
            if len(pp_field_list) == 1:
                payment_plan_data[pp_field] = tp_value
            elif len(pp_field_list) == 2 and pp_field_list[0] == "internal_data":
                internal_data[pp_field_list[1]] = str(tp_value)  # type: ignore
    payment_plan_data["internal_data"] = internal_data
    return payment_plan_data


def tc_migrate_hh_ind_ids(tc: TargetingCriteria) -> Optional[TargetingCriteriaRule]:
    """migrate data 'household_ids' & 'individual_ids' from TargetingCriteria into TargetingCriteriaRule"""
    rules = tc.get_rules()
    if rules.count() > 1:
        print(f"**** Found more than one TargetingCriteriaRule for TargetingCriteria {str(tc.pk)}.")
    if first_rule := rules.first():
        if tc.household_ids:
            first_rule.household_ids = tc.household_ids
        if tc.individual_ids:
            first_rule.individual_ids = tc.individual_ids
        return first_rule
    return None


def migrate_tp_qs(tp_qs: QuerySet["TargetPopulation"]) -> None:
    new_payment_plans = []
    updated_payment_plans = []
    full_reduild_payment_plans = []  # full rebuild for PP in PREPARING status
    updated_tc_rules = []  # migrate TargetingCriteriaRule 'household_ids' & 'individual_ids'

    for tp in tp_qs:
        # migrate ind_ids and hh_ids
        tcr = tc_migrate_hh_ind_ids(tp.targeting_criteria)
        if tcr:
            updated_tc_rules.append(tcr)

        # update existing PaymentPlan
        existing_payment_plans = list(tp.payment_plans.all())
        if existing_payment_plans:
            for payment_plan in existing_payment_plans:
                payment_plan_data = map_tp_to_pp(tp)

                for field, value in payment_plan_data.items():
                    setattr(payment_plan, field, value)
                updated_payment_plans.append(payment_plan)
                # full rebuild for PREPARING Payment Plan
                if payment_plan.status == PaymentPlan.Status.PREPARING:
                    full_reduild_payment_plans.append(str(payment_plan.pk))
        else:
            # create new PaymentPlan
            payment_plan_data = map_tp_to_pp(tp)
            # TODO: populate more data like:
            # business_area, created_by, program_cycle, targeting_criteria, name,
            # status_date=timezone.now(), start_date=program_cycle.start_date, end_date=program_cycle.end_date,
            # status=PaymentPlan.Status.TP_OPEN,
            # build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            # built_at=timezone.now(),
            new_payment_plans.append(PaymentPlan(**payment_plan_data))

    if updated_payment_plans:
        PaymentPlan.objects.bulk_update(
            updated_payment_plans, list(TP_MIGRATION_MAPPING.values()) + ["internal_data"], 1000
        )
    if new_payment_plans:
        PaymentPlan.objects.bulk_create(new_payment_plans, 1000)

    if updated_tc_rules:
        TargetingCriteriaRule.objects.bulk_update(updated_tc_rules, ["household_ids", "individual_ids"], 1000)

    # rebuild Preparing Payment Plans
    if full_reduild_payment_plans:
        print(f" **** Found {len(full_reduild_payment_plans)} Payment Plan(s) in PREPARING status")
    for payment_plan_id in full_reduild_payment_plans:
        if pp := PaymentPlan.objects.filter(pk=payment_plan_id).first():
            PaymentPlanService(payment_plan=pp).full_rebuild()


def get_statistics() -> None:
    tp_qs_count = TargetPopulation.objects.all().count()
    pp_qs_count = PaymentPlan.objects.all().count()
    print("*=" * 50)
    print(f"TargetPopulation.objects : {tp_qs_count}")
    print(f"PaymentPlan.objects : {pp_qs_count}")
    print("*=" * 50)
    if tp_without_ba := TargetPopulation.objects.filter(business_area__isnull=True).count():
        print(f"##### Found {tp_without_ba} without BA")


def migrate_tp_into_pp(batch_size: int = 500) -> None:
    start_time = timezone.now()
    # queryset.model.__name__
    model_name = "TargetPopulation"

    print(f"*** Data Migration {model_name} ***\n", "*" * 60)
    get_statistics()

    for business_area in BusinessArea.objects.all().only("id", "name"):
        queryset = TargetPopulation.objects.filter(business_area_id=business_area.id).only(
            "id",
        )
        if queryset:
            print(f"Processing {queryset.count()} {model_name} for {business_area.name}.")

            list_ids = [str(obj_id) for obj_id in queryset.values_list("id", flat=True).iterator(chunk_size=batch_size)]
            page_count = 0
            total_count = len(list_ids)

            for i in range(0, total_count, batch_size):
                batch_ids = list_ids[i : i + batch_size]

                with transaction.atomic():
                    processing_qs = TargetPopulation.objects.filter(id__in=batch_ids).prefetch_related("payment_plans")
                    migrate_tp_qs(processing_qs)

                    page_count += 1
                if i % (batch_size * 10) == 0:
                    print(f"progress: migrated {page_count * batch_size}/{total_count} TPs.")

    # for pp in new_payment_plans:
    # prepare_payment_plan_task(str(pp.id))

    print(f"Completed in {timezone.now() - start_time}\n", "*" * 55)


# TODO:
# 1) Check if TargetingCriteria can has more that one rule > tc_migrate_hh_ind_ids()
# 2) add more fields for PaymentPlan create > new_payment_plans[]
# 3) add create Payments for all new_payment_plans[]
