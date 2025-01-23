from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from hct_mis_api.apps.accountability.models import Message, Survey
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetPopulation,
)

# tp.field: payment_plan.field
# if value has internal_data__ will story into json
TP_MIGRATION_MAPPING = {
    "name": "name",
    "created_by": "created_by",
    "change_date": "status_date",
    "business_area": "business_area",
    "status": "status",
    "build_status": "build_status",
    "built_at": "built_at",
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
    # we need to store ID in case to migrate maybe data in future like Message or Survey
    "id": "internal_data__target_population_id",
}

ALL_TP_MIGRATION_MAPPING = TP_MIGRATION_MAPPING | INTERNAL_DATA_FIELDS

tp_status_to_pp_mapping = {
    TargetPopulation.STATUS_OPEN: PaymentPlan.Status.TP_OPEN,
    TargetPopulation.STATUS_LOCKED: PaymentPlan.Status.TP_LOCKED,
    TargetPopulation.STATUS_PROCESSING: PaymentPlan.Status.TP_PROCESSING,
    TargetPopulation.STATUS_STEFICON_WAIT: PaymentPlan.Status.TP_STEFICON_WAIT,
    TargetPopulation.STATUS_STEFICON_RUN: PaymentPlan.Status.TP_STEFICON_RUN,
    TargetPopulation.STATUS_STEFICON_COMPLETED: PaymentPlan.Status.TP_STEFICON_COMPLETED,
    TargetPopulation.STATUS_STEFICON_ERROR: PaymentPlan.Status.TP_STEFICON_ERROR,
    TargetPopulation.STATUS_SENDING_TO_CASH_ASSIST: PaymentPlan.Status.DRAFT,
    TargetPopulation.STATUS_READY_FOR_CASH_ASSIST: PaymentPlan.Status.DRAFT,
    TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE: PaymentPlan.Status.DRAFT,
    # TargetPopulation.STATUS_ASSIGNED: None,  # TP has created Payment Plan
}


def map_tp_to_pp(tp: TargetPopulation) -> Dict[str, Any]:
    """helper function to map TargetPopulation to PaymentPlan fields"""
    payment_plan_data = defaultdict(dict)
    internal_data = defaultdict(dict)

    for tp_field, pp_field in ALL_TP_MIGRATION_MAPPING.items():
        tp_value = getattr(tp, tp_field, None)
        if tp_value:
            pp_field_list = pp_field.split("__")
            if len(pp_field_list) == 1:
                # map TP and PP status
                if pp_field_list[0] == "status":
                    if tp_value == TargetPopulation.STATUS_ASSIGNED:
                        # for assigned TP just skip updating PP.status
                        continue
                    else:
                        tp_value = tp_status_to_pp_mapping.get(tp_value)

                payment_plan_data[pp_field] = tp_value
            # internal_data json
            elif len(pp_field_list) == 2 and pp_field_list[0] == "internal_data":
                internal_data[pp_field_list[1]] = str(tp_value)  # type: ignore
    payment_plan_data["internal_data"] = internal_data
    return payment_plan_data


def tc_migrate_hh_ind_ids(tc: TargetingCriteria) -> Tuple[Optional[TargetingCriteriaRule], bool]:
    """migrate data 'household_ids' & 'individual_ids' from TargetingCriteria into TargetingCriteriaRule"""
    # return TargetingCriteriaRule or None and bool new tcr to create
    # None, False OR first_rule, False
    rules = tc.get_rules()
    if rules.count() == 0:
        # create new one if HH or Ind ids and return new TargetingCriteriaRule, True
        if tc.individual_ids or tc.household_ids:
            # print("not found TargetingCriteriaRule for TargetingCriteria. Going to create a new one.")
            new_tcr = TargetingCriteriaRule(
                targeting_criteria=tc, household_ids=tc.household_ids, individual_ids=tc.individual_ids
            )
            return new_tcr, True
        return None, False

    if first_rule := rules.first():
        if tc.household_ids and tc.household_ids != first_rule.household_ids:
            first_rule.household_ids = tc.household_ids
        if tc.individual_ids and tc.individual_ids != first_rule.individual_ids:
            first_rule.individual_ids = tc.individual_ids
        return first_rule, False
    return None, False


