from hct_mis_api.apps.payment.models import FinancialServiceProvider, PaymentPlan


def update_pg_payment_plans_money_fields() -> None:
    payment_plans = PaymentPlan.objects.filter(
        splits__sent_to_payment_gateway=True,
        status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
        financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        financial_service_provider__payment_gateway_id__isnull=False,
    ).distinct()
    print(f"PPs to update: {payment_plans.count()}")
    for idx, pp in enumerate(payment_plans):
        print(f"Updating {idx}")
        pp.update_money_fields()
