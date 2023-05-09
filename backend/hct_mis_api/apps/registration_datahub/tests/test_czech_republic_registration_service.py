import datetime

from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_NATIONAL_ID, IDENTIFICATION_TYPE_NATIONAL_PASSPORT, IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.czech_republic_flex_registration_service import (
    CzechRepublicFlexRegistration,
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

        ImportedDocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            label=IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
        )

        ImportedDocumentType.objects.create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE],
            label=IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE,
        )

        BusinessArea.objects.create(
            **{
                "code": "BOCZ",
                "name": "Czech Republic",
                "region_name": "CZE",
                "slug": "czech-republic",
                "has_data_sharing_agreement": True,
            },
        )

        geo_models.Country.objects.create(name="Czechia")

        consent = [
            {
                "consent_h_c": True,
                "consent_sharing_h_c": True,
                "government_partner": "some_partner",
                "consent_sharing_h_c_1": True,
                "consent_sharing_h_c_2": True
            }
        ]

        needs_assessment = [
            {
                "65_count_h_f": 2,
                "assistance_h_f": "y",
                "adults_count_h_f": 2,
                "receiving_mop_h_f": "y",
                "school_enrolled_i_f": "no",
                "children_below_18_h_f": 2,
                "access_health_rate_h_f": "A little Difficult",
                "additional_support_h_f": "y",
                "access_education_rate_h_f": "A little Difficult",
                "access_social_services_rate_h_f": "Somewhat Easy",
                "access_leisure_activities_rate_h_f": "Very Difficult",
                "in_state_provided_accommodation_h_f": "yes_emergency_accomodation"
            }
        ]

        household_address = [
            {
                "admin1_h_c": "CZ020",
                "admin2_h_c": "CZ0201",
                "address_h_c": "Street Name/55",
                "village_h_c": "TEST City",
                "zip_code_h_c": "12344"
            }
        ]

        primary_carer_info = [
            {
                "role_i_c": "primary",
                "gender_i_c": "male",
                "id_type_i_c": "national_id",
                "phone_no_i_c": "+420123123123",
                "birth_date_i_c": "1989-06-13",
                "given_name_i_c": "TEST",
                "employment_type": "fixed_salary",
                "family_name_i_c": "TEST",
                "work_status_i_c": "y",
                "bank_account_h_f": "y",
                "relationship_i_c": "other",
                "other_nationality": "Russian",
                "country_origin_h_c": "other",
                "immediate_relative": True,
                "national_id_no_i_c": "12345",
                "national_passport_i_c": "",
                "bank_account_number": "CZ6508000000192000145399",
                "confirm_phone_number": "+420123123123",
                "preferred_language_i_c": "uk-ua",
                "bank_account_number_h_f": "CZ6508000000192000145399",
                "czech_formal_employment": "part_time",
                "other_communication_language": ["hu-hu"],
                "primary_carer_is_legal_guardian": "n"
            }
        ]

        children_information = [
            {
                "gender_i_c": "female",
                "id_type_i_c": "national_id",
                "birth_date_i_c": "2023-04-30",
                "disability_i_c": "disabled",
                "follow_up_flag": ["legal_guardianship_documents"],
                "given_name_i_c": "TEST",
                "family_name_i_c": "TEST",
                "other_id_no_i_c": "TPV123",
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
                "has_disability_card_and_medical_cert": "Has Both"
            }
        ]

        legal_guardian_information = [
            {
                "gender_i_c": "male",
                "id_type_i_c": "national_passport",
                "phone_no_i_c": "+420123123123",
                "birth_date_i_c": "1998-12-27",
                "given_name_i_c": "TEST",
                "family_name_i_c": "TEST",
                "relationship_i_c": "head",
                "confirm_phone_number": "+420123123123",
                "national_passport_i_c": "1234",
                "national_id_no_i_c": "",
                "legal_guardia_not_primary_carer": "y"
            }
        ]

        records = [
            Record(
                registration=17,
                timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
                source_id=1,
                fields={
                    "consent": consent,
                    "needs-assessment": needs_assessment,
                    "household-address": household_address,
                    "primary-carer-info": primary_carer_info,
                    "children-information": children_information,
                    "legal-guardian-information": legal_guardian_information
                },
            )
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = CzechRepublicFlexRegistration()
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        # self.records[0].refresh_from_db()
        # self.assertEqual(
        #     Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count(), 2
        # )
        #
        # self.assertEqual(ImportedHousehold.objects.count(), 1)
        # self.assertEqual(ImportedIndividualRoleInHousehold.objects.count(), 1)
        # self.assertEqual(ImportedBankAccountInfo.objects.count(), 1)
        # self.assertEqual(ImportedDocument.objects.count(), 1)
        #
        # imported_household = ImportedHousehold.objects.first()
        # self.assertEqual(imported_household.admin1, "LK1")
        # self.assertEqual(imported_household.admin1_title, "SriLanka admin1")
        # self.assertEqual(imported_household.admin2, "LK11")
        # self.assertEqual(imported_household.admin2_title, "SriLanka admin2")
        # self.assertEqual(imported_household.admin3, "LK1163")
        # self.assertEqual(imported_household.admin3_title, "SriLanka admin3")
        # self.assertEqual(imported_household.admin4, "LK1163020")
        # self.assertEqual(imported_household.admin4_title, "SriLanka admin4")
        # self.assertEqual(imported_household.admin_area, "LK1163020")
        # self.assertEqual(imported_household.admin_area_title, "SriLanka admin4")
        #
        # self.assertEqual(
        #     ImportedIndividual.objects.filter(relationship="HEAD").first().flex_fields, {"has_nic_number_i_c": "n"}
        # )
        #
        # self.assertEqual(
        #     ImportedIndividual.objects.filter(full_name="Dome").first().flex_fields,
        #     {
        #         "confirm_nic_number": "123456789V",
        #         "branch_or_branch_code": "7472_002",
        #         "who_answers_this_phone": "alternate collector",
        #         "confirm_alternate_collector_phone_number": "+94788908046",
        #         "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
        #     },
        # )
        # self.assertEqual(ImportedIndividual.objects.filter(full_name="Dome").first().email, "email999@mail.com")
