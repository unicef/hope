from operator import itemgetter

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.validators import (
    KoboProjectImportDataInstanceValidator,
)


class TestKoboSaveValidatorsMethods(TestCase):
    databases = ("default", "registration_datahub")
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)
    VALID_JSON = [
        {
            "_notes": [],
            "wash_questions/score_num_items": "8",
            "wash_questions/bed_hhsize": "NaN",
            "monthly_income_questions/total_inc_h_f": "0",
            "household_questions/m_0_5_age_group_h_c": "0",
            "_xform_id_string": "aPkhoRMrkkDwgsvWuwi39s",
            "_bamboo_dataset_id": "",
            "_tags": [],
            "health_questions/pregnant_member_h_c": "0",
            "health_questions/start": "2020-04-28T17:34:22.979+02:00",
            "health_questions/end": "2020-05-28T18:56:33.979+02:00",
            "household_questions/first_registration_date_h_c": "2020-07-18",
            "household_questions/f_0_5_disability_h_c": "0",
            "household_questions/size_h_c": "1",
            "household_questions/country_h_c": "AFG",
            "monthly_expenditures_questions/total_expense_h_f": "0",
            "individual_questions": [
                {
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "40",
                    "individual_questions/first_registration_date_i_c": "2020-07-18",
                    "individual_questions/more_information/marital_status_i_c": "married",
                    "individual_questions/individual_index": "1",
                    "individual_questions/birth_date_i_c": "1980-07-18",
                    "individual_questions/estimated_birth_date_i_c": "0",
                    "individual_questions/relationship_i_c": "head",
                    "individual_questions/gender_i_c": "male",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                    "individual_questions/full_name_i_c": "Test Testowy",
                    "individual_questions/is_only_collector": "NO",
                    "individual_questions/mas_treatment_i_f": "1",
                    "individual_questions/arm_picture_i_f": "signature-17_32_52.png",
                    "individual_questions/identification/tax_id_no_i_c": "45638193",
                    "individual_questions/identification/tax_id_issuer_i_c": "UKR",
                    "individual_questions/identification/bank_account_number_i_c": "UA3481939838393949",
                    "individual_questions/identification/bank_name_i_c": "Privat",
                }
            ],
            "wash_questions/score_bed": "5",
            "meta/instanceID": "uuid:512ca816-5cab-45a6-a676-1f47cfe7658e",
            "wash_questions/blanket_hhsize": "NaN",
            "household_questions/f_adults_disability_h_c": "0",
            "wash_questions/score_childclothes": "5",
            "household_questions/org_enumerator_h_c": "UNICEF",
            "household_questions/specific_residence_h_f": "returnee",
            "household_questions/org_name_enumerator_h_c": "Test",
            "household_questions/name_enumerator_h_c": "Test",
            "household_questions/consent_h_c": "0",
            "household_questions/consent_sharing_h_c": "UNICEF",
            "household_questions/m_12_17_age_group_h_c": "0",
            "household_questions/f_adults_h_c": "0",
            "household_questions/f_12_17_disability_h_c": "0",
            "household_questions/f_0_5_age_group_h_c": "0",
            "household_questions/m_6_11_age_group_h_c": "0",
            "wash_questions/score_womencloth": "5",
            "household_questions/f_12_17_age_group_h_c": "0",
            "wash_questions/score_jerrycan": "5",
            "start": "2020-05-28T17:32:43.054+02:00",
            "_attachments": [
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?"
                    "media_file=wnosal%2Fattachments%"
                    "2Fb83407aca1d647a5bf65a3383ee761d4%2F512ca816-5cab-45a6-a676-1f47cfe7658e"
                    "%2Fsignature-17_32_52.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal%"
                    "2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                    "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                    "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                    "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/"
                    "512ca816-5cab-45a6-a676-1f47cfe7658e/signature-17_32_52.png",
                    "instance": 101804069,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                    "%2F512ca816-5cab-45a6-a676-1f47cfe7658e%2Fsignature-17_32_52.png",
                    "id": 34814249,
                    "xform": 549831,
                }
            ],
            "_status": "submitted_via_web",
            "__version__": "vrBoKHPPCWpiRNvCbmnXCK",
            "household_questions/m_12_17_disability_h_c": "0",
            "wash_questions/score_tool": "5",
            "wash_questions/total_liter_yesterday_h_f": "0",
            "wash_questions/score_NFI_h_f": "5",
            "food_security_questions/FCS_h_f": "NaN",
            "wash_questions/jerrycan_hhsize": "NaN",
            "enumerator/name_enumerator": "Test",
            "wash_questions/score_bassin": "5",
            "_validation_status": {},
            "_uuid": "512ca816-5cab-45a6-a676-1f47cfe7658e",
            "household_questions/m_adults_h_c": "1",
            "consent/consent_sign_h_c": "signature-17_32_52.png",
            "wash_questions/score_total": "40",
            "_submitted_by": None,
            "individual_questions_count": "1",
            "end": "2020-05-28T17:34:22.979+02:00",
            "household_questions/pregnant_h_c": "0",
            "household_questions/m_6_11_disability_h_c": "0",
            "household_questions/m_0_5_disability_h_c": "0",
            "formhub/uuid": "b83407aca1d647a5bf65a3383ee761d4",
            "enumerator/org_enumerator": "unicef",
            "monthly_income_questions/round_total_income_h_f": "0",
            "wash_questions/score_cookingpot": "5",
            "household_questions/m_adults_disability_h_c": "0",
            "_submission_time": "2020-05-28T15:34:37",
            "household_questions/household_location/residence_status_h_c": "refugee",
            "_geolocation": [None, None],
            "monthly_expenditures_questions/round_total_expense_h_f": "0",
            "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
            "food_security_questions/cereals_tuber_score_h_f": "NaN",
            "household_questions/f_6_11_disability_h_c": "0",
            "wash_questions/score_blanket": "5",
            "household_questions/f_6_11_age_group_h_c": "0",
            "_id": 101804069,
        }
    ]

    INVALID_JSON = [
        {
            "wash_questions/score_num_items": "8",
            "wash_questions/bed_hhsize": "0.6666666666666666",
            "health_questions/unaccompanied_child_h_f": "0",
            "health_questions/breastfed_child_h_f": "0",
            "_tags": [],
            "food_security_questions/pulses_h_f": "2",
            "household_questions/household_location/admin2_h_c": "SO2502",
            "_xform_id_string": "a6bSLrF8gVRVzMPPuTnHMq",
            "wash_questions/score_bed": "1",
            "wash_questions/Child_clothes_h_f": "3",
            "wash_questions/bassin_h_f": "1",
            "wash_questions/score_jerrycan": "4",
            "wash_questions/waste_collect_freq_h_f": "monthly_collect",
            "coping_strategies/strategies_h_f": "borrowed_money sell_assets sent_child_beg",
            "wash_questions/score_NFI_h_f": "1.9375",
            "wash_questions/blanket_h_f": "4",
            "wash_questions/score_bassin": "2.5",
            "household_questions/household_location/country_h_c": "AFG",
            "wash_questions/door_light_vent_h_f": "1",
            "child_protection_questions/know_access_service_h_f": "level_mostly",
            "wash_questions/waste_disposal_h_f": "yes_bags",
            "food_security_questions/meals_yesterday_h_f": "3",
            "food_security_questions/meat_fish_h_f": "0",
            "wash_questions/odor_taste_color_h_f": "0",
            "monthly_income_questions/round_total_income_h_f": "123",
            "_submission_time": "2020-05-26T12:35:58",
            "household_questions/household_location/residence_status_h_c": "host",
            "_geolocation": [33.760882, 67.661513],
            "wash_questions/latrine_h_f": "not_shared",
            "child_protection_questions/risk_early_marriage_h_f": "level_mostly",
            "wash_questions/score_blanket": "0",
            "wash_questions/jerrycans_capacity_h_f": "5",
            "monthly_expenditures_questions/monthly_rent_h_f": "124",
            "monthly_income_questions/inc_enterprise_h_f": "123",
            "health_questions/pregnant_member_h_c": "0",
            "meta/instanceID": "uuid:dd376f5c-57c1-4f37-9b5d-482359f38598",
            "wash_questions/hygiene_materials_h_f": "soap_material",
            "food_security_questions/tubers_roots_h_f": "3",
            "wash_questions/score_childclothes": "2.5",
            "end": "2020-05-26T14:35:43.469+02:00",
            "wash_questions/total_liter_yesterday_h_f": "30",
            "level_debt_h_f": "111",
            "enumerator/name_enumerator": "test",
            "household_questions/household_location/admin1_h_c": "SO25",
            "wash_questions/score_tool": "1",
            "_validation_status": {},
            "food_security_questions/vegetables_h_f": "2",
            "_uuid": "dd376f5c-57c1-4f37-9b5d-482359f38598",
            "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
            "food_security_questions/sugarsweet_h_f": "0",
            "wash_questions/score_cookingpot": "3.5",
            "child_protection_questions/children_safe_h_f": "level_mostly",
            "child_protection_questions/child_not_at_fault_h_f": "level_never",
            "child_protection_questions/believe_better_life_h_f": "level_mostly",
            "child_protection_questions/sexviolence_survivor_not_shame_h_f": "level_never",
            "wash_questions/score_total": "15.5",
            "wash_questions/blanket_hhsize": "1.3333333333333333",
            "wash_questions/trips_to_fetch_water_h_f": "2",
            "monthly_expenditures_questions/monthly_utilities_h_f": "22",
            "wash_questions/jerrycan_hhsize": "1.6666666666666667",
            "individual_questions_count": "3",
            "enumerator/org_enumerator": "unicef",
            "wash_questions/volume_container_h_f": "15",
            "wash_questions/Cooking_pot_h_f": "1",
            "_notes": [],
            "food_security_questions/oilfat_h_f": "1",
            "_bamboo_dataset_id": "",
            "child_protection_questions/ok_parent_hit_child_h_f": "level_never",
            "wash_questions/seat_handrail_for_disabled_h_f": "0",
            "monthly_expenditures_questions/total_expense_h_f": "157",
            "individual_questions": [
                {
                    "individual_questions/individual_vulnerabilities/wellbeing_index/relaxed_h_f": "1",
                    "individual_questions/individual_vulnerabilities/wellbeing_index/fresh_h_f": "2",
                    "individual_questions/birth_date_i_c": "1980-07-16",
                    "individual_questions/more_information/birth_certificate_no_i_c": "123123123",
                    "individual_questions/individual_vulnerabilities/memory_disability_i_f": "lot_difficulty",
                    "individual_questions/more_information/phone_no_i_c": "+12123123123",
                    "individual_questions/individual_vulnerabilities/formal_school_i_f": "0",
                    "individual_questions/individual_vulnerabilities/observed_disability_i_f": "memory",
                    "individual_questions/individual_vulnerabilities/wellbeing_index/active_h_f": "1",
                    "individual_questions/family_name_i_c": "Testowski",
                    "individual_questions/individual_vulnerabilities/wellbeing_index/interested_h_f": "4",
                    "individual_questions/individual_index": "1",
                    "individual_questions/full_name_i_c": "Test Testowski",
                    "individual_questions/relationship_i_c": "head",
                    "individual_questions/individual_vulnerabilities/wellbeing_index/cheer_h_f": "2",
                    "individual_questions/gender_i_c": "male",
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "40",
                    "individual_questions/given_name_i_c": "Test",
                    "individual_questions/more_information/marital_status_i_c": "married",
                    "individual_questions/more_information/id_type_i_c": "birth_certificate",
                    "individual_questions/individual_vulnerabilities/selfcare_disability_i_f": "some_difficulty",
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "0",
                    "individual_questions/estimated_birth_date_i_c": "0",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "disabled",
                    "individual_questions/mas_treatment_i_f": "1",
                    "individual_questions/arm_picture_i_f": "signature-12_13_0.png",
                },
                {
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "37",
                    "individual_questions/given_name_i_c": "Tes",
                    "individual_questions/gender_i_c": "female",
                    "individual_questions/more_information/marital_status_i_c": "married",
                    "individual_questions/more_information/pregnant_i_f": "0",
                    "individual_questions/family_name_i_c": "Testowski",
                    "individual_questions/more_information/phone_no_i_c": "+49432123422",
                    "individual_questions/individual_vulnerabilities/formal_school_i_f": "0",
                    "individual_questions/individual_index": "2",
                    "individual_questions/full_name_i_c": "Tes Testowski",
                    "individual_questions/relationship_i_c": "wife_husband",
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "0",
                    "individual_questions/estimated_birth_date_i_c": "0",
                    "individual_questions/more_information/id_type_i_c": "birth_certificate",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                    "individual_questions/more_information/birth_certificate_no_i_c": "4442124124",
                    "individual_questions/birth_date_i_c": "1983-06-20",
                    "individual_questions/mas_treatment_i_f": "1",
                    "individual_questions/arm_picture_i_f": "signature-12_13_0.png",
                },
                {
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "23",
                    "individual_questions/given_name_i_c": "Tesa",
                    "individual_questions/more_information/marital_status_i_c": "single",
                    "individual_questions/more_information/pregnant_i_f": "0",
                    "individual_questions/family_name_i_c": "Testowski",
                    "individual_questions/more_information/phone_no_i_c": "+48535131412",
                    "individual_questions/individual_index": "3",
                    "individual_questions/birth_date_i_c": "1997-06-18",
                    "individual_questions/relationship_i_c": "son_daughter",
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "0",
                    "individual_questions/estimated_birth_date_i_c": "0",
                    "individual_questions/gender_i_c": "female",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                    "individual_questions/full_name_i_c": "Tesa Testowski",
                    "individual_questions/mas_treatment_i_f": "1",
                    "individual_questions/arm_picture_i_f": "signature-12_13_0.png",
                },
            ],
            "health_questions/recent_diarrehea_child_h_f": "0",
            "wash_questions/water_source_h_f": "piped_water",
            "living_conditions_questions/total_dwellers_h_f": "3",
            "living_conditions_questions/one_room_dwellers_h_f": "3",
            "monthly_expenditures_questions/monthly_food_h_f": "11",
            "household_questions/household_location/address_h_c": "Adr test 12",
            "household_questions/specific_residence_h_f": "returnee",
            "wash_questions/score_womencloth": "1",
            "_status": "submitted_via_web",
            "food_security_questions/fruits_h_f": "4",
            "food_security_questions/FCS_h_f": "34.5",
            "child_protection_questions/ok_teacher_hit_child_h_f": "level_never",
            "monthly_income_questions/gen_enterprise_h_f": "by_father",
            "_submitted_by": None,
            "wash_questions/latrine_connect_h_f": "pit_connection",
            "living_conditions_questions/living_situation_h_f": "own",
            "living_conditions_questions/total_households_h_f": "1",
            "wash_questions/beds_h_f": "2",
            "humanitarian_assistance_questions/assistance_h_f": "0",
            "child_protection_questions/leave_school_to_work_h_f": "level_rarely",
            "food_security_questions/dairy_h_f": "3",
            "wash_questions/days_no_water_h_f": "0",
            "living_conditions_questions/number_of_rooms_h_f": "3",
            "household_questions/hh_size_h_c": "3",
            "wash_questions/Women_clothes_h_f": "4",
            "food_security_questions/cereals_h_f": "2",
            "wash_questions/sufficient_water_h_f": "sufficientwater",
            "health_questions/recent_illness_child_h_f": "0",
            "child_protection_questions/meet_child_needs_h_f": "level_sometimes",
            "__version__": "vdGkCVQKjXNwcfpwHAPYmc",
            "monthly_income_questions/total_inc_h_f": "123",
            "child_protection_questions/law_against_underage_work_h_f": "level_rarely",
            "consent/consent_sign_h_c": "signature-12_13_0.png",
            "start": "2020-05-26T12:11:01.475+02:00",
            "formhub/uuid": "59f3ce8716a0487bb2f82b10a4f3e8e3",
            "household_questions/household_location/hh_geopoint_h_c": "33.760882 67.661513 0 0",
            "household_questions/org_enumerator_h_c": "UNICEF",
            "household_questions/org_name_enumerator_h_c": "Test",
            "household_questions/name_enumerator_h_c": "Test",
            "household_questions/consent_h_c": "0",
            "household_questions/consent_sharing_h_c": "UNICEF",
            "wash_questions/Agric_tool_h_f": "4",
            "_attachments": [
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info"
                    "/media/small?media_file=wnosal%2F"
                    "attachments%2F59f3ce8716a0487bb2f82"
                    "b10a4f3e8e3%2Fdd376f5c-57c1-4f37-9b"
                    "5d-482359f38598%2F"
                    "signature-12_13_0.png",
                    "download_large_url": "https://kc.humanitarianresponse.info"
                    "/media/large?media_file=wnosal%2F"
                    "attachments%2F59f3ce8716a0487bb2f82"
                    "b10a4f3e8e3%2Fdd376f5c-57c1-4f37-"
                    "9b5d-482359f38598%2F"
                    "signature-12_13_0.png",
                    "download_url": "https://kc.humanitarianresponse.info/"
                    "media/original?media_file="
                    "wnosal%2Fattachments%2F59f3ce8716a0487bb2"
                    "f82b10a4f3e8e3%2Fdd376f5c-57c1-4f37-9b5d-"
                    "482359f38598%2Fsignature-12_13_0.png",
                    "filename": "wnosal/attachments/59f3ce8716a0487bb2f82b10a4"
                    "f3e8e3/dd376f5c-57c1-4f37-9b5d-482359f38598/"
                    "signature-12_13_0.png",
                    "instance": 101482856,
                    "download_medium_url": "https://kc.humanitarianresponse."
                    "info/media/medium?media_file="
                    "wnosal%2Fattachments%2F59f3ce8716"
                    "a0487bb2f82b10a4f3e8e3%2Fdd376f5c-"
                    "57c1-4f37-9b5d-482359f38598%2F"
                    "signature-12_13_0.png",
                    "id": 34715446,
                    "xform": 548070,
                }
            ],
            "monthly_expenditures_questions/round_total_expense_h_f": "157",
            "wash_questions/sewage_overflow_h_f": "no_overflow",
            "food_security_questions/cereals_tuber_score_h_f": "5",
            "_id": 101482856,
        }
    ]

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()

    def test_image_validator(self):
        # test for valid value
        valid_attachments = [
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/"
                "media/small?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13eb8"
                "ec5d49%2Fb41093c6-94f6-418c-8224-04cb5e"
                "8a42dd%2Fsignature-17_10_32.png",
                "download_large_url": "https://kc.humanitarianresponse.info/"
                "media/large?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13eb8"
                "ec5d49%2Fb41093c6-94f6-418c-8224-04cb5e"
                "8a42dd%2Fsignature-17_10_32.png",
                "download_url": "https://kc.humanitarianresponse.info/media/"
                "original?media_file=wnosal%2Fattachments%2Ff1f"
                "5b29d931442d3abf0c13eb8ec5d49%2Fb41093c6-94f6-"
                "418c-8224-04cb5e8a42dd%2F"
                "signature-17_10_32.png",
                "filename": "wnosal/attachments/f1f5b29d931442d3abf0c13eb8ec5d"
                "49/b41093c6-94f6-418c-8224-04cb5e8a42dd"
                "/signature-17_10_32.png",
                "instance": 101800316,
                "download_medium_url": "https://kc.humanitarianresponse.info/"
                "media/medium?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13e"
                "b8ec5d49%2Fb41093c6-94f6-418c-8224-04c"
                "b5e8a42dd%2Fsignature-17_10_32.png",
                "id": 34813696,
                "xform": 549819,
            }
        ]
        validator = KoboProjectImportDataInstanceValidator()
        result = validator.image_validator("signature-17_10_32.png", "consent_sign_h_c", valid_attachments)
        self.assertIsNone(result, None)

        # test for invalid value
        invalid_attachments = [
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/"
                "media/small?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13eb"
                "8ec5d49%2Fb41093c6-94f6-418c-8224-04cb5"
                "e8a42dd%2Fsignature-20_32_17.png",
                "download_large_url": "https://kc.humanitarianresponse.info/"
                "media/large?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13eb"
                "8ec5d49%2Fb41093c6-94f6-418c-8224-04cb5"
                "e8a42dd%2Fsignature-20_32_17.png",
                "download_url": "https://kc.humanitarianresponse.info/media/"
                "original?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13eb8ec5d4"
                "9%2Fb41093c6-94f6-418c-8224-04cb5e8a42dd%2F"
                "signature-20_32_17.png",
                "filename": "wnosal/attachments/f1f5b29d931442d3abf0c13eb8ec5"
                "d49/b41093c6-94f6-418c-8224-04cb5e8a42dd"
                "/signature-20_32_17.png",
                "instance": 171833527,
                "download_medium_url": "https://kc.humanitarianresponse.info/"
                "media/medium?media_file=wnosal%2F"
                "attachments%2Ff1f5b29d931442d3abf0c13"
                "eb8ec5d49%2Fb41093c6-94f6-418c-8224-"
                "04cb5e8a42dd%2Fsignature-20_32_17.png",
                "id": 41517596,
                "xform": 449127,
            }
        ]
        result = validator.image_validator("signature-17_10_32.png", "consent_sign_h_c", invalid_attachments)
        expected = "Specified image signature-17_10_32.png for field " "consent_sign_h_c is not in attachments"
        self.assertEqual(result, expected)

        # test for empty value
        result = validator.image_validator("signature-17_10_32.png", "consent_sign_h_c", [])
        expected = "Specified image signature-17_10_32.png for field " "consent_sign_h_c is not in attachments"
        self.assertEqual(result, expected)

        # test invalid file extension
        result = validator.image_validator("signature-17_10_32.txt", "consent_sign_h_c", [])
        expected = "Specified image signature-17_10_32.txt for field " "consent_sign_h_c is not a valid image file"
        self.assertEqual(result, expected)

    def test_geopoint_validator(self):
        valid_geolocations = (
            "33.937574 67.709401 100 100",
            "1.22521 29.68428",
            "-75.10735 -116.99551",
        )
        invalid_geolocations = (
            "11, 12",
            "a, b",
            [33.123, "a"],
            [],
            None,
        )
        validator = KoboProjectImportDataInstanceValidator()
        for valid_option in valid_geolocations:
            self.assertIsNone(
                validator.geopoint_validator(
                    valid_option,
                    "hh_geopoint_h_c",
                )
            )

        for invalid_option in invalid_geolocations:
            self.assertEqual(
                validator.geopoint_validator(
                    invalid_option,
                    "hh_geopoint_h_c",
                ),
                f"Invalid geopoint {invalid_option} for field hh_geopoint_h_c",
            )

    def test_date_validator(self):
        test_data = (
            {"args": ("2020-05-28T17:13:31.590+02:00", "birth_date_i_c"), "expected": None},
            {"args": ("2020-05-28", "birth_date_i_c"), "expected": None},
            {
                "args": ("2020-13-32T25:13:31.590+02:00", "birth_date_i_c"),
                "expected": (
                    "Invalid datetime/date 2020-13-32T25:13:31.590+02:00 for "
                    "field birth_date_i_c, "
                    "accepted formats: datetime ISO 8601, date YYYY-MM-DD"
                ),
            },
            {
                "args": (None, "birth_date_i_c"),
                "expected": (
                    "Invalid datetime/date None for "
                    "field birth_date_i_c, "
                    "accepted formats: datetime ISO 8601, date YYYY-MM-DD"
                ),
            },
        )
        validator = KoboProjectImportDataInstanceValidator()
        for data in test_data:
            result = validator.date_validator(*data["args"])
            self.assertEqual(result, data["expected"])

    def test_get_field_type_error(self):
        attachments = self.VALID_JSON[0]["_attachments"]

        test_data = (
            # INTEGER
            {"args": ("size_h_c", 4, attachments), "expected": None},
            {
                "args": ("size_h_c", "four", attachments),
                "expected": {
                    "header": "size_h_c",
                    "message": "Invalid value four of type str for field " "size_h_c of type int",
                },
            },
            # STRING
            {"args": ("address_h_c", "Street 123", attachments), "expected": None},
            {"args": ("address_h_c", 123, attachments), "expected": None},
            # BOOL
            {"args": ("returnee_h_c", True, attachments), "expected": None},
            {"args": ("returnee_h_c", "True", attachments), "expected": None},
            {"args": ("returnee_h_c", False, attachments), "expected": None},
            {"args": ("returnee_h_c", "False", attachments), "expected": None},
            {"args": ("returnee_h_c", 1, attachments), "expected": None},
            {"args": ("returnee_h_c", "1", attachments), "expected": None},
            {"args": ("returnee_h_c", 0, attachments), "expected": None},
            {"args": ("returnee_h_c", "0", attachments), "expected": None},
            {
                "args": ("returnee_h_c", "123", attachments),
                "expected": {
                    "header": "returnee_h_c",
                    "message": "Invalid value 123 of type str for field " "returnee_h_c of type bool",
                },
            },
            {
                "args": ("returnee_h_c", 123, attachments),
                "expected": {
                    "header": "returnee_h_c",
                    "message": "Invalid value 123 of type int for field " "returnee_h_c of type bool",
                },
            },
            # SELECT ONE
            {"args": ("gender_i_c", "MALE", attachments), "expected": None},
            {
                "args": ("gender_i_c", "YES", attachments),
                "expected": {"header": "gender_i_c", "message": "Invalid choice YES for field gender_i_c"},
            },
            # DATE
            {
                "args": (
                    "birth_date_i_c",
                    "2020-05-28T17:13:31.590+02:00",
                    attachments,
                ),
                "expected": None,
            },
            {
                "args": ("birth_date_i_c", "2020/05/28", attachments),
                "expected": {
                    "header": "birth_date_i_c",
                    "message": "Invalid datetime/date 2020/05/28 for field "
                    "birth_date_i_c, accepted formats: "
                    "datetime ISO 8601, date YYYY-MM-DD",
                },
            },
            # GEOPOINT
            {"args": ("hh_geopoint_h_c", "12.123 13.123", attachments), "expected": None},
            {
                "args": (
                    "hh_geopoint_h_c",
                    "GeoPoint 12.123, 32.123",
                    attachments,
                ),
                "expected": {
                    "header": "hh_geopoint_h_c",
                    "message": "Invalid geopoint GeoPoint 12.123, 32.123 " "for field hh_geopoint_h_c",
                },
            },
            # IMAGE
            {
                "args": ("consent_sign_h_c", "signature-17_10_3.png", attachments),
                "expected": {
                    "header": "consent_sign_h_c",
                    "message": "Specified image signature-17_10_3.png "
                    "for field consent_sign_h_c is not in attachments",
                },
            },
        )
        validator = KoboProjectImportDataInstanceValidator()
        for data in test_data:
            result = validator._get_field_type_error(*data["args"])
            self.assertEqual(result, data["expected"])

    def test_validate_everything(self):
        validator = KoboProjectImportDataInstanceValidator()
        business_area = BusinessArea.objects.first()

        result = validator.validate_everything(self.VALID_JSON, business_area)
        self.assertEqual(result, [])

        result = validator.validate_everything(self.INVALID_JSON, business_area)

        result.sort(key=itemgetter("header"))
        expected = [
            {"header": "admin1_h_c", "message": "Invalid choice SO25 for field admin1_h_c"},
            {"header": "admin2_h_c", "message": "Invalid choice SO2502 for field admin2_h_c"},
            {
                "header": "birth_certificate_no_i_c",
                "message": "Issuing country for birth_certificate_no_i_c is required, when any document data are provided",
            },
            {
                "header": "birth_certificate_no_i_c",
                "message": "Issuing country for birth_certificate_no_i_c is required, when any document data are provided",
            },
            {"header": "role_i_c", "message": "Only one person can be a primary collector"},
            {"header": "size_h_c", "message": "Missing household required field size_h_c"},
        ]
        self.assertEqual(result, expected)
