from hct_mis_api.apps.payment.models import (
    Account,
    AccountType,
    DeliveryMechanism,
    Payment,
)


def migrate_mobile_money_accounts() -> None:
    mobile_account_type, _ = AccountType.objects.get_or_create(
        key="mobile", defaults=dict(label="Mobile", unique_fields=[])
    )
    mobile_money_dm = DeliveryMechanism.objects.get(code="mobile_money")
    # Chunk size
    CHUNK_SIZE = 10000

    handled_collectors_ids = []

    # Get the distinct payments/collectors IDs in a memory-safe way
    def yield_payments_id_chunks():  # type: ignore
        qs = (
            Payment.objects.filter(delivery_type=mobile_money_dm)
            .distinct(
                "collector",
            )
            .order_by("collector", "-created_at")
            .values_list("id", flat=True)
        )

        chunk = []
        for pk in qs.iterator(chunk_size=CHUNK_SIZE):
            chunk.append(pk)
            if len(chunk) >= CHUNK_SIZE:
                yield chunk
                chunk = []

        if chunk:
            yield chunk

    account_ids = []
    chunk_count = 0

    for id_chunk in yield_payments_id_chunks():  # type: ignore
        chunk_count += 1
        print(f"Chunk {chunk_count}")
        for payment in Payment.objects.filter(id__in=id_chunk).select_related("collector"):
            print(payment)
            if payment.collector_id not in handled_collectors_ids:
                snapshot = getattr(payment, "household_snapshot", None)
                if not snapshot:
                    continue
                snapshot_data = snapshot.snapshot_data
                collector_data = snapshot_data.get("primary_collector")
                if not collector_data:
                    continue

                snapshot_phone_number = collector_data.get("phone_no", "")
                collector_phone_number = payment.collector.phone_no

                if snapshot_phone_number:
                    handled_collectors_ids.append(payment.collector_id)

                    account, created = Account.all_objects.get_or_create(
                        individual_id=payment.collector_id,
                        account_type=mobile_account_type,
                        defaults=dict(
                            number=snapshot_phone_number,
                        ),
                    )

                    if created:
                        if snapshot_phone_number != collector_phone_number:
                            account.active = False
                        account.rdi_merge_status = "MERGED"
                        account.data.update(
                            dict(
                                number=snapshot_phone_number or "",
                            )
                        )
                        account.save()
                        account_ids.append(account.id)

    Account.validate_uniqueness(Account.objects.filter(id__in=account_ids))
