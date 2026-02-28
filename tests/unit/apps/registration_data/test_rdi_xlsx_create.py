import datetime
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.core.files import File
from django.forms import model_to_dict
from django.utils.dateparse import parse_datetime
from django_countries.fields import Country
import openpyxl
from PIL import Image
import pytest

from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import (
    DocumentTypeFactory,
    PendingIndividualFactory,
)
from extras.test_utils.factories.payment import AccountTypeFactory, FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import ImportDataFactory, RegistrationDataImportFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING, SheetImageLoader
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_TAX_ID,
)
from hope.apps.registration_data.tasks.rdi_xlsx_create import RdiXlsxCreateTask
from hope.models import (
    Country as GeoCountry,
    FlexibleAttribute,
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PendingIndividualRoleInHousehold,
    PeriodicFieldData,
    Program,
)
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]

FILES_DIR = Path(__file__).resolve().parent / "test_file"


def build_test_image() -> Image.Image:
    return Image.new("RGB", (2, 2), color=(255, 0, 0))


def create_document_image() -> File:
    file_obj = BytesIO()
    build_test_image().save(file_obj, format="PNG")
    file_obj.seek(0)
    return File(file_obj, name="image.png")


class ImageLoaderMock(SheetImageLoader):
    def __init__(self) -> None:
        pass

    def image_in(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def get(self, *args: Any, **kwargs: Any) -> Image.Image:
        file_obj = BytesIO()
        build_test_image().save(file_obj, format="PNG")
        file_obj.seek(0)
        image = Image.open(file_obj)
        image.load()
        return image


class CellMock:
    def __init__(self, value: Any, coordinate: Any) -> None:
        self.value = value
        self.coordinate = coordinate


@pytest.fixture
def countries() -> dict[str, object]:
    afghanistan = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    poland = CountryFactory(
        name="Poland",
        short_name="Poland",
        iso_code2="PL",
        iso_code3="POL",
        iso_num="0616",
    )
    return {"afghanistan": afghanistan, "poland": poland}


@pytest.fixture
def admin_areas(countries: dict[str, object]) -> dict[str, object]:
    area_type_l1 = AreaTypeFactory(country=countries["afghanistan"], area_level=1)
    area_type_l2 = AreaTypeFactory(country=countries["afghanistan"], area_level=2, parent=area_type_l1)
    parent = AreaFactory(p_code="AF11", name="Name", area_type=area_type_l1)
    child = AreaFactory(p_code="AF1115", name="Name2", parent=parent, area_type=area_type_l2)
    return {"admin1": parent, "admin2": child}


@pytest.fixture
def business_area(countries: dict[str, object]):
    business_area = BusinessAreaFactory(
        slug="afghanistan",
        name="Afghanistan",
        long_name="Afghanistan",
        active=True,
        office_country=countries["afghanistan"],
        postpone_deduplication=False,
    )
    business_area.countries.add(countries["afghanistan"])
    business_area.payment_countries.add(countries["afghanistan"])
    return business_area


@pytest.fixture
def partners() -> dict[str, object]:
    return {
        "wfp": PartnerFactory(name="WFP"),
        "unhcr": PartnerFactory(name="UNHCR"),
    }


@pytest.fixture
def document_types() -> dict[str, object]:
    tax_id_key = IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]
    return {"tax_id": DocumentTypeFactory(key=tax_id_key)}


@pytest.fixture
def account_type() -> object:
    return AccountTypeFactory(key="bank")


@pytest.fixture
def financial_institution() -> object:
    return FinancialInstitutionFactory(name="Generic Bank")


