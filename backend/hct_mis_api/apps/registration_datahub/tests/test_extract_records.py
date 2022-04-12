import base64
import datetime
import json

from django.test import TestCase

from hct_mis_api.apps.registration_datahub.celery_tasks import extract_records_task
from hct_mis_api.apps.registration_datahub.models import Record


class TestExtractRecords(TestCase):
    databases = ("default", "registration_datahub")

    def test_extract_without_image(self):
        storage = {
            "household": [
                {
                    "residence_status_h_c": "non_host",
                    "where_are_you_now": "",
                    "admin1_h_c": "UA07",
                    "admin2_h_c": "UA0702",
                    "admin3_h_c": "UA0702001",
                    "size_h_c": 5,
                }
            ],
            "individuals": [
                {
                    "given_name_i_c": "\\u041d\\u0430\\u0442\\u0430\\u043b\\u0456\\u044f",
                    "family_name_i_c": "\\u0421\\u0430\\u043f\\u0456\\u0433\\u0430",
                    "patronymic": "\\u0410\\u0434\\u0430\\u043c\\u0456\\u0432\\u043d\\u0430",
                    "birth_date": "1983-09-24",
                    "gender_i_c": "female",
                    "relationship_i_c": "head",
                    "disability_i_c": "y",
                    "disabiliyt_recognize_i_c": "y",
                    "disability_certificate_picture": str(base64.b64encode(b"very big image")),
                    "phone_no_i_c": "0636060474",
                    "q1": "",
                    "tax_id_no_i_c": "123123123",
                    "national_id_no_i_c_1": "",
                    "international_passport_i_c": "",
                    "drivers_license_no_i_c": "",
                    "birth_certificate_no_i_c": "",
                    "residence_permit_no_i_c": "",
                    "birth_certificate_picture": str(base64.b64encode(b"very big image")),
                    "role_i_c": "y",
                    "bank_account_h_f": "y",
                    "bank_name_h_f": "privatbank",
                    "other_bank_name": "",
                    "bank_account": 2356789789789789,
                    "bank_account_number": "879789789",
                    "debit_card_number_h_f": 9978967867666,
                    "debit_card_number": "87987979789789",
                }
            ],
        }
        Record.objects.create(
            registration=1, timestamp=datetime.datetime.now(), source_id=1, storage=bytes(json.dumps(storage), "utf-8")
        )

        extract_records_task()

        record = Record.objects.first()
        self.assertTrue(record.data)
        self.assertEqual(
            record.data["individuals"][0],
            {
                "given_name_i_c": "\\u041d\\u0430\\u0442\\u0430\\u043b\\u0456\\u044f",
                "family_name_i_c": "\\u0421\\u0430\\u043f\\u0456\\u0433\\u0430",
                "patronymic": "\\u0410\\u0434\\u0430\\u043c\\u0456\\u0432\\u043d\\u0430",
                "birth_date": "1983-09-24",
                "gender_i_c": "female",
                "relationship_i_c": "head",
                "disability_i_c": "y",
                "disabiliyt_recognize_i_c": "y",
                "disability_certificate_picture": "",
                "phone_no_i_c": "0636060474",
                "q1": "",
                "tax_id_no_i_c": "123123123",
                "national_id_no_i_c_1": "",
                "international_passport_i_c": "",
                "drivers_license_no_i_c": "",
                "birth_certificate_no_i_c": "",
                "residence_permit_no_i_c": "",
                "birth_certificate_picture": "",
                "role_i_c": "y",
                "bank_account_h_f": "y",
                "bank_name_h_f": "privatbank",
                "other_bank_name": "",
                "bank_account": 2356789789789789,
                "bank_account_number": "879789789",
                "debit_card_number_h_f": 9978967867666,
                "debit_card_number": "87987979789789",
            },
        )
