import datetime
from django.utils import timezone
import json

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_TAX_ID, DocumentType
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType,
    ImportedHousehold,
    Record,
    ImportedDocument,
)
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    FlexRegistrationService,
)


class TestUkrainianRegistrationService(TestCase):
    databases = (
        "default",
        "registration_datahub",
    )

    @classmethod
    def setUp(self):
        ImportedDocumentType.objects.create(
            type=IDENTIFICATION_TYPE_TAX_ID, label=IDENTIFICATION_TYPE_TAX_ID, country="UA"
        )
        BusinessArea.objects.create(
            **{
                "code": "0060",
                "name": "Ukraine",
                "long_name": "Ukraine",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "ukraine",
                "has_data_sharing_agreement": True,
            },
        )
        household = [
            {
                "residence_status_h_c": "non_host",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0702001",
                "size_h_c": 5,
            }
        ]
        individual_wit_bank_account_and_tax_and_disability = {
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Jan",
            "family_name_i_c": "Romaniak",
            "patronymic": "Roman",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_wit_bank_account_and_tax = {
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Wiktor",
            "family_name_i_c": "Lamiący",
            "patronymic": "Stefan",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_with_no_tax = {
            "tax_id_no_i_c": "",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Michał",
            "family_name_i_c": "Brzęczący",
            "patronymic": "Janusz",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_without_bank_account = {
            "tax_id_no_i_c": "TESTID",
            "bank_account_h_f": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_with_tax_id_which_is_too_long = {
            "tax_id_no_i_c": "x" * 300,
            "bank_account_h_f": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        defaults = {
            "registration": 1,
            "timestamp": timezone.make_aware(datetime.datetime(2022, 4, 1)),
        }

        files = {
            "individuals": [
                {
                    "disability_certificate_picture": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
                }
            ]
        }

        records = [
            Record(
                **defaults,
                source_id=1,
                fields={"household": household, "individuals": [individual_wit_bank_account_and_tax_and_disability]},
                files=json.dumps(files).encode(),
            ),
            Record(
                **defaults,
                source_id=2,
                fields={"household": household, "individuals": [individual_wit_bank_account_and_tax]},
                files=json.dumps({}).encode(),
            ),
            Record(
                **defaults,
                source_id=3,
                fields={"household": household, "individuals": [individual_with_no_tax]},
                files=json.dumps(files).encode(),
            ),
            Record(
                **defaults,
                source_id=4,
                fields={"household": household, "individuals": [individual_without_bank_account]},
                files=json.dumps(files).encode(),
            ),
        ]
        bad_records = [
            Record(
                **defaults,
                source_id=1,
                fields={"household": household, "individuals": [individual_with_tax_id_which_is_too_long]},
                files=json.dumps(files).encode(),
            ),
        ]
        self.records = Record.objects.bulk_create(records)
        self.bad_records = Record.objects.bulk_create(bad_records)
        self.user = UserFactory.create()

    def test_import_data_to_datahub(self):
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)
        self.records[2].refresh_from_db()
        self.assertEqual(Record.objects.filter(id__in=records_ids, ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)
        self.assertEqual(
            ImportedDocument.objects.filter(document_number="TESTID", type__type=IDENTIFICATION_TYPE_TAX_ID).count(),
            1,
        )

    def test_import_data_to_datahub_retry(self):
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids_all = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids_all)
        self.records[2].refresh_from_db()
        self.assertEqual(Record.objects.filter(id__in=records_ids_all, ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records[:2]]
        service.process_records(rdi.id, records_ids)
        self.assertEqual(Record.objects.filter(id__in=records_ids_all, ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)

    def test_import_document_validation(self):
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [x.id for x in self.bad_records])
        self.bad_records[0].refresh_from_db()
        self.assertEqual(self.bad_records[0].status, Record.STATUS_ERROR)
        self.assertEqual(ImportedHousehold.objects.count(), 0)
