from collections import defaultdict
from typing import Any, Dict, Optional

from django.db import transaction

from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetPopulation,
)


def migrate_tp_into_pp() -> None:
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
        """helper function to map TargetPopulation to PaymentPlan fields."""
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
        if first_rule := tc.rules.first():
            if tc.household_ids:
                first_rule.household_ids = tc.household_ids
            if tc.individual_ids:
                first_rule.individual_ids = tc.individual_ids
            return first_rule
        return None

    with transaction.atomic():
        tp_qs = TargetPopulation.objects.prefetch_related("payment_plans")
        new_payment_plans = []
        updated_payment_plans = []
        full_reduild_payment_plans = []
        updated_tc_rules = []

        for tp in tp_qs:
            tcr = tc_migrate_hh_ind_ids(tp.targeting_criteria)
            if tcr:
                updated_tc_rules.append(tcr)

            existing_payment_plans = list(tp.payment_plans.all())
            if existing_payment_plans:
                for pp in existing_payment_plans:
                    payment_plan_data = map_tp_to_pp(tp)
                    for field, value in payment_plan_data.items():
                        setattr(pp, field, value)
                    updated_payment_plans.append(pp)
                    if pp.status == PaymentPlan.Status.PREPARING:
                        full_reduild_payment_plans.append(str(pp.pk))
            else:
                # create new PaymentPlan
                payment_plan_data = map_tp_to_pp(tp)
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
        for payment_plan_id in full_reduild_payment_plans:
            if pp := PaymentPlan.objects.filter(pk=payment_plan_id).first():
                PaymentPlanService(payment_plan=pp).full_rebuild()
