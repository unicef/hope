from hct_mis_api.apps.household.models import BankAccountInfo
from hct_mis_api.apps.payment.models import Account, AccountType


def migrate_bank_account_info() -> None:
    bank_account_type, _ = AccountType.objects.get_or_create(
        key="bank", defaults=dict(label="Bank", unique_fields=["number"])
    )
    # Chunk size
    CHUNK_SIZE = 1000

    # Get the distinct bank account IDs in a memory-safe way
    def yield_bank_account_id_chunks():  # type: ignore
        qs = (
            BankAccountInfo.all_objects.order_by(
                "individual",
                "bank_name",
                "bank_account_number",
                "debit_card_number",
                "bank_branch_name",
                "account_holder_name",
                "id",
            )
            .distinct(
                "individual",
                "bank_name",
                "bank_account_number",
                "debit_card_number",
                "bank_branch_name",
                "account_holder_name",
            )
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

    dmd_ids = []
    chunk_count = 0
    for id_chunk in yield_bank_account_id_chunks():  # type: ignore
        chunk_count += 1
        print(f"Chunk {chunk_count}")
        for bai in BankAccountInfo.all_objects.filter(id__in=id_chunk).iterator(chunk_size=CHUNK_SIZE):
            dmd, _ = Account.objects.get_or_create(
                individual_id=bai.individual_id,
                account_type=bank_account_type,
                number=bai.bank_account_number or "",
            )
            dmd.data.update(
                dict(
                    name=bai.bank_name or "",
                    number=bai.bank_account_number or "",
                    debit_card_number=bai.debit_card_number or "",
                    branch_name=bai.bank_branch_name or "",
                    account_holder_name=bai.account_holder_name or "",
                )
            )
            dmd.save()
            dmd_ids.append(dmd.id)

    Account.validate_uniqueness(Account.objects.filter(id__in=dmd_ids))


def migrate_collectors_accounts() -> None:
    migrate_bank_account_info()
