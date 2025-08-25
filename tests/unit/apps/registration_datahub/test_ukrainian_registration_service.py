import datetime
import json
from typing import Dict

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.aurora import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.program import ProgramFactory

from hope.models.core import DataCollectingType
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.models.household import (
    IDENTIFICATION_TYPE_TAX_ID,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.ukraine_flex_registration_service import (
    Registration2024,
    UkraineBaseRegistrationService,
)


class BaseTestUkrainianRegistrationService(TestCase):
    @classmethod
    def individual_with_bank_account_and_tax_and_disability(cls) -> Dict:
        return {
            "tax_id_no_i_c": "123123123",
            "relationship_i_c": "head",
            "given_name_i_c": "Jan",
            "family_name_i_c": "Romaniak",
            "patronymic": "Roman",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email123@mail.com",
        }

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init_geo_fixtures")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
            label=IDENTIFICATION_TYPE_TAX_ID,
        )
        cls.business_area = BusinessAreaFactory(slug="some-ukraine-slug")

        cls.data_collecting_type = DataCollectingType.objects.create(label="SomeFull", code="some_full")
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.program = ProgramFactory(status="ACTIVE", data_collecting_type=cls.data_collecting_type)
        cls.organization = OrganizationFactory(business_area=cls.business_area, slug=cls.business_area.slug)
        cls.project = ProjectFactory(name="fake_project", organization=cls.organization, programme=cls.program)
        cls.registration = RegistrationFactory(name="fake_registration", project=cls.project)
        admin1 = AreaFactory(p_code="UA07", name="Name1")
        admin2 = AreaFactory(p_code="UA0702", name="Name2", parent=admin1)
        AreaFactory(p_code="UA0702001", name="Name3", parent=admin2)

        cls.household = [
            {
                "residence_status_h_c": "non_host",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0702001",
                "size_h_c": 5,
            }
        ]

        individual_wit_bank_account_and_tax = {
            "tax_id_no_i_c": "123123123",
            "relationship_i_c": "head",
            "given_name_i_c": "Wiktor",
            "family_name_i_c": "Lamiący",
            "patronymic": "Stefan",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email321@mail.com",
        }
        individual_with_no_tax = {
            "tax_id_no_i_c": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Michał",
            "family_name_i_c": "Brzęczący",
            "patronymic": "Janusz",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email111@mail.com",
        }
        individual_without_bank_account = {
            "tax_id_no_i_c": "TESTID",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email222@mail.com",
        }
        individual_with_tax_id_which_is_too_long = {
            "tax_id_no_i_c": "x" * 300,
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
            "email": "email333@mail.com",
        }
        defaults = {
            "registration": 2,
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
                fields={
                    "household": cls.household,
                    "individuals": [cls.individual_with_bank_account_and_tax_and_disability()],
                },
                files=json.dumps(files).encode(),
            ),
            Record(
                **defaults,
                source_id=2,
                fields={
                    "household": cls.household,
                    "individuals": [individual_wit_bank_account_and_tax],
                },
                files=json.dumps({}).encode(),
            ),
            Record(
                **defaults,
                source_id=3,
                fields={
                    "household": cls.household,
                    "individuals": [individual_with_no_tax],
                },
                files=json.dumps(files).encode(),
            ),
            Record(
                **defaults,
                source_id=4,
                fields={
                    "household": cls.household,
                    "individuals": [individual_without_bank_account],
                },
                files=json.dumps(files).encode(),
            ),
        ]
        bad_records = [
            Record(
                **defaults,
                source_id=1,
                fields={
                    "household": cls.household,
                    "individuals": [individual_with_tax_id_which_is_too_long],
                },
                files=json.dumps(files).encode(),
            ),
        ]
        cls.records = Record.objects.bulk_create(records)
        cls.bad_records = Record.objects.bulk_create(bad_records)
        cls.user = UserFactory.create()


class TestUkrainianRegistrationService(BaseTestUkrainianRegistrationService):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

    def test_import_data_to_datahub(self) -> None:
        service = UkraineBaseRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[2].refresh_from_db()
        assert Record.objects.filter(id__in=records_ids, ignored=False).count() == 4
        assert PendingHousehold.objects.count() == 4
        assert PendingHousehold.objects.filter(program=rdi.program).count() == 4
        assert (
            PendingDocument.objects.filter(
                document_number="TESTID",
                type__key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
            ).count()
            == 1
        )

        # Checking only first is enough, because they all in one RDI
        registration_data_import = PendingHousehold.objects.all()[0].registration_data_import
        assert registration_data_import.program == self.program

    def test_import_data_to_datahub_retry(self) -> None:
        service = UkraineBaseRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids_all = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids_all)
        self.records[2].refresh_from_db()
        assert Record.objects.filter(id__in=records_ids_all, ignored=False).count() == 4
        assert PendingHousehold.objects.count() == 4
        service = UkraineBaseRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records[:2]]
        service.process_records(rdi.id, records_ids)
        assert Record.objects.filter(id__in=records_ids_all, ignored=False).count() == 4
        assert PendingHousehold.objects.count() == 4

    def test_import_document_validation(self) -> None:
        service = UkraineBaseRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [x.id for x in self.bad_records])
        self.bad_records[0].refresh_from_db()
        assert self.bad_records[0].status == Record.STATUS_ERROR
        assert PendingHousehold.objects.count() == 0


class TestRegistration2024(BaseTestUkrainianRegistrationService):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.record = Record.objects.create(
            registration=2,
            timestamp=timezone.make_aware(datetime.datetime(2024, 2, 4)),
            source_id=5,
            fields={
                "household": cls.household,
                "individuals": [cls.individual_with_bank_account_and_tax_and_disability()],
            },
        )

    @classmethod
    def individual_with_bank_account_and_tax_and_disability(cls) -> Dict:
        return {
            **super().individual_with_bank_account_and_tax_and_disability(),
            "low_income_hh_h_f": True,
            "single_headed_hh_h_f": False,
        }

    def test_import_data_to_datahub(self) -> None:
        service = Registration2024(self.registration)
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")
        service.process_records(rdi.id, [self.record.id])

        assert Record.objects.filter(id__in=[self.record.id], ignored=False).count() == 1
        assert PendingHousehold.objects.count() == 1
        assert PendingIndividual.objects.count() == 1
        assert PendingIndividual.objects.filter(program=rdi.program).count() == 1
        assert PendingIndividual.objects.get(family_name="Romaniak").flex_fields == {
            "low_income_hh_h_f": True,
            "single_headed_hh_h_f": False,
        }
