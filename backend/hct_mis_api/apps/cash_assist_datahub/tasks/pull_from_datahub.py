from django.db import transaction
from django.db.models import Q, F

from cash_assist_datahub.models import Session
from core.models import BusinessArea
from core.utils import nested_getattr
from cash_assist_datahub import models as ca_models
from payment.models import PaymentRecord, ServiceProvider
from program.models import CashPlan, Program
from targeting.models import TargetPopulation


class PullFromDatahubTask:

    MAPPING_CASH_PLAN_DICT = {
        "ca_id": "cash_plan_id",
        "ca_hash_id": "cash_plan_hash_id",
        "status": "status",
        "total_undelivered_quantity": "total_undelivered_quantity",
        "total_delivered_quantity": "total_delivered_quantity",
        "total_entitled_quantity_revised": "total_entitled_quantity_revised",
        "total_entitled_quantity": "total_entitled_quantity",
        "total_persons_covered_revised": "total_persons_covered_revised",
        "total_persons_covered": "total_persons_covered",
        "validation_alerts_count": "validation_alerts_count",
        "down_payment": "down_payment",
        "funds_commitment": "funds_commitment",
        "vision_id": "vision_id",
        "assistance_through": "assistance_through",
        "assistance_measurement": "assistance_measurement",
        "delivery_type": "delivery_type",
        "comments": "comments",
        "coverage_duration": "coverage_duration",
        "dispersion_date": "dispersion_date",
        "end_date": "end_date",
        "start_date": "start_date",
        "distribution_level": "distribution_level",
        "name": "name",
        "status_date": "status_date",
        "program_id": "program_mis_id",
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
        "target_population_id": "target_population_mis_id",
        "distribution_modality": "distribution_modality",
        "total_persons_covered": "total_persons_covered",
        "full_name": "full_name",
        "household_id": "household_mis_id",
        "ca_id": "ca_id",
        "ca_hash_id": "ca_hash_id",
        "status_date": "status_date",
        "transaction_reference_id": "transaction_reference_id",
        "vision_id": "vision_id",
    }
    MAPPING_SERVICE_PROVIDER_DICT = {
        "ca_id": "ca_id",
        "full_name": "full_name",
        "short_name": "short_name",
        "country": "country",
        "vision_id": "vision_id",
    }

    @transaction.atomic(using="default")
    @transaction.atomic(using="cash_assist_datahub_ca")
    def execute(self):
        sessions = Session.objects.filter(status=Session.STATUS_READY)
        for session in sessions:
            self.copy_session(session)

    def build_arg_dict(self, model_object, mapping_dict):
        return {key: nested_getattr(model_object, mapping_dict[key]) for key in mapping_dict}

    def copy_session(self, session):
        session.status = session.STATUS_PROCESSING
        session.save()
        self.copy_service_providers(session)
        programs = self.copy_programs_ids(session)
        Program.objects.bulk_update(programs, ["ca_id", "ca_hash_id"])
        TargetPopulation.objects.bulk_update(self.copy_target_population_ids(session), ["ca_id", "ca_hash_id"])
        self.copy_cash_plans(session)
        self.copy_payment_records(session)
        session.status = session.STATUS_COMPLETED
        session.save()

    def copy_cash_plans(self, session):
        dh_cash_plans = ca_models.CashPlan.objects.filter(session=session)
        for dh_cash_plan in dh_cash_plans:
            cash_plan_args = self.build_arg_dict(dh_cash_plan, PullFromDatahubTask.MAPPING_CASH_PLAN_DICT)
            cash_plan_args["business_area"] = BusinessArea.objects.get(code=dh_cash_plan.business_area)
            (cash_plan, created,) = CashPlan.objects.update_or_create(
                ca_id=dh_cash_plan.cash_plan_id, defaults=cash_plan_args
            )

    def copy_payment_records(self, session):
        dh_payment_records = ca_models.PaymentRecord.objects.filter(session=session)
        for dh_payment_record in dh_payment_records:
            payment_record_args = self.build_arg_dict(
                dh_payment_record, PullFromDatahubTask.MAPPING_PAYMENT_RECORD_DICT,
            )

            payment_record_args["business_area"] = BusinessArea.objects.get(code=dh_payment_record.business_area)
            payment_record_args["service_provider"] = ServiceProvider.objects.get(
                ca_id=dh_payment_record.service_provider_ca_id
            )
            (payment_record, created,) = PaymentRecord.objects.update_or_create(
                ca_id=dh_payment_record.ca_id, defaults=payment_record_args
            )

    def copy_service_providers(self, session):
        dh_service_providers = ca_models.ServiceProvider.objects.filter(session=session)
        for dh_service_provider in dh_service_providers:
            service_provider_args = self.build_arg_dict(
                dh_service_provider, PullFromDatahubTask.MAPPING_SERVICE_PROVIDER_DICT,
            )
            service_provider_args["business_area"] = BusinessArea.objects.get(code=dh_service_provider.business_area)
            (service_provider, created,) = ServiceProvider.objects.update_or_create(
                ca_id=dh_service_provider.ca_id, defaults=service_provider_args
            )

    def copy_programs_ids(self, session):
        dh_programs = ca_models.Programme.objects.filter(session=session)
        import ipdb;ipdb.set_trace()
        programs = []
        for dh_program in dh_programs:
            program = Program.objects.get(id=dh_program.mis_id)
            program.ca_id = dh_program.ca_id
            program.ca_hash_id = dh_program.ca_hash_id
            programs.append(program)
        return programs

    def copy_target_population_ids(self, session):
        dh_target_populations = ca_models.TargetPopulation.objects.filter(session=session)

        for dh_target_population in dh_target_populations:
            target_population = TargetPopulation.objects.get(id=dh_target_population.mis_id)
            target_population.ca_id = dh_target_population.ca_id
            target_population.ca_hash_id = dh_target_population.ca_hash_id
            yield target_population
