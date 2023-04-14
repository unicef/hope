import datetime

from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_NATIONAL_ID
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.sri_lanka_registration_service import (
    SriLankaRegistrationService,
)


class TestSriLankaRegistrationService(TestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUp(cls) -> None:
        ImportedDocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
            label=IDENTIFICATION_TYPE_NATIONAL_ID,
        )

        BusinessArea.objects.create(
            **{
                "code": "0780",
                "name": "Sri Lanka",
                "long_name": "THE DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "sri-lanka",
                "has_data_sharing_agreement": True,
            },
        )

        country = geo_models.Country.objects.create(name="Sri Lanka")

        area_type1 = geo_models.AreaType.objects.create(country=country, name="admin1")
        area_type2 = geo_models.AreaType.objects.create(country=country, name="admin2")
        area_type3 = geo_models.AreaType.objects.create(country=country, name="admin3")
        area_type4 = geo_models.AreaType.objects.create(country=country, name="admin4")

        admin1 = geo_models.Area(
            name="SriLanka admin1",
            p_code="LK1",
            area_type=area_type1,
        )
        admin1.save()
        admin2 = geo_models.Area(name="SriLanka admin2", p_code="LK11", area_type=area_type2, parent=admin1)
        admin2.save()
        admin3 = geo_models.Area(name="SriLanka admin3", p_code="LK1163", area_type=area_type3, parent=admin2)
        admin3.save()
        admin4 = geo_models.Area(name="SriLanka admin4", p_code="LK1163020", area_type=area_type4, parent=admin3)
        admin4.save()
        geo_models.Area.objects.rebuild()

        children_info = [
            {
                "gender_i_c": "male",
                "full_name_i_c": "Alexis",
                "birth_date_i_c": "2022-01-04",
                "relationship_i_c": "son_daughter",
            }
        ]

        caretaker_info = [
            {
                "gender_i_c": "   female",
                "full_name_i_c": "Alexis",
                "birth_date_i_c": "1989-01-04",
                "has_nic_number_i_c": "n",
                "who_answers_phone_i_c": "mother/caretaker",
            }
        ]

        collector_info = [
            {
                "bank_name": "7472",
                "gender_i_c": " male",
                "phone_no_i_c": "+94788908046",
                "email": "email999@mail.com",
                "full_name_i_c": "Dome",
                "birth_date_i_c": "1980-01-04",
                "bank_description": "Axis Bank",
                "relationship_i_c": "brother_sister",
                "confirm_nic_number": "123456789V",
                "national_id_no_i_c": "123456789V",
                "branch_or_branch_code": "7472_002",
                "confirm_bank_account_number": "0082785064",
                "who_answers_this_phone": "alternate collector",
                "confirm_alternate_collector_phone_number": "+94788908046",
                "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
            }
        ]

        localization_info = [
            {
                "admin2_h_c": "LK11",
                "admin3_h_c": "LK1163",
                "admin4_h_c": "LK1163020",
                "address_h_c": "Alexis",
                "moh_center_of_reference": "MOH279",
            }
        ]

        records = [
            Record(
                registration=17,
                timestamp=timezone.make_aware(datetime.datetime(2022, 4, 1)),
                source_id=1,
                fields={
                    "children-info": children_info,
                    "id_enumerator": "1992",
                    "caretaker-info": caretaker_info,
                    "collector-info": collector_info,
                    "localization-info": localization_info,
                    "prefered_language_of_contact": "ta",
                },
            ),
            Record(
                registration=17,
                timestamp=timezone.make_aware(datetime.datetime(2022, 4, 1)),
                source_id=2,
                fields={},
                status=Record.STATUS_IMPORTED,
            ),
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = SriLankaRegistrationService()
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[0].refresh_from_db()
        self.assertEqual(
            Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count(), 2
        )

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        self.assertEqual(ImportedIndividualRoleInHousehold.objects.count(), 1)
        self.assertEqual(ImportedBankAccountInfo.objects.count(), 1)
        self.assertEqual(ImportedDocument.objects.count(), 1)

        imported_household = ImportedHousehold.objects.first()
        self.assertEqual(imported_household.admin1, "LK1")
        self.assertEqual(imported_household.admin1_title, "SriLanka admin1")
        self.assertEqual(imported_household.admin2, "LK11")
        self.assertEqual(imported_household.admin2_title, "SriLanka admin2")
        self.assertEqual(imported_household.admin3, "LK1163")
        self.assertEqual(imported_household.admin3_title, "SriLanka admin3")
        self.assertEqual(imported_household.admin4, "LK1163020")
        self.assertEqual(imported_household.admin4_title, "SriLanka admin4")
        self.assertEqual(imported_household.admin_area, "LK1163020")
        self.assertEqual(imported_household.admin_area_title, "SriLanka admin4")

        self.assertEqual(
            ImportedIndividual.objects.filter(relationship="HEAD").first().flex_fields, {"has_nic_number_i_c": "n"}
        )

        self.assertEqual(
            ImportedIndividual.objects.filter(full_name="Dome").first().flex_fields,
            {
                "confirm_nic_number": "123456789V",
                "branch_or_branch_code": "7472_002",
                "who_answers_this_phone": "alternate collector",
                "confirm_alternate_collector_phone_number": "+94788908046",
                "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
            },
        )
        self.assertEqual(ImportedIndividual.objects.filter(full_name="Dome").first().email, "email999@mail.com")

    def test_import_record_twice(self) -> None:
        service = SriLankaRegistrationService()
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [self.records[0].id])
        self.records[0].refresh_from_db()

        self.assertEqual(Record.objects.first().status, Record.STATUS_IMPORTED)
        self.assertEqual(ImportedHousehold.objects.count(), 1)

        # Process again, but no new household created
        service.process_records(rdi.id, [self.records[0].id])
        self.records[0].refresh_from_db()
        self.assertEqual(ImportedHousehold.objects.count(), 1)

    def test_import_record_not_from_registration_17(self) -> None:
        record = Record.objects.create(
            registration=666,
            timestamp=timezone.make_aware(datetime.datetime(2022, 4, 1)),
            source_id=2,
            fields={},
            status=Record.STATUS_TO_IMPORT,
        )

        service = SriLankaRegistrationService()
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")
        service.process_records(rdi.id, [record.id])

        record.refresh_from_db()
        self.assertEqual(record.status, Record.STATUS_ERROR)
        self.assertEqual(ImportedHousehold.objects.count(), 0)
