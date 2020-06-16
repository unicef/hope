from django.db import transaction
from django.db.models import Q, F

from cash_assist_datahub.models import Session
from core.models import BusinessArea
from core.utils import nested_getattr
from cash_assist_datahub import models as ca_models
from program.models import CashPlan


class PullFromDatahubTask:

    MAPPING_CASH_PLAN_DICT = {
        "ca_id": "cash_plan_id",
        "status": "status",
        "total_undelivered_quantity": "total_undelivered_quantity",
        "total_delivered_quantity": "total_delivered_quantity",
        "total_entitled_quantity_revised": "total_entitled_quantity_revised",
        "total_entitled_quantity": "total_entitled_quantity",
        "payment_records_count": "payment_records_count",
        "total_persons_covered_revised": "total_persons_covered_revised",
        "total_persons_covered": "total_persons_covered",
        "validation_alerts_count": "validation_alerts_count",
        "down_payment": "down_payment",
        "funds_commitment": "funds_commitment",
        "vision_id": "vision_id",
        "assistance_through": "assistance_through",
        "assistance_measurement": "assistance_measurement",
        "delivery_type": "delivery_type",
        "program_mis_id": "program_mis_id",
        "comments": "comments",
        "coverage_duration": "coverage_duration",
        "dispersion_date": "dispersion_date",
        "end_date": "end_date",
        "start_date": "start_date",
        "distribution_level": "distribution_level",
        "name": "name",
        "status_date": "status_date",
    }
    MAPPING_PAYMENT_RECORD_DICT = {
        "delivery_date": "delivery_date",
        "delivered_quantity": "delivered_quantity",
        "entitlement_quantity": "entitlement_quantity",
        "currency": "currency",
        "delivery_type": "delivery_type",
        "entitlement_card_issue_date": "entitlement_card_issue_date",
        "entitlement_card_status": "entitlement_card_status",
        "entitlement_card_number": "entitlement_card_number",
        "target_population_mis_id": "target_population_id",
        "distribution_modality": "distribution_modality",
        "total_persons_covered": "total_persons_covered",
        "full_name": "full_name",
        "household_mis_id": "household_id",
        "ca_id": "ca_id",
        "ca_hash_id": "ca_hash_id",
        "status_date": "status_date",
        "status": "status",
    }


    @transaction.atomic(using="default")
    @transaction.atomic(using="cash_assist_datahub_ca")
    def execute(self):
        sessions = Session.objects.filter(status=Session.STATUS_READY)
        for session in sessions:
            self.copy_session(session)

    def build_arg_dict(self, model_object, mapping_dict):
        args = {}
        for key in mapping_dict:
            args[key] = nested_getattr(model_object, mapping_dict[key], None)
        return args
    def copy_session(self,session):
        self.copy_cash_plans(session)
        self.copy_payment_records(session)
    def copy_cash_plans(self,session):
        cash_plans = ca_models.CashPlan.objects.filter(session=session)
        for dh_cash_plan in cash_plans:
            cash_plan_args = self.build_arg_dict(
                dh_cash_plan, PullFromDatahubTask.MAPPING_CASH_PLAN_DICT
            )
            cash_plan = CashPlan(**cash_plan_args)
            cash_plan.business_area = BusinessArea.objects.get(code=dh_cash_plan.business_area)

    def copy_payment_records(self,session):
        pass