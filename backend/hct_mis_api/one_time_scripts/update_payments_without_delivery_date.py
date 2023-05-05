from django.core.paginator import Paginator

from hct_mis_api.apps.payment.models import Payment, PaymentPlan


def update_payments_with_empty_delivery_date() -> None:
    payments_to_update = []
    queryset = (
        Payment.objects.filter(delivery_date__isnull=True, parent__status=PaymentPlan.Status.FINISHED)
        .only("parent", "delivery_date")
        .select_related("parent__export_file_per_fsp")
    )
    paginator = Paginator(queryset, 500)
    number_of_pages = paginator.num_pages

    for page in paginator.page_range:
        print(f"Processing page {page} of {number_of_pages}")
        for payment in paginator.page(page).object_list:
            delivery_date = getattr(payment.parent.export_file_per_fsp, "created", None)
            if delivery_date:
                payment.delivery_date = delivery_date
                payments_to_update.append(payment)
        Payment.objects.bulk_update(payments_to_update, ["delivery_date"])
        payments_to_update = []
