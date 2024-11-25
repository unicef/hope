from collections import defaultdict

from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.targeting.models import TargetPopulation


def migrate_tp_into_pp() -> None:
    TP_MIGRATION_MAPPING = {
        # tp.field: payment_plan.field
        # if value has internal_data__ will story into json
        "name": "name",
        "ca_id": "internal_data__ca_id",
        "ca_hash_id": "internal_data__ca_hash_id",
        "created_by": "created_by",
        "change_date": "status_date",
        "business_area": "business_area",
        "status": "status",
        "build_status": "build_status",
        "built_at": "built_at",
        "program": "program",
        "program_cycle": "program_cycle",
        "targeting_criteria": "targeting_criteria",
        "sent_to_datahub": "internal_data__sent_to_datahub",
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

    # TODO: migrate hh_ids, ind_ids into rule hh_ids, ind_ids!

    # per BA;
    for tp in TargetPopulation.objects.all():
        for pp in tp.payment_plans.all():
            internal_data = defaultdict(dict)

            for tp_field, pp_field in TP_MIGRATION_MAPPING.items():
                tp_value = getattr(tp, tp_field, None)

                if tp_value:
                    pp_field_list = pp_field.split("__")
                    if len(pp_field_list) == 1:
                        setattr(pp, pp_field, tp_value)
                    if len(pp_field_list) == 2 and pp_field_list[0] == internal_data:
                        internal_data[pp_field_list[1]] = str(tp_value)

                    setattr(pp, "internal_data", internal_data)

            pp.save()

        # if no PP create new PaymentPlan
        payment_plan = PaymentPlan()
        for tp_field, pp_field in TP_MIGRATION_MAPPING.items():
            tp_value = getattr(tp, tp_field, None)

            if tp_value:
                pp_field_list = pp_field.split("__")
                if len(pp_field_list) == 1:
                    setattr(payment_plan, pp_field, tp_value)
                if len(pp_field_list) == 2 and pp_field_list[0] == internal_data:
                    internal_data[pp_field_list[1]] = str(tp_value)

                setattr(payment_plan, "internal_data", internal_data)

        payment_plan.save()