@pytest.fixture
def flex_fields() -> dict[str, object]:
    muac = FlexibleAttributeFactory(
        type=FlexibleAttribute.INTEGER,
        name="muac_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )
    jan_decimal = FlexibleAttributeFactory(
        type=FlexibleAttribute.DECIMAL,
        name="jan_decimal_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )
    return {"muac": muac, "jan_decimal": jan_decimal}


@pytest.fixture
def program(business_area) -> Program:
    return ProgramFactory(status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def pdu_attributes(program: Program) -> dict[str, object]:
    pdu_string = FlexibleAttributeForPDUFactory(
        label="PDU String Attribute",
        pdu_data__subtype=PeriodicFieldData.STRING,
        pdu_data__number_of_rounds=1,
        pdu_data__rounds_names=["May"],
        program=program,
    )
    pdu_date = FlexibleAttributeForPDUFactory(
        label="PDU Date Attribute",
        pdu_data__subtype=PeriodicFieldData.DATE,
        pdu_data__number_of_rounds=1,
        pdu_data__rounds_names=["May"],
        program=program,
    )
    return {"string": pdu_string, "date": pdu_date}


@pytest.fixture
def import_data(business_area) -> object:
    content = (FILES_DIR / "new_reg_data_import.xlsx").read_bytes()
    file = File(BytesIO(content), name="new_reg_data_import.xlsx")
    return ImportDataFactory(
        file=file,
        number_of_households=3,
        number_of_individuals=6,
        business_area_slug=business_area.slug,
    )


@pytest.fixture
def registration_data_import(business_area, program, import_data) -> object:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data,
        number_of_households=3,
        number_of_individuals=6,
    )


@pytest.fixture
def import_data_flex(business_area) -> object:
    content = (FILES_DIR / "new_reg_data_import_flex_field.xlsx").read_bytes()
    file = File(BytesIO(content), name="new_reg_data_import_flex_field.xlsx")
    return ImportDataFactory(
        file=file,
        number_of_households=3,
        number_of_individuals=6,
        business_area_slug=business_area.slug,
    )


@pytest.fixture
def registration_data_import_flex(business_area, program, import_data_flex) -> object:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        import_data=import_data_flex,
        number_of_households=3,
        number_of_individuals=6,
    )


@pytest.fixture
def rdi_setup(
    admin_areas: dict[str, object],
    partners: dict[str, object],
    document_types: dict[str, object],
    account_type: object,
    financial_institution: object,
    flex_fields: dict[str, object],
    pdu_attributes: dict[str, object],
) -> dict[str, object]:
    return {
        "admin_areas": admin_areas,
        "partners": partners,
        "document_types": document_types,
        "account_type": account_type,
        "financial_institution": financial_institution,
        "flex_fields": flex_fields,
        "pdu_attributes": pdu_attributes,
    }


def test_execute(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )

    assert PendingHousehold.objects.count() == 3
    assert PendingIndividual.objects.count() == 6

    individual_data = {
        "full_name": "Some Full Name",
        "given_name": "Some",
        "middle_name": "Full",
        "family_name": "Name",
        "sex": "MALE",
        "relationship": "HEAD",
        "birth_date": date(1963, 2, 3),
        "marital_status": "MARRIED",
        "email": "fake_email_123@mail.com",
    }
    matching_individuals = PendingIndividual.objects.filter(**individual_data)
    assert matching_individuals.count() == 1

    household_data = {
        "residence_status": "REFUGEE",
        "country": GeoCountry.objects.get(iso_code2="AF").id,
        "zip_code": "2153",
        "flex_fields": {"enumerator_id": "UNICEF"},
    }
    household = matching_individuals.first().household
    household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

    roles = household.individuals_and_roles(manager="pending_objects").all()
    assert roles.count() == 1
    role = roles.first()
    assert role.role == "PRIMARY"
    assert role.individual.full_name == "Some Full Name"

    assert household_obj_data == household_data


def test_execute_with_postpone_deduplication(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    business_area.postpone_deduplication = True
    business_area.save()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )

    assert PendingHousehold.objects.count() == 3
    assert PendingIndividual.objects.count() == 6

    individual_data = {
        "full_name": "Some Full Name",
        "given_name": "Some",
        "middle_name": "Full",
        "family_name": "Name",
        "sex": "MALE",
        "relationship": "HEAD",
        "birth_date": date(1963, 2, 3),
        "marital_status": "MARRIED",
        "email": "fake_email_123@mail.com",
    }
    matching_individuals = PendingIndividual.objects.filter(**individual_data)

    assert matching_individuals.count() == 1

    household_data = {
        "residence_status": "REFUGEE",
        "country": GeoCountry.objects.get(iso_code2="AF").id,
        "zip_code": "2153",
        "flex_fields": {"enumerator_id": "UNICEF"},
    }
    household = matching_individuals.first().household
    household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

    roles = household.individuals_and_roles(manager="pending_objects").all()
    assert roles.count() == 1
    role = roles.first()
    assert role.role == "PRIMARY"
    assert role.individual.full_name == "Some Full Name"

    assert household_obj_data == household_data


def test_execute_with_flex_field_and_pdu(
    rdi_setup: dict[str, object],
    registration_data_import_flex: object,
    import_data_flex: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    registration_data_import_flex.created_at = datetime.datetime(2021, 3, 7)
    registration_data_import_flex.save()
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import_flex.id,
        import_data_flex.id,
        business_area.id,
        program.id,
    )

    assert PendingHousehold.objects.count() == 3
    assert PendingIndividual.objects.count() == 6

    individual_data = {
        "full_name": "Some Full Name",
        "given_name": "Some",
        "middle_name": "Full",
        "family_name": "Name",
        "sex": "MALE",
        "relationship": "HEAD",
        "birth_date": date(1963, 2, 3),
        "marital_status": "MARRIED",
        "email": "fake_email_123@mail.com",
    }
    matching_individuals = PendingIndividual.objects.filter(**individual_data)

    assert matching_individuals.count() == 1

    household_data = {
        "residence_status": "REFUGEE",
        "country": GeoCountry.objects.get(iso_code2="AF").id,
        "zip_code": "2153",
        "flex_fields": {"enumerator_id": "UNICEF"},
    }
    household = matching_individuals.first().household
    household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))
    individual = matching_individuals.first()
    roles = household.individuals_and_roles(manager="pending_objects").all()
    assert roles.count() == 1
    role = roles.first()
    assert role.role == "PRIMARY"
    assert role.individual.full_name == "Some Full Name"

    assert household_obj_data == household_data
    assert individual.flex_fields == {
        "muac_i_f": 1,
        "jan_decimal_i_f": 12.376,
        "pdu_date_attribute": {"1": {"value": "1996-06-26", "collection_date": "2021-03-07"}},
        "pdu_string_attribute": {"1": {"value": "Test PDU Value", "collection_date": "2020-01-08"}},
    }