def migrate_tp_qs(tp_qs: QuerySet["TargetPopulation"]) -> None:
    new_payment_plans = []
    update_payment_plans = []
    full_rebuild_payment_plans = []  # full rebuild for PP in PREPARING status
    update_tc_rules = []  # migrate TargetingCriteriaRule 'household_ids' & 'individual_ids'
    create_tc_rules = []

    tp_qs = tp_qs.prefetch_related("payment_plans", "targeting_criteria", "program_cycle")

    for tp in tp_qs:
        print(" ******** Processing TP ", str(tp.id))
        # migrate ind_ids and hh_ids
        if tp.targeting_criteria:
            tcr, create = tc_migrate_hh_ind_ids(tp.targeting_criteria)
            if tcr and not create:
                update_tc_rules.append(tcr)
            if tcr and create:
                create_tc_rules.append(tcr)

        # update existing PaymentPlan
        pp_count = 0
        existing_payment_plans = list(tp.payment_plans.filter(targeting_criteria__isnull=True))
        if existing_payment_plans:
            # if len(existing_payment_plans) > 1:
            # print(f"Found more then 1 PP for TP {str(tp.pk)}, {len(existing_payment_plans)} PPs")
            for payment_plan in existing_payment_plans:
                pp_count += 1
                payment_plan_data = map_tp_to_pp(tp)

                for field, value in payment_plan_data.items():
                    setattr(payment_plan, field, value)
                # create copy targeting_criteria for other PP from the same TP
                # like for follow up PPs and from Cash Assist maybe as well
                if pp_count > 1:
                    copy_new_target_criteria = PaymentPlanService.copy_target_criteria(tp.targeting_criteria)
                    payment_plan.targeting_criteria = copy_new_target_criteria
                # full rebuild for PREPARING Payment Plan
                if payment_plan.status == PaymentPlan.Status.PREPARING:
                    full_rebuild_payment_plans.append(str(payment_plan.pk))
                update_payment_plans.append(payment_plan)
        else:
            # skip create payments if build_status is failed
            # or set empty if no targeting_criteria
            if tp.build_status == TargetPopulation.BUILD_STATUS_FAILED:
                build_status = PaymentPlan.BuildStatus.BUILD_STATUS_FAILED
            elif tp.targeting_criteria:
                build_status = PaymentPlan.BuildStatus.BUILD_STATUS_PENDING
            else:
                build_status = None
            # create new PaymentPlan in no PP with tp.targeting_criteria
            payment_plan_data = map_tp_to_pp(tp)
            payment_plan_data["start_date"] = tp.program_cycle.start_date
            payment_plan_data["end_date"] = tp.program_cycle.end_date
            payment_plan_data["status"] = PaymentPlan.Status.TP_OPEN
            payment_plan_data["status_date"] = timezone.now()
            payment_plan_data["build_status"] = build_status
            payment_plan_data["built_at"] = timezone.now()
            if payment_plan_data.get("targeting_criteria") is None:
                #  create new empty targeting_criteria
                payment_plan_data["targeting_criteria"] = TargetingCriteriaFactory()
            # check if PaymentPlan exists for this targeting_criteria
            if not PaymentPlan.objects.filter(targeting_criteria=payment_plan_data["targeting_criteria"]).exists():
                # create new PaymentPlan if no any PaymentPlan with the targeting_criteria
                new_payment_plans.append(PaymentPlan(**payment_plan_data))

    if update_tc_rules:
        print("* processing update_tc_rules")
        TargetingCriteriaRule.objects.bulk_update(update_tc_rules, ["household_ids", "individual_ids"], 500)

    if create_tc_rules:
        print("** processing create_tc_rules")
        TargetingCriteriaRule.objects.bulk_create(create_tc_rules, 500)

    if update_payment_plans:
        print("*** processing update_payment_plans", len(update_payment_plans))
        PaymentPlan.objects.bulk_update(
            update_payment_plans, list(TP_MIGRATION_MAPPING.values()) + ["internal_data"], 500
        )

    if new_payment_plans:
        print("**** processing new_payment_plans")
        PaymentPlan.objects.bulk_create(new_payment_plans, 500)

    # rebuild Preparing Payment Plans
    if full_rebuild_payment_plans:
        print(f" ****** Found {len(full_rebuild_payment_plans)} Payment Plan(s) in PREPARING status")
        for payment_plan in PaymentPlan.objects.filter(pk__in=full_rebuild_payment_plans):
            PaymentPlanService(payment_plan=payment_plan).full_rebuild()
            payment_plan.status = PaymentPlan.Status.OPEN
            payment_plan.save()


