import datetime
import json

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from tests.extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.models import Area, AreaType
from hct_mis_api.apps.household.models import (
    HEAD,
    MALE,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from tests.extras.test_utils.factories.payment import generate_delivery_mechanisms
from hct_mis_api.apps.payment.models import PendingAccount
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.contrib.aurora.fixtures import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from hct_mis_api.contrib.aurora.models import Record
from hct_mis_api.contrib.aurora.services.nigeria_people_registration_service import (
    NigeriaPeopleRegistrationService,
)


class TestNigeriaPeopleRegistrationService(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUp(cls) -> None:
        generate_delivery_mechanisms()
        country = geo_models.Country.objects.create(name="Nigeria")
        area_type_1 = AreaType.objects.create(name="State", area_level=1, country=country)
        area_type_2 = AreaType.objects.create(
            name="Local government area", area_level=2, country=country, parent=area_type_1
        )
        area_type_3 = AreaType.objects.create(name="Ward", area_level=3, country=country, parent=area_type_2)
        area_1 = Area.objects.create(name="Borno", p_code="NG002", area_type=area_type_1)
        area_2 = Area.objects.create(name="Bama", p_code="NG002001", area_type=area_type_2, parent=area_1)
        Area.objects.create(name="Andara", p_code="NG002001007", area_type=area_type_3, parent=area_2)
        DocumentType.objects.create(key="national_id", label="National ID")
        cls.business_area = BusinessAreaFactory(slug="some-ng-slug")
        cls.data_collecting_type = DataCollectingType.objects.create(label="someLabel", code="some_label")
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.program = ProgramFactory(
            status="ACTIVE", data_collecting_type=cls.data_collecting_type, biometric_deduplication_enabled=True
        )
        cls.organization = OrganizationFactory(business_area=cls.business_area, slug=cls.business_area.slug)
        cls.project = ProjectFactory(name="fake_project", organization=cls.organization, programme=cls.program)
        cls.registration = RegistrationFactory(name="fake_registration", project=cls.project, mapping={})
        files = {
            "individual-details": [
                {
                    "photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
                    "national_id_photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
                }
            ]
        }
        records = [
            Record(
                registration=25,
                timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
                source_id=1,
                files=json.dumps(files).encode(),
                fields={
                    "household-info": [{"admin1_h_c": "NG002", "admin2_h_c": "NG002001", "admin3_h_c": "NG002001007"}],
                    "intro-and-consent": [
                        {"consent_h_c": True, "enumerator_code": "SHEAbi5350", "who_to_register": "myself"}  # ff  # ff
                    ],
                    "individual-details": [
                        {
                            "email_i_c": "gfranco@unicef.org",
                            "gender_i_c": "male",
                            "phone_no_i_c": "+2348023456789",
                            "birth_date_i_c": "1988-04-08",
                            "given_name_i_c": "Giulio",
                            "middle_name_i_c": "D",
                            "national_id_no": "01234567891",
                            "account_details": {
                                "uba_code": "000004",
                                "name": "United Bank for Africa",
                                "number": "2087008012",
                                "holder_name": "xxxx",
                            },
                            "family_name_i_c": "Franco",
                            "national_id_no_i_c": "01234567891",
                            "estimated_birth_date_i_c": "y",
                            "frontline_worker_designation_i_f": "H2HCL",  # ff
                        }
                    ],
                },
            )
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = NigeriaPeopleRegistrationService(self.registration)
        rdi = service.create_rdi(self.user, f"nigeria rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.assertEqual(
            Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count(), 1
        )
        self.assertEqual(PendingHousehold.objects.count(), 1)
        self.assertEqual(PendingHousehold.objects.filter(program=rdi.program).count(), 1)

        household = PendingHousehold.objects.first()
        self.assertEqual(household.consent, True)
        self.assertEqual(household.country, geo_models.Country.objects.get(iso_code2="NG"))
        self.assertEqual(household.country_origin, geo_models.Country.objects.get(iso_code2="NG"))
        self.assertEqual(household.head_of_household, PendingIndividual.objects.get(given_name="Giulio"))
        self.assertEqual(household.rdi_merge_status, "PENDING")
        self.assertEqual(household.flex_fields, {"enumerator_code": "SHEAbi5350", "who_to_register": "myself"})

        registration_data_import = household.registration_data_import
        self.assertEqual(registration_data_import.program, self.program)

        primary_collector = PendingIndividual.objects.get(id=household.head_of_household_id)
        self.assertIsNotNone(primary_collector.phone_no)
        self.assertEqual(primary_collector.sex, MALE)
        self.assertEqual(primary_collector.email, "gfranco@unicef.org")
        self.assertEqual(primary_collector.full_name, "Giulio D Franco")
        self.assertEqual(primary_collector.relationship, HEAD)
        self.assertIsNotNone(primary_collector.phone_no_alternative)
        self.assertEqual(
            primary_collector.flex_fields,
            {
                "frontline_worker_designation_i_f": "H2HCL",
                "national_id_no": "01234567891",
            },
        )
        self.assertEqual(primary_collector.rdi_merge_status, "PENDING")
        self.assertIsNotNone(primary_collector.photo.url)
        self.assertEqual(PendingIndividualRoleInHousehold.objects.count(), 1)

        primary_role = PendingIndividualRoleInHousehold.objects.first()
        self.assertEqual(primary_role.individual, primary_collector)
        self.assertEqual(primary_role.household, household)

        account = PendingAccount.objects.first()
        self.assertEqual(
            account.account_data,
            {
                "number": "2087008012",
                "name": "United Bank for Africa",
                "uba_code": "000004",
                "holder_name": "xxxx",
            },
        )
        self.assertEqual(account.account_type.key, "bank")

        national_id = PendingDocument.objects.filter(document_number="01234567891").first()
        self.assertEqual(national_id.individual, primary_collector)
        self.assertEqual(national_id.rdi_merge_status, "PENDING")
        self.assertIsNotNone(national_id.photo.url)
