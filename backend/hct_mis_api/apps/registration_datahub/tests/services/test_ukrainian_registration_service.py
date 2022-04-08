import datetime
import json

from django.test import TestCase

from hct_mis_api.apps.registration_datahub.models import Record
from hct_mis_api.apps.registration_datahub.services.ukrainian_registration_service import UkrainianRegistrationService


class TestUkrainianRegistrationService(TestCase):
    databases = ("default", "registration_datahub",)

    @classmethod
    def setUpTestData(cls):
        household = [
            {
                "residence_status_h_c": "non_host",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0702001",
                "size_h_c": 5
            }
        ]
        individual_wit_bank_account_and_tax_and_disability = {
            "disability_certificate_picture": "picture.jpeg",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
        }
        individual_wit_bank_account_and_tax = {
            "disability_certificate_picture": None,
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
        }
        individual_with_no_tax = {
            "disability_certificate_picture": "picture.jpeg",
            "tax_id_no_i_c": "",
            "bank_account_h_f": "y",
        }
        individual_without_bank_account = {
            "disability_certificate_picture": "picture.jpeg",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "",
        }
        defaults = {
            "registration": 1,
            "timestamp": datetime.datetime(2022, 4, 1),
            "source_id": 1,
        }

        records = [
            Record(**defaults,
                   storage=bytes(json.dumps({"household": household,
                                             "individuals": [individual_wit_bank_account_and_tax_and_disability]}),
                                 'utf-8')),
            Record(**defaults, storage=bytes(
                json.dumps({"household": household, "individuals": [individual_wit_bank_account_and_tax]}),
                'utf-8')),
            Record(**defaults,
                   storage=bytes(json.dumps({"household": household, "individuals": [individual_with_no_tax]}),
                                 'utf-8')),
            Record(**defaults, storage=bytes(
                json.dumps({"household": household, "individuals": [individual_without_bank_account]}),
                'utf-8')),
        ]
        cls.records = Record.objects.bulk_create(records)

    def test_import_data_to_datahub(self):
        service = UkrainianRegistrationService(self.records)