def get_statistics(after_migration_status: bool = False) -> None:
    tp_qs_count = TargetPopulation.objects.count()
    pp_qs_count = PaymentPlan.objects.count()
    print("*=" * 50)
    print(f"TargetPopulation.objects : {tp_qs_count}")
    print(f"PaymentPlan.objects : {pp_qs_count}")
    print(
        f"TPs with Statuses Not assigned to PP: {TargetPopulation.objects.exclude(status=TargetPopulation.STATUS_ASSIGNED).count()}"
    )
    print("*=" * 50)
    if tp_without_ba := TargetPopulation.objects.filter(business_area__isnull=True).count():
        print(f"##### Found {tp_without_ba} without BA")

    if after_migration_status:
        not_migrated_tps = TargetPopulation.objects.exclude(
            targeting_criteria_id__in=PaymentPlan.objects.filter(targeting_criteria__isnull=False).values_list(
                "targeting_criteria_id", flat=True
            )
        ).filter(payment_plans__targeting_criteria__isnull=True)
        not_migrated_tps_list = []
        if not_migrated_tps.exists():
            for tp in not_migrated_tps:
                pp_qs = PaymentPlan.objects.filter(
                    business_area=tp.business_area,
                    internal_data__has_key="target_population_id",
                    internal_data__target_population_id=str(tp.id),
                )
                if pp_qs.exists():
                    continue
                not_migrated_tps_list.append(tp)

        if not_migrated_tps_list:
            print(f"Found {not_migrated_tps.count()} TargetPopulation objects didn't migrated into PaymentPlan.")
            for tp in not_migrated_tps_list:
                print(
                    f"### TargetPopulation ID: {tp.id}, status: {tp.status}, targeting_criteria: {tp.targeting_criteria_id}"
                )
        else:
            print("All TargetPopulation's targeting_criteria had assigned to PaymentPlans.")

        pp_without_targeting_criteria = PaymentPlan.objects.filter(targeting_criteria__isnull=True).order_by(
            "business_area"
        )
        if pp_without_targeting_criteria:
            print("#### Found PaymentPlan without targeting_criteria ", pp_without_targeting_criteria.count())
            for pp in pp_without_targeting_criteria:
                print(
                    pp.unicef_id,
                    "Status:",
                    pp.status,
                    f"(build status: {pp.build_status})",
                    "BA:",
                    pp.business_area.name,
                    "Program:",
                    pp.program_cycle.program.name,
                )


def get_payment_plan_id_from_tp_id(business_area_id: str, target_population_id: str) -> Optional[str]:
    for pp in PaymentPlan.all_objects.filter(business_area_id=business_area_id):
        if pp.internal_data.get("target_population_id") == target_population_id:
            return str(pp.pk)
    # print(f"****** Not found PaymentPlan for old target_population_id: {target_population_id}, BA: {business_area_id}")
    # just return None if no data
    return None


def migrate_message_and_survey(list_ids: List[str], model: Any, business_area_id: str) -> List:
    objects_to_update = []

    for obj_id in list_ids:
        obj = model.objects.get(pk=obj_id)
        if obj.target_population_id and obj.target_population.payment_plans.first():
            obj.payment_plan_id = str(obj.target_population.payment_plans.first().id)
            objects_to_update.append(obj)
        if obj.target_population_id and not obj.target_population.payment_plans.first():
            # find new migrated PP by payment_plan.internal_data["target_population_id"]
            payment_plan_id: Optional[str] = get_payment_plan_id_from_tp_id(
                business_area_id, str(obj.target_population_id)
            )
            if payment_plan_id:
                obj.payment_plan_id = payment_plan_id
                objects_to_update.append(obj)

    return objects_to_update


