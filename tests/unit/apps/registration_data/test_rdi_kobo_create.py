from io import BytesIO
from pathlib import Path
import re
from unittest import mock

from django.core.files import File
from django.db.models.fields.files import ImageFieldFile
from django.forms import model_to_dict
from django_countries.fields import Country
import pytest

from extras.test_utils.factories import (
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    ImportDataFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_CHOICE
from hope.apps.registration_data.tasks.rdi_kobo_create import RdiKoboCreateTask
from hope.models import PendingAccount, PendingDocument, PendingHousehold, PendingIndividual, RegistrationDataImport
from hope.models.financial_institution import FinancialInstitution
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]

FILES_DIR = Path(__file__).resolve().parent / "test_file"


@pytest.fixture
def countries() -> dict:
    afghanistan = CountryFactory(
        name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"
    )
    CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")
    CountryFactory(name="Nigeria", short_name="Nigeria", iso_code2="NG", iso_code3="NGA", iso_num="0566")
    return {"afghanistan": afghanistan}


@pytest.fixture
def business_area(countries: dict) -> object:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    business_area.kobo_username = "1234ABC"
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["kobo_username", "postpone_deduplication"])
    return business_area


@pytest.fixture
def admin_areas(countries: dict) -> None:
    admin1_type = AreaTypeFactory(name="Bakool", area_level=1, country=countries["afghanistan"])
    admin1 = AreaFactory(p_code="SO25", name="SO25", area_type=admin1_type)
    admin2_type = AreaTypeFactory(name="Ceel Barde", area_level=2, country=countries["afghanistan"])
    AreaFactory(p_code="SO2502", name="SO2502", parent=admin1, area_type=admin2_type)


@pytest.fixture
def document_types() -> None:
    for doc_type, label in IDENTIFICATION_TYPE_CHOICE:
        DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type], label=label)


@pytest.fixture
def financial_institutions() -> None:
    FinancialInstitutionFactory(
        name="Generic Telco Company",
        type=FinancialInstitution.FinancialInstitutionType.TELCO,
    )
    FinancialInstitutionFactory(
        name="Generic Bank",
        type=FinancialInstitution.FinancialInstitutionType.BANK,
    )


@pytest.fixture
def account_types() -> None:
    AccountTypeFactory(key="mobile")


@pytest.fixture
def import_data() -> object:
    content = (FILES_DIR / "kobo_submissions.json").read_bytes()
    file = File(BytesIO(content), name="kobo_submissions.json")
    return ImportDataFactory(
        file=file,
        number_of_households=1,
        number_of_individuals=2,
    )


@pytest.fixture
def import_data_collectors() -> object:
    content = (FILES_DIR / "kobo_submissions_collectors.json").read_bytes()
    file = File(BytesIO(content), name="kobo_submissions_collectors.json")
    return ImportDataFactory(
        file=file,
        number_of_households=2,
        number_of_individuals=5,
    )


@pytest.fixture
def program(business_area: object) -> object:
    return ProgramFactory(status="ACTIVE", business_area=business_area)


@pytest.fixture
def registration_data_import(
    business_area: object,
    program: object,
    import_data: object,
    admin_areas: None,
    document_types: None,
    financial_institutions: None,
    account_types: None,
) -> object:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
        number_of_individuals=99,
        number_of_households=33,
    )


def _mock_get_attached_file():
    return lambda *args, **kwargs: BytesIO(b"fake-image-binary")


def test_execute(
    business_area: object,
    registration_data_import: object,
    import_data: object,
    program: object,
) -> None:
    assert registration_data_import.number_of_households == 33
    assert registration_data_import.number_of_individuals == 99

    with mock.patch(
        "hope.apps.registration_data.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        side_effect=_mock_get_attached_file(),
    ):
        task = RdiKoboCreateTask(registration_data_import.id, business_area.id)
        task.execute(import_data.id, program.id)

    registration_data_import.refresh_from_db(fields=["status", "number_of_households", "number_of_individuals"])
    assert registration_data_import.status == RegistrationDataImport.IN_REVIEW
    assert registration_data_import.number_of_households == 1
    assert registration_data_import.number_of_individuals == 2

    households = PendingHousehold.objects.all()
    individuals = PendingIndividual.objects.all()
    documents = PendingDocument.objects.all()

    assert households.count() == 1
    assert individuals.count() == 2
    assert documents.count() == 4

    individual = individuals.get(full_name="Test Testowski")

    individuals_obj_data = model_to_dict(
        individual,
        ("country", "sex", "age", "marital_status", "relationship"),
    )
    expected_ind = {
        "relationship": "HEAD",
        "sex": "MALE",
        "marital_status": "MARRIED",
    }
    assert individuals_obj_data == expected_ind

    pending_household = individual.pending_household
    household_obj_data = {
        "residence_status": pending_household.residence_status,
        "country": pending_household.country.iso_code2,
        "flex_fields": pending_household.flex_fields,
    }
    expected_hh = {
        "residence_status": "REFUGEE",
        "country": Country(code="AF").code,
        "flex_fields": {},
    }
    assert household_obj_data == expected_hh

    assert pending_household.detail_id == "aPkhoRMrkkDwgsvWuwi39s"
    assert str(pending_household.kobo_submission_uuid) == "c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
    assert pending_household.kobo_submission_time.isoformat() == "2020-06-03T13:05:10+00:00"

    assert PendingAccount.objects.count() == 2
    dmd = PendingAccount.objects.get(individual__full_name="Tesa Testowski")
    assert dmd.account_type.key == "mobile"
    assert dmd.data == {
        "service_provider_code": "ABC",
        "delivery_phone_number": "+48880110456",
        "provider": "SIGMA",
    }
    assert dmd.individual.full_name == "Tesa Testowski"


