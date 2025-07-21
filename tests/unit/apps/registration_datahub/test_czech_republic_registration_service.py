import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

import pytz

from tests.extras.test_utils.factories.account import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import (
    DISABLED,
    FEMALE,
    GOVERNMENT_PARTNER,
    MALE,
    NOT_DISABLED,
    PRIVATE_PARTNER,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.contrib.aurora.fixtures import (
    OrganizationFactory,
    ProjectFactory,
    RegistrationFactory,
)
from hct_mis_api.contrib.aurora.models import Record
from hct_mis_api.contrib.aurora.services.czech_republic_flex_registration_service import (
    CzechRepublicFlexRegistration,
)


class TestCzechRepublicRegistrationService(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUp(cls) -> None:
        document_types_to_create = []

        DOCUMENT_MAPPING = {
            "birth_certificate": "Birth Certificate",
            "disability_card": "Disability Card",
            "national_id": "National ID",
            "national_passport": "National Passport",
            "medical_certificate": "Medical Certificate",
            "temporary_protection_visa": "Temporary Protection Visa",
            "proof_legal_guardianship": "Proof of Legal Guardianship",
        }

        for key, label in DOCUMENT_MAPPING.items():
            document_types_to_create.append(DocumentType(key=key, label=label))

        DocumentType.objects.bulk_create(document_types_to_create)

        cls.business_area = BusinessAreaFactory(slug="some-czech-slug")

        cls.data_collecting_type = DataCollectingType.objects.create(label="someLabel", code="some_label")
        cls.data_collecting_type.limit_to.add(cls.business_area)

        cls.program = ProgramFactory(
            status="ACTIVE", data_collecting_type=cls.data_collecting_type, biometric_deduplication_enabled=True
        )
        cls.organization = OrganizationFactory(business_area=cls.business_area, slug=cls.business_area.slug)
        cls.project = ProjectFactory(name="fake_project", organization=cls.organization, programme=cls.program)
        cls.registration = RegistrationFactory(name="fake_registration", project=cls.project)

        geo_models.Country.objects.create(name="Czechia")

        consent = [
            {
                "consent_h_c": "y",
                "consent_sharing_h_c": True,
                "government_partner": "",
                "consent_sharing_h_c_1": "y",
                "consent_sharing_h_c_2": "n",
            }
        ]

        needs_assessment = [
            {
                "access_education_rate_h_f": "Somewhat Easy",
                "access_health_rate_h_f": "A little Difficult",
                "access_leisure_activities_rate_h_f": "Very Easy",
                "access_social_services_rate_h_f": "Very Easy",
                "additional_support_h_f": "y",
                "adults_count_h_f": 2,
                "assistance_h_f": "y",
                "children_below_18_h_f": 3,
                "in_state_provided_accommodation_h_f": "no",
                "receiving_mop_h_f": "n",
                "school_enrolled_i_f": "no",
            }
        ]

        household_address = [
            {
                "address_h_c": "Opo\u010d\u00ednsk\u00e1 375",
                "admin1_h_c": "CZ010",
                "admin2_h_c": "CZ0109",
                "village_h_c": "Praha",
                "zip_code_h_c": "19017",
            }
        ]

        primary_carer_info = [
            {
                "birth_date_i_c": "1995-08-01",
                "confirm_phone_number": "+420774844183",
                "country_origin_h_c": "ukr",
                "czech_formal_employment": "no",
                "family_name_i_c": "Symkanych",
                "gender_i_c": "female",
                "given_name_i_c": "Tetiana",
                "id_type_i_c": "national_passport",
                "national_passport_i_c": "GB500567",
                "other_communication_language": ["ru-ru"],
                "phone_no_i_c": "+420774844183",
                "preferred_language_i_c": "uk-ua",
                "primary_carer_is_legal_guardian": "y",
                "role_i_c": "primary",
                "work_status_i_c": "n",
            }
        ]

        children_information = [
            {
                "birth_certificate_no_i_c": "262873",
                "birth_date_i_c": "2013-07-04",
                "disability_i_c": "not disabled",
                "family_name_i_c": "Symkanych",
                "follow_up_needed": "n",
                "gender_i_c": "male",
                "given_name_i_c": "John",
                "has_birth_certificate_i_c": "y",
                "other_id_no_i_c": "900541571",
                "preregistration_case_id": "13277",
                "qualifies_for_programme_i_f": "y",
                "relationship_i_c": "son_daughter",
            },
            {
                "gender_i_c": "female",
                "id_type_i_c": "national_id",
                "birth_date_i_c": "2023-04-30",
                "disability_i_c": "disabled",
                "follow_up_flag": ["legal_guardianship_documents"],
                "given_name_i_c": "TEST",
                "family_name_i_c": "TEST",
                "follow_up_needed": "y",
                "relationship_i_c": "brother_sister",
                "follow_up_comments": "No comments",
                "national_id_no_i_c": "123214",
                "national_passport_i_c": "",
                "disability_card_i_c": "y",
                "disability_degree_i_c": "2",
                "disability_card_no_i_c": "1213",
                "medical_certificate_i_c": "y",
                "preregistration_case_id": "10937",
                "has_birth_certificate_i_c": "n",
                "medical_certificate_no_i_c": "2321",
                "qualifies_for_programme_i_f": "y",
                "disability_card_issuance_i_c": "2023-05-01",
                "proof_legal_guardianship_no_i_c": "128dj",
                "medical_certificate_issuance_i_c": "2023-05-01",
                "medical_certificate_validity_i_c": "2023-05-17",
                "has_disability_card_and_medical_cert": "Has Both",
            },
        ]

        legal_guardian_information = [
            {
                "gender_i_c": "male",
                "id_type_i_c": "national_passport",
                "phone_no_i_c": "+420123123666",
                "birth_date_i_c": "1988-12-27",
                "given_name_i_c": "Ivan",
                "family_name_i_c": "Drago",
                "relationship_i_c": "head",
                "confirm_phone_number": "+420123123666",
                "national_passport_i_c": "1234567890",
                "national_id_no_i_c": "",
                "legal_guardia_not_primary_carer": "y",
                "work_status_i_c": "y",
            },
            {
                "legal_guardia_not_primary_carer": "n",
            },
        ]
        records = [
            Record(
                registration=25,
                timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
                source_id=1,
                fields={
                    "consent": consent,
                    "needs-assessment": needs_assessment,
                    "household-address": household_address,
                    "primary-carer-info": primary_carer_info,
                    "children-information": children_information,
                    "legal-guardian-information": legal_guardian_information,
                },
            )
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = CzechRepublicFlexRegistration(self.registration)
        rdi = service.create_rdi(self.user, f"czech_republic rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[0].refresh_from_db()
        self.assertEqual(
            Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count(), 1
        )
        self.assertEqual(PendingHousehold.objects.count(), 1)
        self.assertEqual(PendingHousehold.objects.filter(program=rdi.program).count(), 1)

        household = PendingHousehold.objects.first()
        self.assertEqual(household.consent, True)
        self.assertEqual(household.consent_sharing, [GOVERNMENT_PARTNER, PRIVATE_PARTNER])
        self.assertEqual(household.country, geo_models.Country.objects.get(iso_code2="CZ"))
        self.assertEqual(household.country_origin, geo_models.Country.objects.get(iso_code2="CZ"))
        self.assertEqual(household.size, 4)
        self.assertEqual(household.zip_code, "19017")
        self.assertEqual(household.village, "Praha")
        self.assertEqual(household.head_of_household, PendingIndividual.objects.get(full_name="Ivan Drago"))
        self.assertEqual(household.rdi_merge_status, "PENDING")

        registration_data_import = household.registration_data_import
        self.assertEqual(registration_data_import.program, self.program)

        head_of_household = PendingIndividual.objects.get(full_name="Ivan Drago")
        self.assertEqual(head_of_household.sex, MALE)
        self.assertEqual(head_of_household.phone_no, "+420123123666")
        self.assertEqual(head_of_household.disability, NOT_DISABLED)
        self.assertEqual(head_of_household.work_status, "1")
        self.assertEqual(head_of_household.rdi_merge_status, "PENDING")

        primary_collector = PendingIndividual.objects.get(full_name="Tetiana Symkanych")
        self.assertEqual(primary_collector.sex, FEMALE)
        self.assertEqual(primary_collector.phone_no, "+420774844183")
        self.assertEqual(primary_collector.disability, NOT_DISABLED)
        self.assertEqual(primary_collector.work_status, "0")
        self.assertEqual(primary_collector.rdi_merge_status, "PENDING")
        self.assertEqual(PendingIndividualRoleInHousehold.objects.count(), 1)

        primary_role = PendingIndividualRoleInHousehold.objects.first()
        self.assertEqual(primary_role.individual, primary_collector)
        self.assertEqual(primary_role.household, household)

        first_child = PendingIndividual.objects.get(given_name="John")
        self.assertEqual(first_child.sex, MALE)
        self.assertEqual(str(first_child.birth_date), "2013-07-04")
        self.assertEqual(first_child.disability, NOT_DISABLED)
        self.assertEqual(first_child.rdi_merge_status, "PENDING")

        second_child = PendingIndividual.objects.get(given_name="TEST")
        self.assertEqual(second_child.sex, FEMALE)
        self.assertEqual(str(second_child.birth_date), "2023-04-30")
        self.assertEqual(second_child.disability, DISABLED)
        self.assertEqual(second_child.rdi_merge_status, "PENDING")

        birth_certificate = PendingDocument.objects.filter(type__key="birth_certificate").first()
        self.assertEqual(birth_certificate.document_number, "262873")
        self.assertEqual(PendingDocument.objects.filter(type__key="disability_card").count(), 1)
        self.assertEqual(PendingDocument.objects.filter(type__key="medical_certificate").count(), 1)
        self.assertEqual(PendingDocument.objects.filter(type__key="temporary_protection_visa").count(), 1)
        self.assertEqual(PendingDocument.objects.filter(type__key="proof_legal_guardianship").count(), 1)
        self.assertEqual(PendingDocument.objects.filter(type__key="national_passport").count(), 2)
        self.assertEqual(birth_certificate.rdi_merge_status, "PENDING")

        national_passport = PendingDocument.objects.filter(document_number="GB500567").first()
        self.assertEqual(national_passport.individual, primary_collector)
        self.assertEqual(national_passport.rdi_merge_status, "PENDING")

        disability_card = PendingDocument.objects.filter(type__key="disability_card").first()
        self.assertEqual(disability_card.document_number, "1213")
        self.assertEqual(disability_card.individual, second_child)
        self.assertEqual(disability_card.rdi_merge_status, "PENDING")

        medical_certificate = PendingDocument.objects.filter(type__key="medical_certificate").first()
        self.assertEqual(medical_certificate.document_number, "2321")
        self.assertEqual(medical_certificate.individual, second_child)
        self.assertEqual(medical_certificate.expiry_date, datetime.datetime(2023, 5, 17, tzinfo=pytz.UTC))
        self.assertEqual(medical_certificate.issuance_date, datetime.datetime(2023, 5, 1, tzinfo=pytz.UTC))
        self.assertEqual(medical_certificate.rdi_merge_status, "PENDING")

        temporary_protection_visa = PendingDocument.objects.filter(type__key="temporary_protection_visa").first()
        self.assertEqual(temporary_protection_visa.document_number, "900541571")
        self.assertEqual(temporary_protection_visa.individual, first_child)
        self.assertEqual(temporary_protection_visa.rdi_merge_status, "PENDING")

        proof_legal_guardianship = PendingDocument.objects.filter(type__key="proof_legal_guardianship").first()
        self.assertEqual(proof_legal_guardianship.document_number, "128dj")
        self.assertEqual(proof_legal_guardianship.individual, second_child)
        self.assertEqual(proof_legal_guardianship.rdi_merge_status, "PENDING")
