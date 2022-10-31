import hashlib
from collections import defaultdict
from random import random

from django.core.management import BaseCommand
from django.db.transaction import atomic

from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    MALE,
    BankAccountInfo,
    Document,
    Individual,
)


class Command(BaseCommand):
    help = "Anonymize data"

    @atomic()
    def handle(self, *args, **options) -> None:
        pl_faker = Faker("pl_PL")
        ba_to_locale_dict = defaultdict(lambda: pl_faker)
        ba_to_locale_dict["afghanistan"] = Faker("fa_IR")
        ba_to_locale_dict["ukraine"] = Faker("uk_UA")
        ba_to_locale_dict["central-african-republic"] = Faker("fr_FR")

        business_areas_dict = BusinessArea.objects.in_bulk()
        index = 0
        print("Documents update Started")
        for document in Document.all_objects.all().only("document_number").iterator():
            index += 1
            if index % 1000 == 0:
                print(f"documents {index}")
            result = hashlib.md5(document.document_number.encode())
            document.document_number = result.hexdigest()[:16]
            document.photo = None
            document.save(update_fields=("document_number", "photo"))
        index = 0
        print("Individuals update Started")
        bulk_update_list = []
        for individual in (
            Individual.all_objects.all()
            .only("given_name", "middle_name", "family_name", "full_name", "sex", "business_area_id", "phone_no")
            .iterator()
        ):
            index += 1
            business_area = business_areas_dict[individual.business_area_id]
            given_name_hash = hash(individual.given_name)
            middle_name_hash = hash(individual.middle_name)
            family_name_hash = hash(individual.family_name)
            phone_no_hash = hash(individual.phone_no or random())
            fake = ba_to_locale_dict[business_area.slug]
            if individual.sex == MALE:
                fake.seed_instance(given_name_hash)
                individual.given_name = fake.first_name_male()
                if individual.middle_name:
                    fake.seed_instance(middle_name_hash)
                    individual.middle_name = fake.first_name_male()
            else:
                fake.seed_instance(given_name_hash)
                individual.given_name = fake.first_name_female()
                if individual.middle_name:
                    fake.seed_instance(middle_name_hash)
                    individual.middle_name = fake.first_name_female()
            fake.seed_instance(family_name_hash)
            individual.family_name = fake.last_name()
            fake.seed_instance(phone_no_hash)
            individual.phone_no = fake.phone_number()
            if individual.middle_name:
                individual.full_name = f"{individual.given_name} {individual.middle_name} {individual.family_name_hash}"
            else:
                individual.full_name = f"{individual.given_name} {individual.family_name_hash}"

            bulk_update_list.append(individual)
            if index % 1000 == 0:
                Individual.objects.bulk_update(
                    bulk_update_list, ("given_name", "middle_name", "family_name", "full_name", "phone_no")
                )
                bulk_update_list = []
                print(f"individuals {index}")

        Individual.objects.bulk_update(
            bulk_update_list, ("given_name", "middle_name", "family_name", "full_name", "phone_no")
        )
        bulk_update_list = []

        index = 0
        bank_infos = BankAccountInfo.objects.only("bank_account_number", "debit_card_number")
        fake = Faker("uk_UA")
        print("BankAccountInfo update started")
        for bank_info in bank_infos:
            index += 1
            if index % 1000 == 0:
                print(f"bank_info {index}")
            bank_info.bank_account_number = fake.iban()
            bank_info.bank_account_number = fake.credit_card_number()
            bulk_update_list.append(bank_info)
            if index % 1000 == 0:
                BankAccountInfo.objects.bulk_update(bulk_update_list, ("bank_account_number", "debit_card_number"))
                bulk_update_list = []
                print(f"individuals {index}")
        BankAccountInfo.objects.bulk_update(bulk_update_list, ("bank_account_number", "debit_card_number"))
        bulk_update_list = []