def test_execute_multiple_collectors(
    business_area: object,
    registration_data_import: object,
    import_data_collectors: object,
    program: object,
) -> None:
    with mock.patch(
        "hope.apps.registration_data.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        side_effect=_mock_get_attached_file(),
    ):
        task = RdiKoboCreateTask(registration_data_import.id, business_area.id)
        task.execute(import_data_collectors.id, program.id)
    households = PendingHousehold.objects.all()
    individuals = PendingIndividual.objects.all()

    assert households.count() == 3
    assert individuals.count() == 7

    documents = PendingDocument.objects.values_list("individual__full_name", flat=True)
    assert sorted(documents) == [
        "Tesa Testowski 222",
        "Tesa XLast",
        "Test Testowski 222",
        "XLast XFull XName",
        "Zbyszek Zbyszkowski",
        "abc efg",
    ]

    first_household = households.get(size=3, individuals__full_name="Tesa Testowski 222")
    second_household = households.get(size=2)

    first_household_collectors = first_household.individuals_and_roles.order_by("individual__full_name").values_list(
        "individual__full_name", "role"
    )
    assert list(first_household_collectors) == [
        ("Tesa Testowski 222", "ALTERNATE"),
        ("Test Testowski 222", "PRIMARY"),
    ]
    second_household_collectors = second_household.individuals_and_roles.values_list("individual__full_name", "role")
    assert list(second_household_collectors) == [("Test Testowski", "PRIMARY")]


def test_handle_image_field(
    business_area: object,
    registration_data_import: object,
) -> None:
    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)
    task.attachments = [
        {
            "mimetype": "image/png",
            "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
            "/signature-14_59_24.png",
            "instance": 102612403,
            "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "id": 35027752,
            "xform": 549831,
        },
        {
            "mimetype": "image/png",
            "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=xD"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
            "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=xD"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
            "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=xD"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
            "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
            "/signature-21_37_xDDD.png",
            "instance": 102612403,
            "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
            "id": 35027752,
            "xform": 549831,
        },
    ]

    with mock.patch(
        "hope.apps.registration_data.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        side_effect=_mock_get_attached_file(),
    ):
        result = task._handle_image_field("image_is_not_there.gif", False)
        assert result is None

        result = task._handle_image_field("signature-14_59_24.png", False)
        assert isinstance(result, File)
        assert result.name == "signature-14_59_24.png"

        result = task._handle_image_field("signature-21_37.png", False)
        assert isinstance(result, File)
        assert result.name == "signature-21_37.png"


def test_handle_geopoint_field(business_area: object, registration_data_import: object) -> None:
    geopoint = "51.107883 17.038538"
    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)

    expected = 51.107883, 17.038538
    result = task._handle_geopoint_field(geopoint, False)
    assert result == expected


def test_cast_boolean_value(business_area: object, registration_data_import: object) -> None:
    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)

    result = task._cast_value("FALSE", "estimated_birth_date_i_c")
    assert result is False

    result = task._cast_value("false", "estimated_birth_date_i_c")
    assert result is False

    result = task._cast_value("False", "estimated_birth_date_i_c")
    assert result is False

    result = task._cast_value("0", "estimated_birth_date_i_c")
    assert result is False

    result = task._cast_value("TRUE", "estimated_birth_date_i_c")
    assert result is True

    result = task._cast_value("true", "estimated_birth_date_i_c")
    assert result is True

    result = task._cast_value("True", "estimated_birth_date_i_c")
    assert result is True

    result = task._cast_value("1", "estimated_birth_date_i_c")
    assert result is True

    result = task._cast_value(True, "estimated_birth_date_i_c")
    assert result is True

    result = task._cast_value(False, "estimated_birth_date_i_c")
    assert result is False


