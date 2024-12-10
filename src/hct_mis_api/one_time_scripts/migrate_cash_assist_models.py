from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from hct_mis_api.apps.grievance.models import (
    TicketComplaintDetails,
    TicketSensitiveDetails,
)
from hct_mis_api.apps.payment.models import (
    CashPlan,
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.targeting.models import TargetPopulation


def get_status(status: str) -> str:
    mapping = {"Transaction Successful": "Distribution Successful"}
    return mapping.get(status, status)


def migrate_cash_plan_to_payment_plan() -> None:
    content_type_for_payment_plan = ContentType.objects.get_for_model(PaymentPlan)
    content_type_for_cash_plan = ContentType.objects.get_for_model(CashPlan)
    content_type_for_payment_record = ContentType.objects.get_for_model(PaymentRecord)

    print("**Migrating Cash Plan to Payment Plan**")
    delivery_type_to_obj = {obj.name: obj for obj in DeliveryMechanism.objects.all()}

    print("Creating FinancialServiceProviders")
    for sp in ServiceProvider.objects.filter(is_migrated_to_payment_plan=False):
        print(f"\nProcessing Service Provider {sp}")
        if not sp.cash_plans.exists():
            print(f"Service provider {sp} has no cash plans")
            continue

        if FinancialServiceProvider.objects.filter(vision_vendor_number=sp.vision_id).exists():
            print(f"FinancialServiceProvider with vision_id {sp.vision_id} already exists")
            continue

        if not sp.vision_id:
            raise ValueError(f"Service Provider {sp} does not have vision_id")

        delivery_mechanisms = set(sp.cash_plans.all().values_list("delivery_type", flat=True))

        fsp = FinancialServiceProvider.objects.create(
            name=sp.full_name,
            vision_vendor_number=sp.vision_id,
            communication_channel="API",
            internal_data={
                "is_cash_assist": True,
                "business_area": sp.business_area.slug,
                "country": sp.country,
                "ca_id": sp.ca_id,
                "short_name": sp.short_name,
            },
        )
        fsp.delivery_mechanisms.set([delivery_type_to_obj[dt] for dt in delivery_mechanisms])
        sp.is_migrated_to_payment_plan = True
        sp.save(update_fields=["is_migrated_to_payment_plan"])

    fsp_vision_vendor_number_to_obj = {obj.vision_vendor_number: obj for obj in FinancialServiceProvider.objects.all()}

    dm_cash = delivery_type_to_obj["Cash"]

    cash_plans = CashPlan.objects.filter(is_migrated_to_payment_plan=False)
    print(f"Total Cash Plans to migrate: {cash_plans.count()}")
    cp_count = cash_plans.count()
    cp_i = 0
    for cp in cash_plans.iterator(chunk_size=50):
        if cp_i % 50 == 0:
            print(f"Processing cash plan {cp_i}/{cp_count}")
        cp_i += 1
        with transaction.atomic():
            if not cp.payment_items.exists():
                continue

            # get target populations from payment records
            target_populations = cp.payment_items.values_list("target_population", flat=True).distinct()
            tp_counter = 0
            # for each target population create a payment plan within tp.payment_cycle
            for tp_id in target_populations:
                tp = TargetPopulation.objects.get(id=tp_id)
                payment_records = cp.payment_items.filter(target_population=tp)
                first_record = payment_records.first()
                if first_record.delivery_type:
                    delivery_mechanism = delivery_type_to_obj[first_record.delivery_type.name]
                else:
                    delivery_mechanism = dm_cash
                currency = first_record.currency

                # create payment plan
                pp = PaymentPlan.objects.create(
                    status="FINISHED",
                    name=tp.name,
                    business_area_id=tp.business_area.id,
                    created_by_id=tp.created_by.id,
                    target_population_id=tp.id,
                    program_cycle_id=tp.program_cycle.id,
                    currency=currency,
                    dispersion_start_date=cp.start_date or tp.program_cycle.start_date,
                    dispersion_end_date=cp.dispersion_date or tp.program_cycle.end_date,
                    start_date=cp.start_date or tp.program_cycle.start_date,
                    end_date=cp.end_date or tp.program_cycle.end_date,
                    status_date=cp.status_date,
                    exchange_rate=cp.exchange_rate,
                    total_entitled_quantity=cp.total_entitled_quantity,
                    total_entitled_quantity_usd=cp.total_entitled_quantity_usd,
                    total_entitled_quantity_revised=cp.total_entitled_quantity_revised,
                    total_entitled_quantity_revised_usd=cp.total_entitled_quantity_revised_usd,
                    total_delivered_quantity=cp.total_delivered_quantity,
                    total_delivered_quantity_usd=cp.total_delivered_quantity_usd,
                    total_undelivered_quantity=cp.total_undelivered_quantity,
                    total_undelivered_quantity_usd=cp.total_undelivered_quantity_usd,
                    is_cash_assist=True,
                    internal_data={
                        "name": cp.name,
                        "ca_hash_id": str(cp.ca_hash_id),
                        "distribution_level": cp.distribution_level,
                        "coverage_duration": cp.coverage_duration,
                        "coverage_unit": cp.coverage_unit,
                        "comments": cp.comments,
                        "assistance_measurement": cp.assistance_measurement,
                        "assistance_through": cp.assistance_through,
                        "vision_id": cp.vision_id,
                        "funds_commitment": cp.funds_commitment,
                        "down_payment": cp.down_payment,
                        "validation_alerts_count": cp.validation_alerts_count,
                        "total_persons_covered": cp.total_persons_covered,
                        "total_persons_covered_revised": cp.total_persons_covered_revised,
                    },
                )
                pp.created_at = cp.created_at
                pp.unicef_id = cp.ca_id
                pp.save(update_fields=["unicef_id", "created_at"])
                pp.update_population_count_fields()

                financial_service_provider = fsp_vision_vendor_number_to_obj.get(cp.service_provider.vision_id)
                if not financial_service_provider:
                    raise ValueError(
                        f"FinancialServiceProvider not found for vision_id: {first_record.service_provider.vision_id}"
                        f"Cash Plan: {cp}"
                        f"Record: {first_record}"
                        f"Service Provider: {first_record.service_provider}"
                    )

                dmppp = DeliveryMechanismPerPaymentPlan.objects.create(
                    payment_plan_id=pp.id,
                    delivery_mechanism_id=delivery_mechanism.id,
                    sent_date=cp.status_date,
                    delivery_mechanism_order=1,
                    created_by_id=tp.created_by.id,
                    financial_service_provider_id=financial_service_provider.id,
                )
                dmppp.created_at = tp.created_at
                dmppp.save(update_fields=["created_at"])

                payment_verification_summary = PaymentVerificationSummary.objects.filter(
                    payment_plan_content_type_id=content_type_for_cash_plan.pk, payment_plan_object_id=cp.pk
                ).first()
                if payment_verification_summary:
                    if tp_counter > 0:
                        # create a copy of the summary for each target population
                        payment_verification_summary.pk = None
                        payment_verification_summary.payment_plan_content_type_id = content_type_for_payment_plan.id
                        payment_verification_summary.payment_plan_object_id = pp.id
                        payment_verification_summary.payment_plan = pp
                        payment_verification_summary.save()
                    else:
                        payment_verification_summary.payment_plan = pp
                        payment_verification_summary.save()

                payment_verification_plan = PaymentVerificationPlan.objects.filter(
                    payment_plan_content_type_id=content_type_for_cash_plan.pk, payment_plan_object_id=cp.pk
                ).first()
                if payment_verification_plan:
                    if tp_counter > 0:
                        # create a copy of the summary for each target population
                        _unicef_id = payment_verification_plan.unicef_id
                        payment_verification_plan.pk = None
                        payment_verification_plan.payment_plan_content_type_id = content_type_for_payment_plan.id
                        payment_verification_plan.payment_plan_object_id = pp.id
                        payment_verification_plan.payment_plan = pp
                        payment_verification_plan.save()
                        payment_verification_plan.unicef_id = _unicef_id
                        payment_verification_plan.save(update_fields=["unicef_id"])

                    else:
                        payment_verification_plan.payment_plan = pp
                        payment_verification_plan.save()

                with transaction.atomic():
                    for record in cp.payment_items.filter(target_population=tp).prefetch_related("service_provider"):
                        financial_service_provider = fsp_vision_vendor_number_to_obj.get(
                            record.service_provider.vision_id
                        )
                        payment = Payment.objects.create(
                            parent_id=pp.id,
                            business_area_id=pp.business_area.id,
                            status=get_status(record.status),
                            status_date=record.status_date,
                            household_id=record.household_id,
                            head_of_household_id=record.head_of_household_id or record.household.head_of_household_id,
                            collector_id=record.head_of_household_id or record.household.head_of_household_id,
                            delivery_type_id=record.delivery_type_id,
                            currency=record.currency,
                            entitlement_quantity=record.entitlement_quantity,
                            entitlement_quantity_usd=record.entitlement_quantity_usd,
                            delivered_quantity=record.delivered_quantity,
                            delivered_quantity_usd=record.delivered_quantity_usd,
                            delivery_date=record.delivery_date,
                            transaction_reference_id=record.transaction_reference_id,
                            transaction_status_blockchain_link=record.transaction_status_blockchain_link,
                            financial_service_provider=financial_service_provider,
                            program_id=tp.program_cycle.program_id,
                            is_cash_assist=True,
                            internal_data={
                                "ca_hash_id": str(record.ca_hash_id),
                                "full_name": record.full_name,
                                "total_persons_covered": record.total_persons_covered,
                                "distribution_modality": record.distribution_modality,
                                "target_population_cash_assist_id": record.target_population_cash_assist_id,
                                "target_population": str(record.target_population_id),
                                "entitlement_card_number": record.entitlement_card_number,
                                "entitlement_card_status": record.entitlement_card_status,
                                "entitlement_card_issue_date": str(record.entitlement_card_issue_date),
                                "vision_id": record.vision_id,
                                "registration_ca_id": record.registration_ca_id,
                                "service_provider": str(record.service_provider_id),
                            },
                        )
                        payment.unicef_id = record.ca_id
                        payment.save(update_fields=["unicef_id"])

                        payment_record_verification = PaymentVerification.objects.filter(
                            payment_content_type_id=content_type_for_payment_record.pk, payment_object_id=record.pk
                        ).first()
                        if payment_record_verification:
                            payment_record_verification.payment_verification_plan = payment_verification_plan
                            payment_record_verification.payment = payment
                            payment_record_verification.save()

                        ticket_complaint_details = TicketComplaintDetails.objects.filter(
                            payment_content_type_id=content_type_for_payment_record.pk, payment_object_id=record.pk
                        ).first()
                        if ticket_complaint_details:
                            ticket_complaint_details.payment = payment
                            ticket_complaint_details.save()

                        ticket_sensitive_details = TicketSensitiveDetails.objects.filter(
                            payment_content_type_id=content_type_for_payment_record.pk, payment_object_id=record.pk
                        ).first()
                        if ticket_sensitive_details:
                            ticket_sensitive_details.payment = payment
                            ticket_sensitive_details.save()

                create_payment_plan_snapshot_data(pp)

                pp.update_population_count_fields()

                payments = pp.eligible_payments.aggregate(
                    total_entitled_quantity=Coalesce(Sum("entitlement_quantity"), Decimal(0.0)),
                    total_entitled_quantity_usd=Coalesce(Sum("entitlement_quantity_usd"), Decimal(0.0)),
                    total_delivered_quantity=Coalesce(Sum("delivered_quantity"), Decimal(0.0)),
                    total_delivered_quantity_usd=Coalesce(Sum("delivered_quantity_usd"), Decimal(0.0)),
                )

                pp.total_entitled_quantity = payments.get("total_entitled_quantity", 0.00)
                pp.total_entitled_quantity_usd = payments.get("total_entitled_quantity_usd", 0.00)
                pp.total_delivered_quantity = payments.get("total_delivered_quantity", 0.00)
                pp.total_delivered_quantity_usd = payments.get("total_delivered_quantity_usd", 0.00)

                pp.total_undelivered_quantity = pp.total_entitled_quantity - pp.total_delivered_quantity
                pp.total_undelivered_quantity_usd = pp.total_entitled_quantity_usd - pp.total_delivered_quantity_usd

                pp.save(
                    update_fields=[
                        "total_entitled_quantity",
                        "total_entitled_quantity_usd",
                        "total_delivered_quantity",
                        "total_delivered_quantity_usd",
                        "total_undelivered_quantity",
                        "total_undelivered_quantity_usd",
                    ]
                )

                tp_counter += 1

            cp.is_migrated_to_payment_plan = True
            cp.save(update_fields=["is_migrated_to_payment_plan"])


def migrate_cash_assist_models() -> None:
    print("***Migrating Cash Assist models to Payment models***")
    migrate_cash_plan_to_payment_plan()
