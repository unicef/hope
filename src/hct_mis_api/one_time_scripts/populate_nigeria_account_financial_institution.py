from django.db import transaction

from apps.payment.models import FinancialInstitution

from hct_mis_api.apps.payment.models import (
    Account,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
)


def populate_nigeria_account_financial_institution() -> None:
    uba_fsp = FinancialServiceProvider.objects.get(name="United Bank for Africa - Nigeria")

    # "code" accounts
    accounts_to_update = []
    accounts = Account.all_objects.filter(
        individual__business_area__slug="nigeria", data__code__isnull=False, financial_institution__isnull=True
    )
    for account in accounts:
        try:
            uba_mapping = FinancialInstitutionMapping.objects.get(
                code=account.data["code"],
                financial_service_provider=uba_fsp,
            )
            account.financial_institution = uba_mapping.financial_institution

        except FinancialInstitutionMapping.DoesNotExist:
            try:
                fi = FinancialInstitution.objects.get(name=account.data["code"])
                account.financial_institution = fi
            except FinancialInstitution.DoesNotExist:
                print(
                    f"FinancialInstitutionMapping for {uba_fsp} uba code {account.data['code']} not found, account: {account.id}"
                )

        accounts_to_update.append(account)
    print(f"Updating {len(accounts_to_update)} 'code' accounts")
    Account.objects.bulk_update(accounts_to_update, ["financial_institution"])

    # "uba_code" accounts
    accounts_to_update = []
    accounts = Account.all_objects.filter(individual__business_area__slug="nigeria", data__uba_code__isnull=False)
    for account in accounts.iterator():
        account.data["code"] = account.data.pop("uba_code")
        if not account.financial_institution:
            try:
                uba_mapping = FinancialInstitutionMapping.objects.get(
                    code=account.data["code"],
                    financial_service_provider=uba_fsp,
                )
                account.financial_institution = uba_mapping.financial_institution
            except FinancialInstitutionMapping.DoesNotExist:
                try:
                    fi = FinancialInstitution.objects.get(name=account.data["code"])
                    account.financial_institution = fi
                except FinancialInstitution.DoesNotExist:
                    print(
                        f"FinancialInstitutionMapping for {uba_fsp} uba code {account.data['code']} not found, account: {account.id}"
                    )

        accounts_to_update.append(account)
    print(f"Updating {len(accounts_to_update)} 'uba_code' accounts")
    Account.objects.bulk_update(accounts_to_update, ["financial_institution", "data"])

    # "bank_code" accounts
    accounts_to_update = []
    accounts = Account.all_objects.filter(individual__business_area__slug="nigeria", data__bank_code__isnull=False)
    for account in accounts.iterator():
        account.data["code"] = account.data.pop("bank_code")
        if not account.financial_institution:
            try:
                uba_mapping = FinancialInstitutionMapping.objects.get(
                    code=account.data["code"],
                    financial_service_provider=uba_fsp,
                )
                account.financial_institution = uba_mapping.financial_institution
            except FinancialInstitutionMapping.DoesNotExist:
                try:
                    fi = FinancialInstitution.objects.get(name=account.data["code"])
                    account.financial_institution = fi
                except FinancialInstitution.DoesNotExist:
                    print(
                        f"FinancialInstitutionMapping for {uba_fsp} uba code {account.data['code']} not found, account: {account.id}"
                    )

        accounts_to_update.append(account)
    print(f"Updating {len(accounts_to_update)} 'bank_code' accounts")
    Account.objects.bulk_update(accounts_to_update, ["financial_institution", "data"])


def dry_run() -> None:
    with transaction.atomic():
        populate_nigeria_account_financial_institution()
        raise Exception
