import copy
import csv
import datetime
from io import StringIO
import json

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    DeliveryMechanismFactory,
    DocumentFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    FinancialServiceProviderFactory,
    OrganizationFactory,
    PendingDocumentFactory,
    PendingIndividualFactory,
    ProgramFactory,
    ProjectFactory,
    RecordFactory,
    RegistrationFactory,
    UserFactory,
)
from hope.admin.registration import RegistrationAdmin
from hope.apps.household.const import HEAD, MALE
from hope.contrib.aurora import models
from hope.contrib.aurora.services.nigeria_people_registration_service import NigeriaPeopleRegistrationService
from hope.models import (
    Document,
    FinancialInstitutionMapping,
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def nigeria_country() -> object:
    return CountryFactory(name="Nigeria", short_name="Nigeria", iso_code2="NG", iso_code3="NGA", iso_num="0566")


@pytest.fixture
def nigeria_admin_areas(nigeria_country: object) -> dict:
    area_type_1 = AreaTypeFactory(name="State", area_level=1, country=nigeria_country)
    area_type_2 = AreaTypeFactory(
        name="Local government area",
        area_level=2,
        country=nigeria_country,
        parent=area_type_1,
    )
    area_type_3 = AreaTypeFactory(name="Ward", area_level=3, country=nigeria_country, parent=area_type_2)
    area_1 = AreaFactory(name="Borno", p_code="NG002", area_type=area_type_1)
    area_2 = AreaFactory(name="Bama", p_code="NG002001", area_type=area_type_2, parent=area_1)
    area_3 = AreaFactory(name="Andara", p_code="NG002001007", area_type=area_type_3, parent=area_2)
    return {
        "area_type_1": area_type_1,
        "area_type_2": area_type_2,
        "area_type_3": area_type_3,
        "area_1": area_1,
        "area_2": area_2,
        "area_3": area_3,
    }


@pytest.fixture
def document_type() -> object:
    return DocumentTypeFactory(key="national_id", label="National ID")


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory(slug="some-ng-slug")


@pytest.fixture
def data_collecting_type(business_area: object) -> object:
    data_collecting_type = DataCollectingTypeFactory(label="someLabel", code="some_label")
    data_collecting_type.limit_to.add(business_area)
    return data_collecting_type


@pytest.fixture
def program(business_area: object, data_collecting_type: object) -> object:
    return ProgramFactory(
        status="ACTIVE",
        data_collecting_type=data_collecting_type,
        biometric_deduplication_enabled=True,
        business_area=business_area,
    )


@pytest.fixture
def organization(business_area: object) -> object:
    return OrganizationFactory(business_area=business_area, slug=business_area.slug)


@pytest.fixture
def project(organization: object, program: object) -> object:
    return ProjectFactory(name="fake_project", organization=organization, programme=program)


@pytest.fixture
def registration(project: object) -> object:
    return RegistrationFactory(name="fake_registration", project=project, mapping={})


@pytest.fixture
def record_files() -> dict:
    return {
        "individual-details": [
            {
                "photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP/////////////////////////////////////////////"
                "/////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAA"
                "AAAAAAAAP/aAAgBAQABPxA=",
                "national_id_photo_i_c": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP///////////////////////////////////"
                "///////////////////////////////////////////////////wgALCAABAAEBAREA/8QAF"
                "BABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            }
        ]
    }


@pytest.fixture
def record_fields() -> dict:
    return {
        "household-info": [{"admin1_h_c": "NG002", "admin2_h_c": "NG002001", "admin3_h_c": "NG002001007"}],
        "intro-and-consent": [{"consent_h_c": True, "enumerator_code": "SHEAbi5350", "who_to_register": "myself"}],
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
                "frontline_worker_designation_i_f": "H2HCL",
            }
        ],
    }


