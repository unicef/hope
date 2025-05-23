from hct_mis_api.apps.household.models import BankAccountInfo
from hct_mis_api.apps.payment.models import Account, AccountType


def migrate_bank_account_info() -> None:
    bank_account_type, _ = AccountType.objects.get_or_create(
        key="bank", defaults=dict(label="Bank", unique_fields=["number"])
    )
    bank_account_ids = (
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
    dmd_ids = []
    for bai in BankAccountInfo.all_objects.filter(id__in=bank_account_ids).iterator(chunk_size=1000):
        dmd, _ = Account.get_or_create(
            individual_id=bai.individual_id,
            account_type=bank_account_type,
        )
        dmd.data.update(
            dict(
                name=bai.bank_name or "",
                number=bai.bank_account_number or "",
                debit_card_number=bai.debit_card_number or "",
                branch_name=bai.bank_branch_name or "",
                account_holder_name=bai.account_holder_name or "",
            )  # TODO field names?
        )
        dmd.save()
        dmd_ids.append(dmd.id)

    Account.validate_uniqueness(Account.objects.filter(id__in=dmd_ids))


def migrate_collectors_accounts() -> None:
    migrate_bank_account_info()
