import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count

from sentry_sdk import configure_scope

from hct_mis_api.apps.cash_assist_datahub import models as ca_models
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.core.cache_keys import (
    PROGRAM_TOTAL_NUMBER_OF_HOUSEHOLDS_CACHE_KEY,
)
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.models import BusinessArea, CountryCodeMap
from hct_mis_api.apps.core.utils import build_arg_dict, clear_cache_for_dashboard_totals
from hct_mis_api.apps.payment.models import (
    CashPlan,
    DeliveryMechanism,
    PaymentRecord,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.handle_total_cash_in_households import (
    handle_total_cash_in_specific_households,
)
from hct_mis_api.apps.payment.utils import get_quantity_in_usd
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation

if TYPE_CHECKING:
    from hct_mis_api.apps.utils.models import AbstractSession


logger = logging.getLogger(__name__)


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
        "coverage_unit": "coverage_unit",
        "dispersion_date": "dispersion_date",
        "end_date": "end_date",  # TODO: what with CashPlan and ProgramCycle ???
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
        "head_of_household_id": "head_of_household_mis_id",
        "ca_id": "ca_id",
        "ca_hash_id": "ca_hash_id",
        "status": "status",
        "status_date": "status_date",
        "transaction_reference_id": "transaction_reference_id",
        "vision_id": "vision_id",
        "registration_ca_id": "registration_ca_id",
    }
    MAPPING_SERVICE_PROVIDER_DICT = {
        "ca_id": "ca_id",
        "full_name": "full_name",
        "short_name": "short_name",
        "vision_id": "vision_id",
    }

    def __init__(self, exchange_rates_client: Optional[ExchangeRates] = None) -> None:
        self.exchange_rates_client = exchange_rates_client or ExchangeRates()

    def execute(self) -> Dict[str, Union[int, List[Any]]]:
        grouped_session = Session.objects.values("business_area").annotate(count=Count("business_area"))
        ret: Dict[str, List] = {
            "skipped_due_failure": [],
            "successes": [],
            "failures": [],
        }
        grouped_session_count = 0
        remove_dashboard_cache = False
        for group in grouped_session:
            grouped_session_count += 1
            business_area = group.get("business_area")
            session_queryset = Session.objects.filter(business_area=business_area)
            # if any session in this business area fails omit other sessions in this business area
            if session_queryset.filter(status=Session.STATUS_FAILED).count() > 0:
                ret["skipped_due_failure"].append(business_area)
                continue
            sessions = session_queryset.filter(status=Session.STATUS_READY).order_by("-last_modified_date")
            for session in sessions:
                try:
                    self.copy_session(session)
                    ret["successes"].append(session.id)
                    remove_dashboard_cache = True
                except Exception as e:
                    logger.exception(e)
                    ret["failures"].append(session.id)
        if remove_dashboard_cache:
            clear_cache_for_dashboard_totals()
        return ret | {"grouped_session": grouped_session_count}

    def clear_cache(self, session: "AbstractSession") -> None:
        business_area = self.get_business_area_for_cash_assist_code(session.business_area)
        cache.delete_pattern(PROGRAM_TOTAL_NUMBER_OF_HOUSEHOLDS_CACHE_KEY.format(business_area.id, "*"))

    def copy_session(self, session: "AbstractSession") -> None:
        with configure_scope() as scope:
            scope.set_tag("session.ca", str(session.id))
            session.status = session.STATUS_PROCESSING
            session.save(update_fields=("status",))
            self.clear_cache(session)
            try:
                with transaction.atomic(), transaction.atomic(using="cash_assist_datahub_ca"):
                    self.copy_service_providers(session)
                    self.copy_programs(session)
                    self.copy_target_population(session)
                    self.copy_cash_plans(session)
                    self.copy_payment_records(session)
                    session.status = session.STATUS_COMPLETED
                    session.save(update_fields=("status",))
            except Exception as e:
                session.process_exception(e)
                session.save(
                    update_fields=(
                        "status",
                        "traceback",
                        "sentry_id",
                    )
                )
                raise

    def get_business_area_for_cash_assist_code(self, cash_assist_code: str) -> BusinessArea:
        return BusinessArea.objects.get(
            code=BusinessArea.cash_assist_to_code_mapping.get(cash_assist_code, cash_assist_code)
        )

    def copy_cash_plans(self, session: "AbstractSession") -> None:
        dh_cash_plans = ca_models.CashPlan.objects.filter(session=session)
        for dh_cash_plan in dh_cash_plans:
            cash_plan_args = build_arg_dict(dh_cash_plan, PullFromDatahubTask.MAPPING_CASH_PLAN_DICT)
            self.set_cash_plan_service_provider(cash_plan_args)
            cash_plan_args["business_area"] = self.get_business_area_for_cash_assist_code(dh_cash_plan.business_area)
            (
                cash_plan,
                created,
            ) = CashPlan.objects.update_or_create(ca_id=dh_cash_plan.cash_plan_id, defaults=cash_plan_args)

            if created:
                PaymentVerificationSummary.objects.create(payment_plan_obj=cash_plan)

                try:
                    if not cash_plan.exchange_rate:
                        cash_plan.exchange_rate = cash_plan.get_exchange_rate(self.exchange_rates_client)
                        cash_plan.save(update_fields=["exchange_rate"])
                    for usd_field in CashPlan.usd_fields:
                        setattr(
                            cash_plan,
                            usd_field,
                            get_quantity_in_usd(
                                amount=getattr(cash_plan, usd_field.removesuffix("_usd")),
                                currency=cash_plan.currency,
                                exchange_rate=cash_plan.exchange_rate,
                                currency_exchange_date=cash_plan.currency_exchange_date,
                            ),
                        )
                    cash_plan.save(update_fields=CashPlan.usd_fields)
                except Exception as e:
                    logger.exception(e)

    def set_cash_plan_service_provider(self, cash_plan_args: Dict) -> None:
        assistance_through = cash_plan_args.get("assistance_through")
        if not assistance_through:
            return
        service_provider = ServiceProvider.objects.filter(ca_id=assistance_through).first()
        if service_provider is None:
            return
        cash_plan_args["service_provider"] = service_provider

    def copy_payment_records(self, session: "AbstractSession") -> None:
        dh_payment_records = ca_models.PaymentRecord.objects.filter(session=session)
        household_ids = []
        for dh_payment_record in dh_payment_records:
            payment_record_args = build_arg_dict(
                dh_payment_record,
                PullFromDatahubTask.MAPPING_PAYMENT_RECORD_DICT,
            )
            payment_record_args["business_area"] = self.get_business_area_for_cash_assist_code(
                dh_payment_record.business_area
            )
            payment_record_args["service_provider"] = ServiceProvider.objects.get(
                ca_id=dh_payment_record.service_provider_ca_id
            )
            payment_record_args["parent"] = CashPlan.objects.get(ca_id=dh_payment_record.cash_plan_ca_id)
            payment_record_args["delivery_type"] = DeliveryMechanism.objects.get(
                name=payment_record_args["delivery_type"]
            )
            (
                payment_record,
                created,
            ) = PaymentRecord.objects.update_or_create(ca_id=dh_payment_record.ca_id, defaults=payment_record_args)
            try:
                for usd_field in PaymentRecord.usd_fields:
                    setattr(
                        payment_record,
                        usd_field,
                        get_quantity_in_usd(
                            amount=getattr(payment_record, usd_field.removesuffix("_usd")),
                            currency=payment_record.currency,
                            exchange_rate=payment_record.parent.exchange_rate,
                            currency_exchange_date=payment_record.parent.currency_exchange_date,
                            exchange_rates_client=self.exchange_rates_client,
                        ),
                    )
                payment_record.save(update_fields=PaymentRecord.usd_fields)
            except Exception as e:
                logger.exception(e)
            household_ids.append(payment_record.household_id)
            if payment_record.household and payment_record.parent and payment_record.parent.program:
                payment_record.household.programs.add(payment_record.parent.program)
        handle_total_cash_in_specific_households(household_ids)

    def copy_service_providers(self, session: "AbstractSession") -> None:
        dh_service_providers = ca_models.ServiceProvider.objects.filter(session=session)
        for dh_service_provider in dh_service_providers:
            service_provider_args = build_arg_dict(
                dh_service_provider,
                PullFromDatahubTask.MAPPING_SERVICE_PROVIDER_DICT,
            )
            service_provider_args["business_area"] = self.get_business_area_for_cash_assist_code(
                dh_service_provider.business_area
            )
            service_provider_args["country"] = CountryCodeMap.objects.get_iso3_code(dh_service_provider.country)
            ServiceProvider.objects.update_or_create(ca_id=dh_service_provider.ca_id, defaults=service_provider_args)

    def copy_programs(self, session: "AbstractSession") -> None:
        dh_programs = ca_models.Programme.objects.filter(session=session)
        programs = []
        for dh_program in dh_programs:
            program = Program.objects.get(id=dh_program.mis_id)
            program.ca_id = dh_program.ca_id
            program.ca_hash_id = dh_program.ca_hash_id
            programs.append(program)
        Program.objects.bulk_update(programs, ["ca_id", "ca_hash_id"])

    def copy_target_population(self, session: "AbstractSession") -> None:
        dh_target_populations = ca_models.TargetPopulation.objects.filter(session=session)
        target_populations = []
        for dh_target_population in dh_target_populations:
            target_population = TargetPopulation.objects.get(id=dh_target_population.mis_id)
            target_population.ca_id = dh_target_population.ca_id
            target_population.ca_hash_id = dh_target_population.ca_hash_id
            target_populations.append(target_population)
        TargetPopulation.objects.bulk_update(target_populations, ["ca_id", "ca_hash_id"])
