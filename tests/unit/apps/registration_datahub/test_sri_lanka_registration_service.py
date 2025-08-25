import datetime

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from extras.test_utils.factories.aurora import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from freezegun import freeze_time

from hope.models.core import DataCollectingType
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from models import geo as geo_models
from hope.models.household import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hope.contrib.aurora.models import Record
from hope.contrib.aurora.services.sri_lanka_flex_registration_service import (
    SriLankaRegistrationService,
)


class TestSriLankaRegistrationService(TestCase):
    @classmethod
    def setUp(cls) -> None:
        call_command("init_geo_fixtures")
        DocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
            label=IDENTIFICATION_TYPE_NATIONAL_ID,
        )

        cls.business_area = BusinessAreaFactory(slug="sri-lanka2")
        cls.data_collecting_type = DataCollectingType.objects.create(label="SizeOnlyXYZ", code="size_onlyXYZ")
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.program = ProgramFactory(status="ACTIVE", data_collecting_type=cls.data_collecting_type)
        cls.organization = OrganizationFactory(business_area=cls.business_area, slug=cls.business_area.slug)
        cls.project = ProjectFactory(name="fake_project", organization=cls.organization, programme=cls.program)
        cls.registration = RegistrationFactory(name="fake_registration", project=cls.project)

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
        admin4 = geo_models.Area(
            name="SriLanka admin4",
            p_code="LK1163020",
            area_type=area_type4,
            parent=admin3,
        )
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
                "gender_i_c": " male",
                "phone_no_i_c": "+94788908046",
                "email": "email999@mail.com",
                "full_name_i_c": "Dome",
                "birth_date_i_c": "1980-01-04",
                "relationship_i_c": "brother_sister",
                "confirm_nic_number": "123456789V",
                "national_id_no_i_c": "123456789V",
                "branch_or_branch_code": "7472_002",
                "account_holder_name_i_c": "Test Holder Name 123",
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

    @freeze_time("2023-12-12")
    def test_import_data_to_datahub(self) -> None:
        service = SriLankaRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[0].refresh_from_db()
        assert Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count() == 2

        assert PendingHousehold.objects.count() == 1
        assert PendingHousehold.objects.filter(program=rdi.program).count() == 1
        assert PendingIndividualRoleInHousehold.objects.count() == 1
        assert PendingDocument.objects.count() == 1
        assert PendingDocument.objects.filter(program=rdi.program).count() == 1

        household = PendingHousehold.objects.first()
        assert household.admin1.p_code == "LK1"
        assert household.admin2.p_code == "LK11"
        assert household.admin3.p_code == "LK1163"
        assert household.admin4.p_code == "LK1163020"
        assert household.admin_area.p_code == "LK1163020"

        registration_data_import = household.registration_data_import

        assert registration_data_import.program == self.program

        assert PendingIndividual.objects.filter(relationship="HEAD").first().flex_fields == {"has_nic_number_i_c": "n"}

        assert PendingIndividual.objects.filter(full_name="Dome").first().flex_fields == {
            "confirm_nic_number": "123456789V",
            "branch_or_branch_code": "7472_002",
            "who_answers_this_phone": "alternate collector",
            "confirm_alternate_collector_phone_number": "+94788908046",
            "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
        }
        assert PendingIndividual.objects.filter(full_name="Dome").first().email == "email999@mail.com"
        assert PendingIndividual.objects.filter(full_name="Dome").first().age_at_registration == 43
        assert PendingIndividual.objects.filter(full_name="Dome", program=rdi.program).first().age_at_registration == 43

    def test_import_record_twice(self) -> None:
        service = SriLankaRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [self.records[0].id])
        self.records[0].refresh_from_db()

        assert Record.objects.first().status == Record.STATUS_IMPORTED
        assert PendingHousehold.objects.count() == 1

        # Process again, but no new household created
        service.process_records(rdi.id, [self.records[0].id])
        self.records[0].refresh_from_db()
        assert PendingHousehold.objects.count() == 1