def create_payments_for_pending_payment_plans() -> None:
    from django.db import transaction
    from django.utils import timezone

    from hct_mis_api.apps.core.models import BusinessArea
    from hct_mis_api.apps.payment.models import PaymentPlan
    from hct_mis_api.apps.payment.services.payment_plan_services import (
        PaymentPlanService,
    )

    """
    step 2 create Payments for BUILD_STATUS_PENDING PaymentPlans
    """
    start_time = timezone.now()
    print("*** Create Payments for BUILD_STATUS_PENDING PaymentPlans ***\n", "*" * 60)
    for business_area in BusinessArea.objects.only("id", "name"):
        build_payment_plans_qs = PaymentPlan.objects.filter(
            build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING,
            business_area_id=business_area.id,
            targeting_criteria__isnull=False,
        ).only("id")
        if build_payment_plans_qs.exists():
            print(f"\n *** Processing {business_area.name}.")
            print("Create payments for New Created Payment Plans: ", build_payment_plans_qs.count())
            for payment_plan in build_payment_plans_qs:
                print(f".... processing with PP: {payment_plan.unicef_id} - {payment_plan.name}")
                with transaction.atomic():
                    try:
                        payment_plan.build_status_building()
                        payment_plan.save(update_fields=("build_status", "built_at"))
                        PaymentPlanService.create_payments(payment_plan)
                        payment_plan.update_population_count_fields()
                        payment_plan.build_status_ok()
                        payment_plan.save(update_fields=("build_status", "built_at"))
                    except Exception as e:
                        payment_plan.build_status_failed()
                        payment_plan.save(update_fields=("build_status", "built_at"))
                        print("Create payments Error", str(e))
                print(f"Finished with PP: {payment_plan.unicef_id}")
    print(f"Completed in {timezone.now() - start_time}\n", "*" * 55)


def migrate_tp_into_pp(batch_size: int = 1) -> None:
    """
    step 1 migrate TP>PP
    """
    start_time = timezone.now()
    # queryset.model.__name__
    model_name = "TargetPopulation"

    print(f"*** Data Migration {model_name} ***\n", "*" * 60)
    get_statistics()

    for business_area in BusinessArea.objects.only("id", "name"):
        queryset = TargetPopulation.objects.filter(business_area_id=business_area.id).only(
            "id",
        )
        if queryset:
            print(f"\n   ***   Processing {queryset.count()} {model_name} for {business_area.name}.")

            list_ids = [str(obj_id) for obj_id in queryset.values_list("id", flat=True).iterator(chunk_size=batch_size)]
            page_count = 0
            total_count = len(list_ids)

            for i in range(0, total_count, batch_size):
                with transaction.atomic():
                    batch_ids = list_ids[i : i + batch_size]
                    processing_qs = TargetPopulation.objects.filter(id__in=batch_ids)
                    migrate_tp_qs(processing_qs)

                    page_count += 1
                    print(f"Progress: {page_count}/{-(-total_count // batch_size)} page(s) migrated.")

                build_payment_plans_qs = PaymentPlan.objects.filter(
                    build_status=PaymentPlan.BuildStatus.BUILD_STATUS_PENDING, business_area_id=business_area.id
                )
                if build_payment_plans_qs.exists():
                    print(f"Payments for {build_payment_plans_qs.count()} Payment Plans will create later")

        # Migrate Message & Survey
        for model in (Message, Survey):
            print(f"Processing with migration {model.__name__} objects.")
            model_qs = model.objects.filter(business_area_id=business_area.id, target_population__isnull=False).only(
                "id"
            )
            list_ids = [str(obj_id) for obj_id in model_qs.values_list("id", flat=True).iterator(chunk_size=batch_size)]
            with transaction.atomic():
                update_list = migrate_message_and_survey(list_ids, model, str(business_area.id))
                model.objects.bulk_update(update_list, ["payment_plan_id"], 1000)

    print(f"Completed in {timezone.now() - start_time}\n", "*" * 55)
    get_statistics(after_migration_status=True)
