from django.core.management import BaseCommand

from hct_mis_api.apps.household.models import BankAccountInfo
from hct_mis_api.apps.registration_datahub.models import ImportedBankAccountInfo


class Command(BaseCommand):
    help = "Fix Bank Account info (remove space from account number and debit card number)"

    def bank_acc_remove_space(self):
        # update BankAccountInfo
        qs = BankAccountInfo.objects.all()

        for bank_acc in qs:
            bank_acc.bank_account_number = bank_acc.bank_account_number.replace(" ", "")
            bank_acc.debit_card_number = bank_acc.debit_card_number.replace(" ", "")

        BankAccountInfo.objects.bulk_update(qs, ["bank_account_number", "debit_card_number"], 1000)

        # update ImportedBankAccountInfo
        qs = ImportedBankAccountInfo.objects.all()

        for bank_acc in qs:
            bank_acc.bank_account_number = bank_acc.bank_account_number.replace(" ", "")
            bank_acc.debit_card_number = bank_acc.debit_card_number.replace(" ", "")

        ImportedBankAccountInfo.objects.bulk_update(qs, ["bank_account_number", "debit_card_number"], 1000)

    def handle(self, *args, **options):
        print("Starting fix Bank Account Info")

        self.bank_acc_remove_space()
        print("Fixed Bank Account Info")