def make_record_fields(
    record_fields: dict,
    *,
    account_number: str = "2087008012",
    national_id: str = "01234567891",
    given_name: str = "Giulio",
    email: str = "gfranco@unicef.org",
    birth_date: str = "1988-04-08",
) -> dict:
    fields = copy.deepcopy(record_fields)
    individual = fields["individual-details"][0]
    individual["account_details"]["number"] = account_number
    individual["national_id_no"] = national_id
    individual["national_id_no_i_c"] = national_id
    individual["given_name_i_c"] = given_name
    individual["email_i_c"] = email
    individual["birth_date_i_c"] = birth_date
    return fields


def make_record(
    record: object,
    record_fields: dict,
    record_files: dict,
    *,
    source_id: int,
    account_number: str,
    national_id: str,
    given_name: str,
    email: str,
    birth_date: str = "1988-04-08",
) -> object:
    return RecordFactory(
        registration=record.registration,
        timestamp=record.timestamp,
        source_id=source_id,
        files=json.dumps(record_files).encode(),
        fields=make_record_fields(
            record_fields,
            account_number=account_number,
            national_id=national_id,
            given_name=given_name,
            email=email,
            birth_date=birth_date,
        ),
    )


@pytest.fixture
def record(record_fields: dict, record_files: dict) -> object:
    return RecordFactory(
        registration=25,
        timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
        source_id=1,
        files=json.dumps(record_files).encode(),
        fields=record_fields,
    )


@pytest.fixture
def user() -> object:
    return UserFactory.create()


@pytest.fixture
def account_type() -> object:
    return AccountTypeFactory(key="bank", label="Bank", unique_fields=[])


@pytest.fixture
def financial_institutions() -> dict:
    return {
        "generic": FinancialInstitutionFactory(name="Generic Bank"),
        "nigeria": FinancialInstitutionFactory(name="Nigeria Bank"),
    }


@pytest.fixture
def financial_service_provider() -> object:
    delivery_mechanism = DeliveryMechanismFactory()
    return FinancialServiceProviderFactory(
        name="United Bank for Africa - Nigeria",
        delivery_mechanisms=[delivery_mechanism],
    )


@pytest.fixture
def financial_institution_mapping(
    financial_institutions: dict,
    financial_service_provider: object,
) -> object:
    return FinancialInstitutionMapping.objects.create(
        financial_service_provider=financial_service_provider,
        financial_institution=financial_institutions["nigeria"],
        code="000004",
    )


def test_get_national_id_field_name() -> None:
    mapping_default = {
        "defaults": {"individuals_key": "individual-details"},
        "individual-details": {
            "national_id_no_i_c": "document.doc_national-document_number",
        },
    }
    assert NigeriaPeopleRegistrationService._get_national_id_field_name(mapping_default) == "national_id_no_i_c"

    mapping_custom = {
        "defaults": {"individuals_key": "members"},
        "members": {
            "custom_nin": "document.doc_national-document_number",
        },
    }
    assert NigeriaPeopleRegistrationService._get_national_id_field_name(mapping_custom) == "custom_nin"

    mapping_without_national_id = {
        "defaults": {"individuals_key": "members"},
        "members": {
            "tax_id": "document.doc_tax-document_number",
        },
    }
    assert (
        NigeriaPeopleRegistrationService._get_national_id_field_name(mapping_without_national_id)
        == "national_id_no_i_c"
    )


def test_record_has_duplicate_national_id(
    registration: object,
    user: object,
    program: object,
    document_type: object,
) -> None:
    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")

    mapping = {
        "defaults": {"individuals_key": "individual-details"},
        "individual-details": {"national_id_no_i_c": "document.doc_national-document_number"},
    }

    assert service._record_has_duplicate_national_id({}, rdi, mapping) is False
    assert service._record_has_duplicate_national_id({"national_id_no_i_c": "UNIQUE-1"}, rdi, mapping) is False

    pending_individual = PendingIndividualFactory(
        program=program,
        business_area=program.business_area,
        registration_data_import=rdi,
    )
    PendingDocumentFactory(
        individual=pending_individual,
        program=program,
        type=document_type,
        document_number="PENDING-EXISTS",
    )
    assert service._record_has_duplicate_national_id({"national_id_no_i_c": "PENDING-EXISTS"}, rdi, mapping) is True

    DocumentFactory(
        program=program,
        type=document_type,
        document_number="MERGED-EXISTS",
        status=Document.STATUS_VALID,
    )
    assert service._record_has_duplicate_national_id({"national_id_no_i_c": "MERGED-EXISTS"}, rdi, mapping) is True


