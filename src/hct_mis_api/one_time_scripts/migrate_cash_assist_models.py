from django.contrib.contenttypes.models import ContentType
from django.db import transaction

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


def get_status(status: str) -> str:
    mapping = {"Transaction Successful": "Distribution Successful"}
    return mapping.get(status, status)


def migrate_cash_plan_to_payment_plan() -> None:
    content_type_for_payment_plan = ContentType.objects.get_for_model(PaymentPlan)
    content_type_for_cash_plan = ContentType.objects.get_for_model(CashPlan)
    content_type_for_payment = ContentType.objects.get_for_model(Payment)
    content_type_for_payment_record = ContentType.objects.get_for_model(PaymentRecord)

    delivery_type_to_obj = {obj.name: obj for obj in DeliveryMechanism.objects.all()}

    for sp in ServiceProvider.objects.all():
        if not sp.cash_plans.exists():
            continue

        if FinancialServiceProvider.objects.filter(vision_vendor_number=sp.vision_id).exists():
            continue

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

    fsp_vision_vendor_number_to_obj = {obj.vision_vendor_number: obj for obj in FinancialServiceProvider.objects.all()}

    dm_cash = delivery_type_to_obj["Cash"]

    for cp in CashPlan.objects.filter(is_migrated_to_payment_plan=False):
        with transaction.atomic():
            if not cp.payment_items.exists():
                continue

            # get target populations from payment records
            target_populations = cp.payment_items.values_list("target_population", flat=True).distinct()
            # for each target population create a payment plan within tp.payment_cycle
            for tp in target_populations:
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
                    created_at=tp.created_at,
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
                pp.unicef_id = cp.ca_id
                pp.save(update_fields=["unicef_id"])
                pp.update_population_count_fields()

                if not first_record.service_provider.vision_id:
                    raise Exception(f"Service provider {first_record.service_provider} vision_id is None")
                financial_service_provider = fsp_vision_vendor_number_to_obj.get(
                    first_record.service_provider.vision_id
                )
                if not financial_service_provider:
                    raise Exception(
                        f"FinancialServiceProvider not found for vision_id: {first_record.service_provider.vision_id}"
                    )

                DeliveryMechanismPerPaymentPlan.objects.update_or_create(
                    payment_plan_id=pp.id,
                    delivery_mechanism_id=delivery_mechanism.id,
                    sent_date=cp.status_date,
                    delivery_mechanism_order=1,
                    created_by_id=tp.created_by.id,
                    created_at=tp.created_at,
                    financial_service_provider_id=financial_service_provider.id,
                )

                # migrate payment verification summary, payment verification plans

                payment_verification_summary = PaymentVerificationSummary.objects.filter(
                    payment_plan_content_type_id=content_type_for_cash_plan.pk, payment_plan_object_id=cp.pk
                ).first()
                if payment_verification_summary:
                    payment_verification_summary.payment_plan_content_type_id = content_type_for_payment_plan.id
                    payment_verification_summary.payment_plan_object_id = pp.id
                    payment_verification_summary.payment_plan = pp
                    payment_verification_summary.save()

                payment_verification_plan = PaymentVerificationPlan.objects.filter(
                    payment_plan_content_type_id=content_type_for_cash_plan.pk, payment_plan_object_id=cp.pk
                ).first()
                if payment_verification_plan:
                    payment_verification_plan.payment_plan_content_type_id = content_type_for_payment_plan.id
                    payment_verification_plan.payment_plan_object_id = pp.id
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
                            head_of_household_id=record.head_of_household_id,
                            collector_id=record.head_of_household_id,
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
                            payment_record_verification.payment_content_type_id = content_type_for_payment.id
                            payment_record_verification.payment_object_id = payment.id
                            payment_record_verification.save()

                        ticket_complaint_details = TicketComplaintDetails.objects.filter(
                            payment_content_type_id=content_type_for_payment_record.pk, payment_object_id=record.pk
                        ).first()
                        if ticket_complaint_details:
                            ticket_complaint_details.payment_content_type_id = content_type_for_payment.id
                            ticket_complaint_details.payment_object_id = payment.id
                            ticket_complaint_details.save()

                        ticket_sensitive_details = TicketSensitiveDetails.objects.filter(
                            payment_content_type_id=content_type_for_payment_record.pk, payment_object_id=record.pk
                        ).first()
                        if ticket_sensitive_details:
                            ticket_sensitive_details.payment_content_type_id = content_type_for_payment.id
                            ticket_sensitive_details.payment_object_id = payment.id
                            ticket_sensitive_details.save()

                create_payment_plan_snapshot_data(pp)

            cp.is_migrated_to_payment_plan = True
            cp.save(update_fields=["is_migrated_to_payment_plan"])


def migrate_payment_verification_plan_generic_foreign_key_to_foreign_key() -> None:
    with transaction.atomic():
        verification_plans_to_update = []
        for verification_plan in PaymentVerificationPlan.objects.exclude(
            payment_plan_content_type__isnull=True, payment_plan_object_id__isnull=True
        ):
            if verification_plan.payment_plan_content_type.model == "paymentplan":
                payment_plan = PaymentPlan.objects.get(id=verification_plan.payment_plan_object_id)
                verification_plan.payment_plan = payment_plan
                verification_plans_to_update.append(verification_plan)

        PaymentVerificationPlan.objects.bulk_update(verification_plans_to_update, ["payment_plan"])


def migrate_payment_verification_summary_generic_foreign_key_to_onetoone() -> None:
    with transaction.atomic():
        verification_summaries_to_update = []
        for verification_summary in PaymentVerificationSummary.objects.exclude(
            payment_plan_content_type__isnull=True, payment_plan_object_id__isnull=True
        ):
            if verification_summary.payment_plan_content_type.model == "paymentplan":
                related_instance = PaymentPlan.objects.get(id=verification_summary.payment_plan_object_id)
                verification_summary.payment_plan = related_instance
                verification_summaries_to_update.append(verification_summary)

        PaymentVerificationSummary.objects.bulk_update(verification_summaries_to_update, ["payment_plan"])


def migrate_payment_verification_generic_foreign_key_to_onetoone() -> None:
    with transaction.atomic():
        verifications_to_update = []
        for verification in PaymentVerification.objects.exclude(
            payment_content_type__isnull=True, payment_object_id__isnull=True
        ):
            if verification.payment_content_type.model == "payment":
                related_instance = Payment.objects.get(id=verification.payment_object_id)
                verification.payment = related_instance
                verifications_to_update.append(verification)

        PaymentVerification.objects.bulk_update(verifications_to_update, ["payment"])


def migrate_payment_verification_models() -> None:
    migrate_payment_verification_plan_generic_foreign_key_to_foreign_key()
    migrate_payment_verification_summary_generic_foreign_key_to_onetoone()
    migrate_payment_verification_generic_foreign_key_to_onetoone()
