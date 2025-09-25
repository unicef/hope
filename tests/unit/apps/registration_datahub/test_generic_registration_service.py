import datetime
import json
from typing import Union

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from parameterized import parameterized

from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.aurora import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.generic_registration_service import (
    GenericRegistrationService,
)
from hope.models.country import Country
from hope.models.data_collecting_type import DataCollectingType
from hope.models.document import PendingDocument
from hope.models.document_type import DocumentType
from hope.models.household import (
    IDENTIFICATION_TYPE_TAX_ID,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    PendingHousehold,
)
from hope.models.individual import PendingIndividual
from hope.models.individual_role_in_household import PendingIndividualRoleInHousehold


class TestGenericRegistrationService(TestCase):
    databases = {"default"}

    @classmethod
    def setUp(cls) -> None:
        call_command("init_geo_fixtures")
        DocumentType.objects.create(key="tax_id", label="Tax ID")
        DocumentType.objects.create(key="disability_certificate", label="Disability Certificate")
        cls.business_area = BusinessAreaFactory(slug="generic-slug")
        ukr = Country.objects.get(name="Ukraine")

        cls.data_collecting_type = DataCollectingType.objects.create(label="SomeFull", code="some_full")
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.program = ProgramFactory(status="ACTIVE", data_collecting_type=cls.data_collecting_type)
        cls.organization = OrganizationFactory(business_area=cls.business_area, slug=cls.business_area.slug)
        cls.project = ProjectFactory(name="fake_project", organization=cls.organization, programme=cls.program)
        admin1 = AreaFactory(p_code="UA07", name="Name1", area_type__country=ukr)
        admin2 = AreaFactory(p_code="UA0702", name="Name2", parent=admin1, area_type__country=ukr)
        AreaFactory(p_code="UA0114007", name="Name3", parent=admin2, area_type__country=ukr)

        mapping = {
            "defaults": {"business_area": "ukraine", "country": "UA"},
            "household": {
                "admin1_h_c": "household.admin1",
                "admin2_h_c": "household.admin2",
                "admin3_h_c": "household.admin3",
                "admin4_h_c": "household.admin4",
                "ff": "household.flex_fields",
            },
            "individuals": {
                "birth_date": "individual.birth_date",
                "patronymic": "individual.middle_name",
                "id_type": "document.doc_tax-key",
                "disability_id_type_i_c": "document.disability_certificate-key",
                "disability_id_i_c": "document.disability_certificate-document_number",
                "disability_id_photo_i_c": "document.disability_certificate-photo",
            },
            "flex_fields": [
                "marketing.can_unicef_contact_you",
                "enumerators",
                "macioce",
            ],
            "household_constances": {"zip_code": "00126"},
            "individual_constances": {"pregnant": True},
        }
        cls.registration = RegistrationFactory(name="fake_registration", project=cls.project, mapping=mapping)

        cls.household = [
            {
                "residence_status_h_c": "NON_HOST",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0114007",
                "size_h_c": 5,
                "ff": "random",
            }
        ]
        cls.individual_with_bank_account_and_tax_and_disability = {
            "id_type": "tax_id",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Jan",
            "family_name_i_c": "Romaniak",
            "patronymic": "Roman",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "+393892781511",
            "email": "email123@mail.com",
            "role_pr_i_c": "y",
            "disability_id_type_i_c": "disability_certificate",
            "disability_id_i_c": "xyz",
        }
        cls.individual_with_bank_account_and_tax = {
            "id_type": "tax_id",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Wiktor",
            "family_name_i_c": "Lamiący",
            "patronymic": "Stefan",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "+393451232123",
            "email": "email321@mail.com",
        }
        cls.individual_with_no_tax = {
            "tax_id_no_i_c": "",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Michał",
            "family_name_i_c": "Brzęczący",
            "patronymic": "Janusz",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "+393451232124",
            "email": "email111@mail.com",
            "role_sec_i_c": "y",
        }
        cls.individual_without_bank_account = {
            "id_type": "tax_id",
            "tax_id_no_i_c": "TESTID",
            "bank_account_h_f": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "+393451212123",
            "email": "email222@mail.com",
        }
        cls.individual_with_tax_id_which_is_too_long = {
            "id_type": "tax_id",
            "tax_id_no_i_c": "x" * 300,
            "bank_account_h_f": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "+393451214623",
            "email": "email333@mail.com",
        }
        cls.defaults = {
            "registration": 2,
            "timestamp": timezone.make_aware(datetime.datetime(2022, 4, 1)),
        }

        cls.files = {
            "individuals": [
                {
                    "disability_id_photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP///////////////////////////////////"
                    "///////////////////////////////////////////////////wgALCAABAAEBAREA/8Q"
                    "AFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
                }
            ]
        }

        cls.user = UserFactory.create()

    @parameterized.expand(
        [
            ("UA07", "UA0702", "UA0114007", "UA0114007", "admin4_h_c"),
            (None, None, None, "UA0114007", "admin4_h_c"),
            (None, None, "UA0114007", None, "admin3_h_c"),
            (None, "UA0702", None, None, "admin2_h_c"),
        ]
    )
    def test_import_data_to_datahub(
        self,
        admin1_h_c: Union[str, None],
        admin2_h_c: Union[str, None],
        admin3_h_c: Union[str, None],
        admin4_h_c: Union[str, None],
        admin_area_field: str,
    ) -> None:
        self.household[0]["admin1_h_c"] = admin1_h_c
        self.household[0]["admin2_h_c"] = admin2_h_c
        self.household[0]["admin3_h_c"] = admin3_h_c
        self.household[0]["admin4_h_c"] = admin4_h_c
        records = [
            Record(
                **self.defaults,
                source_id=1,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_with_bank_account_and_tax_and_disability],
                },
                files=json.dumps(self.files).encode(),
            ),
            Record(
                **self.defaults,
                source_id=2,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_with_bank_account_and_tax],
                },
                files=json.dumps({}).encode(),
            ),
            Record(
                **self.defaults,
                source_id=3,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_with_no_tax],
                },
                files=json.dumps(self.files).encode(),
            ),
            Record(
                **self.defaults,
                source_id=4,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_without_bank_account],
                },
                files=json.dumps(self.files).encode(),
            ),
        ]
        bad_records = [
            Record(
                **self.defaults,
                source_id=1,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_with_tax_id_which_is_too_long],
                },
                files=json.dumps(self.files).encode(),
            ),
        ]
        records = Record.objects.bulk_create(records)
        Record.objects.bulk_create(bad_records)

        service = GenericRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"generic rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in records]
        service.process_records(rdi.id, records_ids)
        records[2].refresh_from_db()
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
        assert (
            PendingDocument.objects.filter(
                document_number="TESTID",
                type__key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
                program=rdi.program,
            ).count()
            == 1
        )

        # Checking only first is enough, because they all in one RDI
        pending_household = PendingHousehold.objects.all()[0]
        registration_data_import = pending_household.registration_data_import
        assert "ff" in pending_household.flex_fields
        assert registration_data_import.program == self.program

        assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).count() == 1
        assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_ALTERNATE).count() == 1

    def test_import_data_to_datahub_household_individual(self) -> None:
        records = [
            Record(
                **self.defaults,
                source_id=1,
                fields={
                    "household": self.household,
                    "individuals": [self.individual_with_bank_account_and_tax_and_disability],
                    "enumerators": "ABC",
                    "marketing": {"can_unicef_contact_you": "YES"},
                },
                files=json.dumps(self.files).encode(),
            ),
        ]
        records = Record.objects.bulk_create(records)
        service = GenericRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"generic rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in records]
        service.process_records(rdi.id, records_ids)
        assert Record.objects.filter(id__in=records_ids, ignored=False).count() == 1
        assert PendingHousehold.objects.count() == 1

        household = PendingHousehold.objects.first()
        assert household.zip_code == "00126"
        assert household.flex_fields["ff"] == "random"
        assert household.flex_fields["enumerators"] == "ABC"
        assert household.flex_fields["marketing_can_unicef_contact_you"] == "YES"

        assert PendingDocument.objects.get(document_number="123123123", type__key="tax_id")
        assert PendingDocument.objects.get(document_number="xyz", type__key="disability_certificate")
        assert PendingIndividual.objects.get(
            given_name="Jan",
            middle_name="Roman",
            family_name="Romaniak",
            relationship="HEAD",
            sex="MALE",
            email="email123@mail.com",
            phone_no="+393892781511",
            pregnant=True,
        )
        assert PendingIndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).count() == 1