def test_record_has_duplicate_account_number_matches_exact_string_only(
    registration: object,
    user: object,
    program: object,
    account_type: object,
) -> None:
    assert account_type

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    mapping = service.get_mapping(registration.mapping)

    assert service._record_has_duplicate_account_number({}, rdi, mapping) is False
    assert (
        service._record_has_duplicate_account_number(
            {"account_details": {"number": "2087008012"}},
            rdi,
            mapping,
        )
        is False
    )

    pending_individual = PendingIndividualFactory(
        program=program,
        business_area=program.business_area,
        registration_data_import=rdi,
    )
    AccountFactory(individual=pending_individual, number="2087008012")

    assert (
        service._record_has_duplicate_account_number(
            {"account_details": {"number": "2087008012"}},
            rdi,
            mapping,
        )
        is True
    )
    assert (
        service._record_has_duplicate_account_number(
            {"account_details": {"number": "208 7008012"}},
            rdi,
            mapping,
        )
        is False
    )


def test_record_has_duplicate_account_number_ignores_other_program_accounts(
    registration: object,
    user: object,
    account_type: object,
) -> None:
    assert account_type

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    mapping = service.get_mapping(registration.mapping)
    AccountFactory(number="2087008012")

    assert (
        service._record_has_duplicate_account_number(
            {"account_details": {"number": "2087008012"}},
            rdi,
            mapping,
        )
        is False
    )


def test_import_data_to_datahub(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    financial_institutions: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id])

    assert PendingHousehold.objects.count() == 1
    assert PendingHousehold.objects.filter(program=rdi.program).count() == 1

    household = PendingHousehold.objects.first()
    assert household
    assert household.consent
    assert household.country.iso_code2 == "NG"
    assert household.country_origin.iso_code2 == "NG"
    assert household.head_of_household == PendingIndividual.objects.get(given_name="Giulio")
    assert household.rdi_merge_status == "PENDING"
    assert household.flex_fields == {"enumerator_code": "SHEAbi5350", "who_to_register": "myself"}

    registration_data_import = household.registration_data_import
    assert registration_data_import.program == rdi.program

    primary_collector = PendingIndividual.objects.get(id=household.head_of_household_id)
    assert primary_collector.phone_no is not None
    assert primary_collector.sex == MALE
    assert primary_collector.email == "gfranco@unicef.org"
    assert primary_collector.full_name == "Giulio D Franco"
    assert primary_collector.relationship == HEAD
    assert primary_collector.phone_no_alternative is not None
    assert primary_collector.flex_fields == {
        "frontline_worker_designation_i_f": "H2HCL",
        "national_id_no": "01234567891",
    }
    assert primary_collector.rdi_merge_status == "PENDING"
    assert primary_collector.photo.url is not None

    account = PendingAccount.objects.first()
    assert account
    assert account.account_data == {
        "number": "2087008012",
        "name": "United Bank for Africa",
        "code": "000004",
        "holder_name": "xxxx",
        "financial_institution_pk": str(financial_institutions["nigeria"].id),
        "financial_institution_name": str(financial_institutions["nigeria"].name),
    }
    assert account.account_type.key == "bank"
    assert account.financial_institution == financial_institutions["nigeria"]

    national_id = PendingDocument.objects.filter(document_number="01234567891").first()
    assert national_id
    assert national_id.individual == primary_collector
    assert national_id.rdi_merge_status == "PENDING"
    assert national_id.photo.url is not None


