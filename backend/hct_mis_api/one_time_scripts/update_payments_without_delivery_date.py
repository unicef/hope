from django.core.paginator import Paginator

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import Payment, PaymentPlan


def update_payments_with_empty_delivery_date() -> None:
    payments_to_update = []
    queryset = (
        Payment.objects.filter(delivery_date__isnull=True, parent__status=PaymentPlan.Status.FINISHED)
        .only("id", "parent")
        .select_related("parent")
    )
    paginator = Paginator(queryset, 100)
    number_of_pages = paginator.num_pages

    most_recent_files = (
        FileTemp.objects.order_by("object_id", "-created").distinct("object_id").only("object_id", "created")
    )

    for page in paginator.page_range:
        print(f"Processing page {page} of {number_of_pages}")
        for payment in paginator.page(page).object_list:
            file_temp = most_recent_files.filter(object_id=payment.parent_id).first()
            if file_temp and file_temp.created:
                payment.delivery_date = file_temp.created
                payments_to_update.append(payment)
        Payment.objects.bulk_update(payments_to_update, ["delivery_date"])
        payments_to_update = []

    print("Processing finished successfully")
    return
