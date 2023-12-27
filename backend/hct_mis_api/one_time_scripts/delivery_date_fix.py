import logging
from typing import Iterator, List, Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet

from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.payment.models import Payment, PaymentPlan

logger = logging.getLogger(__name__)


def generic_batching(
    queryset: QuerySet,
    batch_size: int = 100,
    select_related: Optional[List[str]] = None,
    prefetch_related: Optional[List[str]] = None,
    objects_manager_name: Optional[str] = None,
) -> Iterator[QuerySet]:
    model_class = queryset.model
    id_list = list(queryset.values_list("id", flat=True))
    items_count = len(id_list)
    objects_manager = (
        model_class.objects if objects_manager_name is None else getattr(model_class, objects_manager_name)
    )
    for batch_start in range(0, len(id_list), batch_size):
        logger.info(f"Batch start {model_class} : {batch_start}/{items_count}")
        batch_end = batch_start + batch_size
        batched_ids = id_list[batch_start:batch_end]
        batched_queryset = objects_manager.filter(id__in=batched_ids)
        if select_related:
            batched_queryset = batched_queryset.select_related(*select_related)
        if prefetch_related:
            batched_queryset = batched_queryset.prefetch_related(*prefetch_related)
        yield batched_queryset


def delivery_date_fix() -> None:
    business_areas = list(BusinessArea.objects.only("slug", "id").all())
    for business_area in business_areas:
        delivery_date_fix_business_area(business_area)


def delivery_date_fix_business_area(business_area: BusinessArea) -> None:
    print(f"Fixing delivery dates for {business_area.name}")
    delivered_q = ~Q(Q(delivered_quantity__isnull=True) | Q(delivered_quantity=0))
    queryset = Payment.objects.filter(delivered_q, business_area=business_area, delivery_date__isnull=True)
    payment_plans_ids = list(PaymentPlan.objects.filter(business_area=business_area).values_list("id", flat=True))
    file_temps = (
        FileTemp.objects.filter(
            object_id__in=payment_plans_ids, content_type=ContentType.objects.get_for_model(PaymentPlan)
        )
        .order_by("created")
        .values("object_id", "created")
    )
    object_id_to_created = {str(file_temp["object_id"]): file_temp["created"] for file_temp in file_temps}

    for batch in generic_batching(queryset, batch_size=1000):
        for payment in batch:
            payment_plan_id = payment.parent_id
            created = object_id_to_created[payment_plan_id]
            # just in case of mistake
            if payment.delivery_date is not None:
                continue
            if payment.delivered_quantity is None or payment.delivered_quantity == 0:
                continue
            payment.delivery_date = created
        Payment.objects.bulk_update(batch, ["delivery_date"])