def test_import_data_skips_duplicate_national_id_in_same_rdi(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    financial_institutions: dict,
    record_fields: dict,
    record_files: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping
    assert financial_institutions

    duplicate_record_fields = copy.deepcopy(record_fields)
    duplicate_individual = duplicate_record_fields["individual-details"][0]
    duplicate_individual["email_i_c"] = "different.person@unicef.org"
    duplicate_individual["given_name_i_c"] = "Different"
    duplicate_individual["middle_name_i_c"] = "Z"
    duplicate_individual["family_name_i_c"] = "Person"
    duplicate_individual["phone_no_i_c"] = "+2348012345678"
    duplicate_individual["birth_date_i_c"] = "1991-05-06"
    duplicate_individual["national_id_no"] = "DIFFERENT_NON_MATCHING_FLEX_FIELD_VALUE"
    duplicate_individual["account_details"]["number"] = "2087008013"

    duplicate_record = RecordFactory(
        registration=record.registration,
        timestamp=record.timestamp,
        source_id=record.source_id + 1,
        files=json.dumps(record_files).encode(),
        fields=duplicate_record_fields,
    )

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id, duplicate_record.id])

    duplicate_record.refresh_from_db()
    assert duplicate_record.ignored is True
    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 1
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 1
    assert (
        PendingDocument.objects.filter(
            program=rdi.program,
            type=document_type,
            document_number="01234567891",
        ).count()
        == 1
    )


def test_import_data_skips_duplicate_account_number_in_same_batch(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    financial_institutions: dict,
    record_fields: dict,
    record_files: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping
    assert financial_institutions

    duplicate_record = make_record(
        record,
        record_fields,
        record_files,
        source_id=record.source_id + 1,
        account_number="2087008012",
        national_id="UNIQUE-NATIONAL-ID-2",
        given_name="Different",
        email="different.person@unicef.org",
    )

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id, duplicate_record.id])

    record.refresh_from_db()
    duplicate_record.refresh_from_db()
    rdi.refresh_from_db()
    assert record.status == record.STATUS_IMPORTED
    assert duplicate_record.ignored is True
    assert duplicate_record.error_message == NigeriaPeopleRegistrationService.DUPLICATE_ACCOUNT_NUMBER_REASON
    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 1
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 1
    assert PendingAccount.objects.filter(individual__registration_data_import=rdi, number="2087008012").count() == 1
    assert rdi.status == RegistrationDataImport.DEDUPLICATION


def test_import_data_does_not_skip_valid_duplicate_account_after_failed_record_in_same_batch(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    financial_institutions: dict,
    record_fields: dict,
    record_files: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping
    assert financial_institutions

    invalid_record = RecordFactory(
        registration=25,
        timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
        source_id=1,
        files=json.dumps(record_files).encode(),
        fields=make_record_fields(
            record_fields,
            account_number="2087008012",
            national_id="UNIQUE-NATIONAL-ID-FAILED",
            given_name="Invalid",
            email="invalid.person@unicef.org",
            birth_date="not-a-date",
        ),
    )
    valid_record = make_record(
        invalid_record,
        record_fields,
        record_files,
        source_id=2,
        account_number="2087008012",
        national_id="01234567891",
        given_name="Giulio",
        email="gfranco@unicef.org",
    )

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [invalid_record.id, valid_record.id])

    invalid_record.refresh_from_db()
    valid_record.refresh_from_db()
    assert invalid_record.status == invalid_record.STATUS_ERROR
    assert valid_record.status == valid_record.STATUS_IMPORTED
    assert valid_record.ignored is not True
    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 1
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 1
    assert PendingAccount.objects.filter(individual__registration_data_import=rdi, number="2087008012").count() == 1


def test_import_data_skips_record_if_account_number_already_imported(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    program: object,
    financial_institutions: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping
    assert financial_institutions

    pending_individual = PendingIndividualFactory(
        program=program,
        business_area=program.business_area,
    )
    AccountFactory(individual=pending_individual, number="2087008012")

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id])

    record.refresh_from_db()
    rdi.refresh_from_db()
    assert record.ignored is True
    assert record.error_message == NigeriaPeopleRegistrationService.DUPLICATE_ACCOUNT_NUMBER_REASON
    assert rdi.status == RegistrationDataImport.IMPORT_ERROR
    assert rdi.error_message == "All selected Aurora Records were ignored during processing"
    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 0
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 0
    assert PendingAccount.objects.filter(individual__registration_data_import=rdi).count() == 0