def test_execute_handle_identities(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )
    assert PendingIndividualIdentity.objects.count() == 2
    assert (
        PendingIndividualIdentity.objects.filter(
            number="TEST",
            country__iso_code2="PL",
            partner__name="WFP",
            individual__full_name="Some Full Name",
        ).count()
        == 1
    )
    assert (
        PendingIndividualIdentity.objects.filter(
            number="WTG",
            country__iso_code2="PL",
            partner__name="UNHCR",
            individual__full_name="Some Full Name",
        ).count()
        == 1
    )


def test_handle_document_fields() -> None:
    task = RdiXlsxCreateTask()
    task.documents = {}
    individual = PendingIndividualFactory()

    header = "birth_certificate_no_i_c"
    row_num = 14

    task._handle_document_fields(None, header, row_num, individual)
    assert task.documents == {}

    value = "AB1247246Q12W"
    task._handle_document_fields(value, header, row_num, individual)
    expected = {
        "individual_14_birth_certificate_i_c": {
            "individual": individual,
            "key": "birth_certificate",
            "value": value,
        }
    }

    assert task.documents == expected

    number = "CD1247246Q12W"
    header = "other_id_no_i_c"
    task._handle_document_fields(number, header, row_num, individual)
    expected = {
        "individual_14_birth_certificate_i_c": {
            "individual": individual,
            "key": "birth_certificate",
            "value": value,
        },
        "individual_14_other_id_i_c": {
            "individual": individual,
            "key": "other_id",
            "value": number,
        },
    }
    assert task.documents == expected


