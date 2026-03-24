import datetime

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    DocumentTypeFactory,
    OrganizationFactory,
    ProgramFactory,
    ProjectFactory,
    RecordFactory,
    RegistrationFactory,
    UserFactory,
)
from hope.apps.household.const import (
    DISABLED,
    FEMALE,
    GOVERNMENT_PARTNER,
    MALE,
    NOT_DISABLED,
    PRIVATE_PARTNER,
)
from hope.contrib.aurora.services.czech_republic_flex_registration_service import CzechRepublicFlexRegistration
from hope.models import (
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
    country as geo_models,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def czech_record_fields() -> dict:
    return {
        "consent": [
            {
                "consent_h_c": "y",
                "consent_sharing_h_c": True,
                "government_partner": "",
                "consent_sharing_h_c_1": "y",
                "consent_sharing_h_c_2": "n",
            }
        ],
        "needs-assessment": [
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
        ],
        "household-address": [
            {
                "address_h_c": "Opo\u010d\u00ednsk\u00e1 375",
                "admin1_h_c": "CZ010",
                "admin2_h_c": "CZ0109",
                "village_h_c": "Praha",
                "zip_code_h_c": "19017",
            }
        ],
        "primary-carer-info": [
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
        ],
        "children-information": [
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
        ],
        "legal-guardian-information": [
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
        ],
    }


@pytest.fixture
def czech_context(czech_record_fields: dict) -> dict:
    CountryFactory(name="Czechia", short_name="Czechia", iso_code2="CZ", iso_code3="CZE", iso_num="0203")
    document_mapping = {
        "birth_certificate": "Birth Certificate",
        "disability_card": "Disability Card",
        "national_id": "National ID",
        "national_passport": "National Passport",
        "medical_certificate": "Medical Certificate",
        "temporary_protection_visa": "Temporary Protection Visa",
        "proof_legal_guardianship": "Proof of Legal Guardianship",
    }
    for key, label in document_mapping.items():
        DocumentTypeFactory(key=key, label=label)
    business_area = BusinessAreaFactory(slug="some-czech-slug")
    data_collecting_type = DataCollectingTypeFactory(label="someLabel", code="some_label")
    data_collecting_type.limit_to.add(business_area)
    program = ProgramFactory(
        status="ACTIVE",
        data_collecting_type=data_collecting_type,
        biometric_deduplication_enabled=True,
        business_area=business_area,
    )
    organization = OrganizationFactory(business_area=business_area, slug=business_area.slug)
    project = ProjectFactory(name="fake_project", organization=organization, programme=program)
    registration = RegistrationFactory(name="fake_registration", project=project, source_id=25)
    user = UserFactory()
    record = RecordFactory(
        registration=registration.source_id,
        timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
        source_id=1,
        fields=czech_record_fields,
        files=None,
    )
    return {
        "program": program,
        "registration": registration,
        "record": record,
        "user": user,
    }


def test_import_data_to_datahub(czech_context: dict) -> None:
    registration = czech_context["registration"]
    record = czech_context["record"]
    user = czech_context["user"]
    program = czech_context["program"]

    service = CzechRepublicFlexRegistration(registration)
    rdi = service.create_rdi(user, f"czech_republic rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id])

    record.refresh_from_db()
    assert PendingHousehold.objects.count() == 1
    assert PendingHousehold.objects.filter(program=rdi.program).count() == 1

    household = PendingHousehold.objects.first()
    assert household.consent is True
    assert household.consent_sharing == [GOVERNMENT_PARTNER, PRIVATE_PARTNER]
    assert household.country == geo_models.Country.objects.get(iso_code2="CZ")
    assert household.country_origin == geo_models.Country.objects.get(iso_code2="CZ")
    assert household.size == 4
    assert household.zip_code == "19017"
    assert household.village == "Praha"
    assert household.head_of_household == PendingIndividual.objects.get(full_name="Ivan Drago")
    assert household.rdi_merge_status == "PENDING"

    registration_data_import = household.registration_data_import
    assert registration_data_import.program == program

    head_of_household = PendingIndividual.objects.get(full_name="Ivan Drago")
    assert head_of_household.sex == MALE
    assert head_of_household.phone_no == "+420123123666"
    assert head_of_household.disability == NOT_DISABLED
    assert head_of_household.work_status == "1"
    assert head_of_household.rdi_merge_status == "PENDING"

    primary_collector = PendingIndividual.objects.get(full_name="Tetiana Symkanych")
    assert primary_collector.sex == FEMALE
    assert primary_collector.phone_no == "+420774844183"
    assert primary_collector.disability == NOT_DISABLED
    assert primary_collector.work_status == "0"
    assert primary_collector.rdi_merge_status == "PENDING"
    assert PendingIndividualRoleInHousehold.objects.count() == 1

    primary_role = PendingIndividualRoleInHousehold.objects.first()
    assert primary_role.individual == primary_collector
    assert primary_role.household == household

    first_child = PendingIndividual.objects.get(given_name="John")
    assert first_child.sex == MALE
    assert str(first_child.birth_date) == "2013-07-04"
    assert first_child.disability == NOT_DISABLED
    assert first_child.rdi_merge_status == "PENDING"

    second_child = PendingIndividual.objects.get(given_name="TEST")
    assert second_child.sex == FEMALE
    assert str(second_child.birth_date) == "2023-04-30"
    assert second_child.disability == DISABLED
    assert second_child.rdi_merge_status == "PENDING"

    birth_certificate = PendingDocument.objects.filter(type__key="birth_certificate").first()
    assert birth_certificate.document_number == "262873"
    assert PendingDocument.objects.filter(type__key="disability_card").count() == 1
    assert PendingDocument.objects.filter(type__key="medical_certificate").count() == 1
    assert PendingDocument.objects.filter(type__key="temporary_protection_visa").count() == 1
    assert PendingDocument.objects.filter(type__key="proof_legal_guardianship").count() == 1
    assert PendingDocument.objects.filter(type__key="national_passport").count() == 2
    assert birth_certificate.rdi_merge_status == "PENDING"

    national_passport = PendingDocument.objects.filter(document_number="GB500567").first()
    assert national_passport.individual == primary_collector
    assert national_passport.rdi_merge_status == "PENDING"

    disability_card = PendingDocument.objects.filter(type__key="disability_card").first()
    assert disability_card.document_number == "1213"
    assert disability_card.individual == second_child
    assert disability_card.rdi_merge_status == "PENDING"

    medical_certificate = PendingDocument.objects.filter(type__key="medical_certificate").first()
    assert medical_certificate.document_number == "2321"
    assert medical_certificate.individual == second_child
    assert medical_certificate.expiry_date == datetime.datetime(2023, 5, 17, tzinfo=datetime.timezone.utc)
    assert medical_certificate.issuance_date == datetime.datetime(2023, 5, 1, tzinfo=datetime.timezone.utc)
    assert medical_certificate.rdi_merge_status == "PENDING"

    temporary_protection_visa = PendingDocument.objects.filter(type__key="temporary_protection_visa").first()
    assert temporary_protection_visa.document_number == "900541571"
    assert temporary_protection_visa.individual == first_child
    assert temporary_protection_visa.rdi_merge_status == "PENDING"

    proof_legal_guardianship = PendingDocument.objects.filter(type__key="proof_legal_guardianship").first()
    assert proof_legal_guardianship.document_number == "128dj"
    assert proof_legal_guardianship.individual == second_child
    assert proof_legal_guardianship.rdi_merge_status == "PENDING"