def test_import_data_skips_record_if_national_id_already_imported(
    nigeria_country: object,
    nigeria_admin_areas: dict,
    document_type: object,
    account_type: object,
    financial_institution_mapping: object,
    registration: object,
    user: object,
    record: object,
    program: object,
    financial_institutions: dict,
) -> None:
    assert nigeria_country
    assert nigeria_admin_areas
    assert document_type
    assert account_type
    assert financial_institution_mapping
    assert financial_institutions

    DocumentFactory(
        program=program,
        type=document_type,
        document_number="01234567891",
        status=Document.STATUS_VALID,
    )

    service = NigeriaPeopleRegistrationService(registration)
    rdi = service.create_rdi(user, f"nigeria rdi {datetime.datetime.now()}")
    service.process_records(rdi.id, [record.id])

    record.refresh_from_db()
    assert record.ignored is True
    assert PendingHousehold.objects.filter(registration_data_import=rdi).count() == 0
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 0
    assert (
        PendingDocument.objects.filter(
            program=rdi.program,
            type=document_type,
            document_number="01234567891",
        ).count()
        == 0
    )


def test_registration_admin_is_nigeria_registration(project: object) -> None:
    nigeria_registration = RegistrationFactory(project=project, rdi_parser=NigeriaPeopleRegistrationService)
    non_nigeria_registration = RegistrationFactory(project=project, rdi_parser=None)

    assert RegistrationAdmin.is_nigeria_registration(nigeria_registration) is True
    assert RegistrationAdmin.is_nigeria_registration(non_nigeria_registration) is False


def test_registration_admin_has_ignored_records(registration: object, record: object) -> None:
    assert RegistrationAdmin.has_ignored_records(registration) is False

    record.ignored = True
    record.save(update_fields=["ignored"])

    assert RegistrationAdmin.has_ignored_records(registration) is False

    record.registration = registration.source_id
    record.save(update_fields=["registration"])

    assert RegistrationAdmin.has_ignored_records(registration) is True


def test_registration_admin_export_ignored_records_returns_csv(
    registration: object,
    record: object,
    record_fields: dict,
    user: object,
) -> None:
    record.registration = registration.source_id
    record.fields = make_record_fields(record_fields)
    record.ignored = True
    record.error_message = NigeriaPeopleRegistrationService.DUPLICATE_ACCOUNT_NUMBER_REASON
    record.save(update_fields=["registration", "fields", "ignored", "error_message"])
    registration.rdi_parser = NigeriaPeopleRegistrationService

    request = type("Request", (), {"user": user})()
    response = RegistrationAdmin(models.Registration, AdminSite()).export_ignored_records(request, registration.pk)
    csv_rows = list(csv.DictReader(StringIO(response.content.decode())))

    assert response["Content-Type"] == "text/csv"
    assert response["Content-Disposition"] == (
        f'attachment; filename="ignored_aurora_records_{registration.source_id}.csv"'
    )
    assert csv_rows == [
        {
            "record_id": str(record.id),
            "source_id": str(record.source_id),
            "registration": str(registration.source_id),
            "timestamp": str(record.timestamp),
            "ignored_reason": NigeriaPeopleRegistrationService.DUPLICATE_ACCOUNT_NUMBER_REASON,
            "account_number": "2087008012",
            "national_id": "01234567891",
            "given_name": "Giulio",
            "middle_name": "D",
            "family_name": "Franco",
            "phone_number": "+2348023456789",
        }
    ]


def test_registration_admin_export_ignored_records_rejects_non_nigeria_registration(
    registration: object,
    user: object,
) -> None:
    registration.rdi_parser = None
    request = type("Request", (), {"user": user})()

    with pytest.raises(PermissionDenied):
        RegistrationAdmin(models.Registration, AdminSite()).export_ignored_records(request, registration.pk)
