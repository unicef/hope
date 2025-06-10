from django.db import transaction

from hct_mis_api.apps.payment.models import (
    Account,
    AccountType,
    FinancialInstitution,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
)


def create_financial_institutions() -> None:
    # Chunk size
    CHUNK_SIZE = 10000

    # Get the distinct bank account IDs in a memory-safe way
    def yield_account_id_chunks():  # type: ignore
        qs = Account.all_objects.order_by("individual__business_area", "created_at").values_list("id", flat=True)
        chunk = []
        for pk in qs.iterator(chunk_size=CHUNK_SIZE):
            chunk.append(pk)
            if len(chunk) >= CHUNK_SIZE:
                yield chunk
                chunk = []

        if chunk:
            yield chunk

    account_type_mobile = AccountType.objects.get(key="mobile")
    account_type_bank = AccountType.objects.get(key="bank")

    account_ids = []
    created_fi = {}
    chunk_count = 0

    uba_fsp = FinancialServiceProvider.objects.get(name="United Bank for Africa - Nigeria")

    for id_chunk in yield_account_id_chunks():  # type: ignore
        chunk_count += 1
        print(f"Chunk {chunk_count}")
        for account in (
            Account.all_objects.filter(id__in=id_chunk)
            .select_related(
                "individual__business_area",
                "individual__household__country",
            )
            .order_by("created_at")
            .iterator(chunk_size=CHUNK_SIZE)
        ):
            if account.individual.business_area.slug == "nigeria":
                try:
                    ubabank_code = account.data.get("code")
                    mapping = FinancialInstitutionMapping.objects.get(
                        code=ubabank_code, financial_service_provider=uba_fsp
                    )
                    account.financial_institution = mapping.financial_institution
                    account.save(update_fields=["financial_institution"])
                    account_ids.append(account.id)
                except Exception as e:
                    print(f"Skipping nigeria account {account.id}\n", e)

            else:
                try:
                    if account.account_type == account_type_mobile:
                        payload_code = account.data.get("service_provider_code")
                        payload_bank_name = account.data.get("provider")
                    elif account.account_type == account_type_bank:
                        payload_code = account.data.get("code")
                        payload_bank_name = account.data.get("name")
                    else:
                        continue

                    if payload_code not in created_fi.keys():
                        fi = FinancialInstitution.objects.create(
                            name=payload_bank_name,
                            type="bank",
                            country=account.individual.household.country,
                            swift_code=payload_code,
                        )
                        created_fi[payload_code] = fi
                    else:
                        fi = created_fi[payload_code]

                    account.financial_institution = fi
                    account.save(update_fields=["financial_institution"])
                    account_ids.append(account.id)
                except Exception as e:
                    print(f"Skipping account {account.id}\n", e)

    Account.validate_uniqueness(Account.objects.filter(id__in=account_ids))
    print(f"Created {len(created_fi)} financial institutions")
    print(f"Updated {len(account_ids)} accounts")


def dry_run() -> None:
    with transaction.atomic():
        create_financial_institutions()
        raise Exception