def test_handle_document_photo_fields() -> None:
    with mock.patch(
        "hope.apps.registration_data.tasks.rdi_xlsx_create.timezone.now",
        return_value=parse_datetime("2020-06-22 12:00:00-0000"),
    ):
        task = RdiXlsxCreateTask()
        task.image_loader = ImageLoaderMock()
        task.documents = {}
        individual = PendingIndividualFactory()
        cell = CellMock("image.png", 12)

        task._handle_document_photo_fields(
            cell,
            14,
            individual,
            "birth_certificate_photo_i_c",
        )
        assert "individual_14_birth_certificate_i_c" in task.documents
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        assert birth_certificate["individual"] == individual
        assert birth_certificate["photo"].name == "12-2020-06-22 12:00:00+00:00.jpg"

        birth_cert_doc = {
            "individual_14_birth_certificate_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": "CD1247246Q12W",
            }
        }
        task.documents = birth_cert_doc
        task._handle_document_photo_fields(
            cell,
            14,
            individual,
            "birth_certificate_photo_i_c",
        )

        assert "individual_14_birth_certificate_i_c" in task.documents
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        assert birth_certificate["name"] == "Birth Certificate"
        assert birth_certificate["type"] == "BIRTH_CERTIFICATE"
        assert birth_certificate["value"] == "CD1247246Q12W"
        assert birth_certificate["photo"].name == "12-2020-06-22 12:00:00+00:00.jpg"


def test_handle_geopoint_field() -> None:
    empty_geopoint = ""
    valid_geopoint = "51.107883, 17.038538"
    task = RdiXlsxCreateTask()

    result = task._handle_geopoint_field(empty_geopoint)
    assert result is None

    expected = 51.107883, 17.038538
    result = task._handle_geopoint_field(valid_geopoint)
    assert result == expected


def test_create_documents(countries: dict[str, object]) -> None:
    assert countries
    task = RdiXlsxCreateTask()
    individual = PendingIndividualFactory(rdi_merge_status=MergeStatusModel.PENDING)
    doc_type = DocumentTypeFactory(
        label="Birth Certificate",
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
    )
    task.documents = {
        "individual_14_birth_certificate_i_c": {
            "individual": individual,
            "name": "Birth Certificate",
            "key": "birth_certificate",
            "value": "CD1247246Q12W",
            "issuing_country": Country("AFG"),
            "photo": create_document_image(),
        }
    }
    task._create_documents()

    documents = PendingDocument.objects.values("document_number", "type_id")
    assert documents.count() == 1

    expected = [{"document_number": "CD1247246Q12W", "type_id": doc_type.id}]
    assert list(documents) == expected

    document = PendingDocument.objects.first()
    photo = document.photo.name
    assert photo.startswith("image")
    assert photo.endswith(".png")


def test_cast_value() -> None:
    task = RdiXlsxCreateTask()

    assert task._cast_value(None, "test_header") is None
    assert task._cast_value("", "test_header") == ""

    assert task._cast_value("12", "size_h_c") == 12
    assert task._cast_value(12.0, "size_h_c") == 12

    assert task._cast_value("male", "gender_i_c") == "MALE"
    assert task._cast_value("Male", "gender_i_c") == "MALE"
    assert task._cast_value("MALE", "gender_i_c") == "MALE"

    assert task._cast_value("TRUE", "estimated_birth_date_i_c") is True
    assert task._cast_value("true", "estimated_birth_date_i_c") is True
    assert task._cast_value("True", "estimated_birth_date_i_c") is True


def test_store_row_id(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )

    for household in PendingHousehold.objects.all():
        assert int(household.detail_id) in [3, 4, 6]

    for individual in PendingIndividual.objects.all():
        assert int(individual.detail_id) in [3, 4, 5, 7, 8, 9]