def test_handle_documents_and_identities(
    business_area: object,
    registration_data_import: object,
    program: object,
) -> None:
    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)
    task.attachments = [
        {
            "mimetype": "image/png",
            "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
            "/signature-14_59_24.png",
            "instance": 102612403,
            "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
            "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
            "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
            "id": 35027752,
            "xform": 549831,
        }
    ]
    individual = IndividualFactory(
        program=program,
        business_area=business_area,
        registration_data_import=registration_data_import,
        rdi_merge_status=MergeStatusModel.PENDING,
    )
    documents_and_identities = [
        {
            "birth_certificate": {
                "number": "123123123",
                "individual": individual,
                "photo": "signature-14_59_24.png",
                "issuing_country": Country("AFG"),
            }
        },
        {
            "national_passport": {
                "number": "444111123",
                "individual": individual,
                "photo": "signature-14_59_24.png",
                "issuing_country": Country("AFG"),
            }
        },
    ]
    with mock.patch(
        "hope.apps.registration_data.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        side_effect=_mock_get_attached_file(),
    ):
        task._handle_documents_and_identities(documents_and_identities)

    result = list(PendingDocument.objects.values("document_number", "individual_id"))
    expected = [
        {"document_number": "123123123", "individual_id": individual.id},
        {"document_number": "444111123", "individual_id": individual.id},
    ]
    assert result == expected

    photo = PendingDocument.objects.first().photo
    assert isinstance(photo, ImageFieldFile)
    assert photo.name.startswith("signature-14_59_24")

    birth_certificate = PendingDocument.objects.get(document_number=123123123).type.key
    national_passport = PendingDocument.objects.get(document_number=444111123).type.key

    assert birth_certificate == "birth_certificate"
    assert national_passport == "national_passport"


def test_handle_household_dict(business_area: object, registration_data_import: object) -> None:
    households_to_create = []
    collectors_to_create, head_of_households_mapping, individuals_ids_hash_dict = ({}, {}, {})
    household = {
        "_id": 1111,
        "uuid": "qweqweqweqwe",
        "start": "2024-03",
        "end": "2024-03",
        "org_name_enumerator_h_c": "org_name_enumerator_string",
        "name_enumerator_h_c": "name_enumerator_string",
        "enumertor_phone_num_h_f": "321123123321",
        "consent_h_c": "1",
        "country_h_c": "NGA",
        "admin1_h_c": "SO25",
        "admin2_h_c": "SO2502",
        "village_h_c": "VillageName",
        "nearest_school_h_f": "next",
        "hh_geopoint_h_c": "46.123 6.312 0 0",
        "size_h_c": "5",
        "children_under_18_h_f": "2",
        "children_6_to_11_h_f": "1",
        "hohh_is_caregiver_h_f": "0",
        "alternate_collector": "1",
        "_xform_id_string": "kobo_asset_id_string_OR_detail_id",
        "_uuid": "5b6f30ee-010b-4bd5-a510-e78f062af155",
        "_submission_time": "2022-02-22T12:22:22",
    }
    submission_meta_data = {
        "kobo_submission_uuid": "5b6f30ee-010b-4bd5-a510-e78f062af155",
        "kobo_asset_id": "kobo_asset_id_string_OR_detail_id",
        "kobo_submission_time": "2022-02-22T12:22:22",
    }

    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)
    task.handle_household(
        collectors_to_create,
        head_of_households_mapping,
        household,
        households_to_create,
        individuals_ids_hash_dict=individuals_ids_hash_dict,
        submission_meta_data=submission_meta_data,
        household_count=1,
    )
    hh = households_to_create[0]

    assert len(households_to_create) == 1
    assert hh.detail_id == "kobo_asset_id_string_OR_detail_id"
    assert hh.kobo_submission_time.isoformat() == "2022-02-22T12:22:22"
    assert hh.kobo_submission_uuid == "5b6f30ee-010b-4bd5-a510-e78f062af155"


def test_process_individual_try_except(business_area: object, registration_data_import: object) -> None:
    households_to_create = []
    collectors_to_create, head_of_households_mapping, individuals_ids_hash_dict = ({}, {}, {})
    submission_meta_data = {"kobo_submission_uuid": "1b6f30ee-010b-4bd5-a510-e78f062af234"}
    household = {"individual_questions": [{"birth_date_i_c": "true"}]}

    task = RdiKoboCreateTask(registration_data_import.id, business_area.id)

    with pytest.raises(
        Exception,
        match=re.escape("Error processing Individual: field `birth_date_i_c` ParserError(Unknown string format: true)"),
    ):
        task.handle_household(
            collectors_to_create,
            head_of_households_mapping,
            household,
            households_to_create,
            individuals_ids_hash_dict=individuals_ids_hash_dict,
            submission_meta_data=submission_meta_data,
            household_count=1,
        )

    household["individual_questions"] = [{"f_6_11_disability_h_c": "true"}]
    with pytest.raises(Exception, match=re.escape("Error processing Household: field `f_6_11_disability_h_c`")):
        task.handle_household(
            collectors_to_create,
            head_of_households_mapping,
            household,
            households_to_create,
            individuals_ids_hash_dict=individuals_ids_hash_dict,
            submission_meta_data=submission_meta_data,
            household_count=1,
        )