def test_create_tax_id_document(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )

    document = PendingDocument.objects.filter(individual__detail_id=5).first()
    assert document.type.key == IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]
    assert document.document_number == "CD1247246Q12W"


def test_import_empty_cell_as_blank_cell(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )

    individual = PendingIndividual.objects.get(detail_id=3)
    assert individual.seeing_disability == ""
    assert individual.hearing_disability == ""


def test_create_receiver_poi_document(countries: dict[str, object]) -> None:
    assert countries
    task = RdiXlsxCreateTask()
    individual = PendingIndividualFactory(rdi_merge_status=MergeStatusModel.PENDING)
    doc_type = DocumentTypeFactory(label="Receiver POI", key="receiver_poi")
    task.documents = {
        "individual_10_receiver_poi_i_c": {
            "individual": individual,
            "name": "Receiver POI",
            "key": "receiver_poi",
            "value": "TEST123_qwerty",
            "issuing_country": Country("AFG"),
            "photo": None,
        }
    }
    task._create_documents()

    documents = PendingDocument.objects.values("document_number", "type_id")
    assert documents.count() == 1

    expected = [{"document_number": "TEST123_qwerty", "type_id": doc_type.id}]
    assert list(documents) == expected


def test_create_delivery_mechanism_data(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
    business_area: object,
    program: Program,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()
    task.execute(
        registration_data_import.id,
        import_data.id,
        business_area.id,
        program.id,
    )
    assert PendingAccount.objects.count() == 3

    dmd1 = PendingAccount.objects.get(individual__detail_id=3)
    dmd2 = PendingAccount.objects.get(individual__detail_id=4)
    dmd3 = PendingAccount.objects.get(individual__detail_id=5)
    assert dmd1.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd2.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd3.rdi_merge_status == MergeStatusModel.PENDING
    assert dmd1.data == {
        "card_number": "164260858",
        "card_expiry_date": "1995-06-03T00:00:00",
    }
    assert dmd2.data == {
        "card_number": "1975549730",
        "card_expiry_date": "2022-02-17T00:00:00",
        "name_of_cardholder": "Name1",
    }
    assert dmd3.data == {
        "card_number": "870567340",
        "card_expiry_date": "2016-06-27T00:00:00",
        "name_of_cardholder": "Name2",
    }


def test_exception_with_cell_processing(
    rdi_setup: dict[str, object],
    registration_data_import: object,
    import_data: object,
) -> None:
    assert rdi_setup
    task = RdiXlsxCreateTask()

    wb = openpyxl.load_workbook(import_data.file, data_only=True)
    sheet = wb["Households"]

    header_value = next((cell.value for cell in sheet[1] if cell.value), None)
    assert header_value is not None
    task.COMBINED_FIELDS = {header_value: {"name": "dummy", "required": True}}

    def raise_cast_value(value: Any, header: str) -> None:
        raise ValueError("boom")

    with patch.object(task, "_cast_value", side_effect=raise_cast_value):
        with patch.object(task, "_extract_household_id_from_row", return_value=None):
            with pytest.raises(Exception, match="Error processing cell"):
                task._create_objects(sheet, registration_data_import)


def test_handle_identity_coverage() -> None:
    task = RdiXlsxCreateTask()
    task.identities = {}
    task.image_loader = ImageLoaderMock()
    ind = PendingIndividualFactory()
    cell = CellMock("img.png", "A1")

    task._handle_identity_fields(None, "unhcr_id_no_i_c", 1, ind)
    assert not task.identities

    task._handle_identity_fields("123", "unhcr_id_no_i_c", 1, ind)
    assert task.identities["individual_1_UNHCR"]["number"] == "123"

    task._handle_identity_fields("456", "unhcr_id_no_i_c", 1, ind)
    assert task.identities["individual_1_UNHCR"]["number"] == "456"

    task._handle_identity_issuing_country_fields(None, "unhcr_id_issuer_i_c", 1, ind)

    task._handle_identity_issuing_country_fields("AF", "unhcr_id_issuer_i_c", 1, ind)
    assert task.identities["individual_1_UNHCR"]["issuing_country"] == Country("AF")

    task._handle_identity_issuing_country_fields("PL", "scope_id_issuer_i_c", 2, ind)
    assert task.identities["individual_2_WFP"]["issuing_country"] == Country("PL")

    task._handle_identity_photo(cell, 1, "unhcr_id_photo_i_c", ind)
    assert "photo" in task.identities["individual_1_UNHCR"]

    cell2 = CellMock("img2.png", "A2")
    task._handle_identity_photo(cell2, 3, "unhcr_id_photo_i_c", ind)
    assert "photo" in task.identities["individual_3_UNHCR"]


def test_handle_collectors_coverage(
    rdi_setup: dict[str, object],
    business_area: object,
    program: Program,
) -> None:
    """Test _handle_collectors method with real data."""
    assert rdi_setup

    task = RdiXlsxCreateTask()

    from extras.test_utils.factories.household import PendingIndividualFactory

    ind = PendingIndividualFactory(
        rdi_merge_status=MergeStatusModel.PENDING,
        business_area=business_area,
        program=program,
    )

    from extras.test_utils.factories.household import PendingHouseholdFactory

    household1 = PendingHouseholdFactory(
        rdi_merge_status=MergeStatusModel.PENDING, business_area=business_area, program=program, unicef_id="1"
    )
    household2 = PendingHouseholdFactory(
        rdi_merge_status=MergeStatusModel.PENDING, business_area=business_area, program=program, unicef_id="2"
    )

    task.households = {"1": household1, "2": household2}

    PendingIndividualRoleInHousehold.objects.filter(household__in=[household1, household2]).delete()

    task._handle_collectors(None, "primary_collector_id", ind)
    assert not task.collectors

    task._handle_collectors("1", "primary_collector_id", ind)
    assert "1" in task.collectors
    assert len(task.collectors["1"]) == 1
    assert task.collectors["1"][0].role == "PRIMARY"

    initial_count = PendingIndividualRoleInHousehold.objects.count()
    task._create_collectors()

    assert PendingIndividualRoleInHousehold.objects.count() == initial_count + 1

    role = PendingIndividualRoleInHousehold.objects.filter(individual=ind, household=household1).first()
    assert role is not None
    assert role.role == "PRIMARY"

    task.collectors.clear()

    ind2 = PendingIndividualFactory(
        rdi_merge_status=MergeStatusModel.PENDING,
        business_area=business_area,
        program=program,
    )

    task._handle_collectors("1,2", "alternate_collector_id", ind2)

    list(task.collectors.keys())
    assert len(task.collectors) > 0

    PendingIndividualRoleInHousehold.objects.filter(household__in=[household1, household2]).delete()

    task.collectors.clear()
    task._handle_collectors(None, "alternate_collector_id", ind2)
    assert not task.collectors


def test_misc_handlers_coverage() -> None:
    task = RdiXlsxCreateTask()
    task.image_loader = ImageLoaderMock()

    cell = CellMock("val", "A1")
    assert task._handle_decimal_field(cell, is_flex_field=False) == "val"

    cell_float = CellMock("12.5", "A2")
    assert task._handle_decimal_field(cell_float, is_flex_field=True) == 12.5

    cell.value = "false"
    assert task._handle_bool_field(cell) is False

    cell.value = "true"
    assert task._handle_bool_field(cell) is True

    cell.value = "image.jpg"
    result = task._handle_image_field(cell, is_flex_field=False)
    from django.core.files import File

    assert isinstance(result, File)
    assert "A1" in result.name
    assert result.name.endswith(".jpg")

    ind = PendingIndividualFactory()
    ind.birth_date = datetime.datetime.now() + datetime.timedelta(days=100)
    task._validate_birth_date(ind)
    assert ind.estimated_birth_date is True
