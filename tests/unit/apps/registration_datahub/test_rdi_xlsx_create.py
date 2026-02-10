import datetime
from datetime import date
from io import BytesIO
from pathlib import Path
import re
from types import SimpleNamespace
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.core.files import File
from django.forms import model_to_dict
from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django_countries.fields import Country
import openpyxl
from PIL import Image
import pytest

from extras.test_utils.old_factories.account import PartnerFactory
from extras.test_utils.old_factories.core import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.household import (
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)
from extras.test_utils.old_factories.payment import generate_delivery_mechanisms
from extras.test_utils.old_factories.program import ProgramFactory
from extras.test_utils.old_factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING, SheetImageLoader
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_TAX_ID,
)
from hope.models import (
    BusinessArea,
    Country as GeoCountry,
    DocumentType,
    FlexibleAttribute,
    ImportData,
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PeriodicFieldData,
    Program,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.usefixtures("mock_elasticsearch")


def create_document_image() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/registration_data/test_file/image.png").read_bytes()
    return File(BytesIO(content), name="image.png")


class ImageLoaderMock(SheetImageLoader):
    def __init__(self) -> None:
        pass

    def image_in(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def get(self, *args: Any, **kwargs: Any) -> Image:
        return Image.open(create_document_image())


class CellMock:
    def __init__(self, value: Any, coordinate: Any) -> None:
        self.value = value
        self.coordinate = coordinate


class TestRdiXlsxCreateTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        # Create only countries needed by test xlsx file (new_reg_data_import.xlsx)
        afghanistan = CountryFactory(
            name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"
        )
        CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")
        area_type_l1 = AreaTypeFactory(country=afghanistan, area_level=1)
        area_type_l2 = AreaTypeFactory(country=afghanistan, area_level=2, parent=area_type_l1)

        generate_delivery_mechanisms()
        FlexibleAttribute.objects.create(
            type=FlexibleAttribute.INTEGER,
            name="muac_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
        FlexibleAttribute.objects.create(
            type=FlexibleAttribute.DECIMAL,
            name="jan_decimal_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
        content = Path(f"{settings.TESTS_ROOT}/apps/registration_data/test_file/new_reg_data_import.xlsx").read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        business_area = create_afghanistan()
        parent = AreaFactory(p_code="AF11", name="Name", area_type=area_type_l1)
        AreaFactory(p_code="AF1115", name="Name2", parent=parent, area_type=area_type_l2)

        from hope.apps.registration_data.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        PartnerFactory(name="WFP")
        PartnerFactory(name="UNHCR")

        cls.RdiXlsxCreateTask = RdiXlsxCreateTask

        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=3,
            number_of_individuals=6,
        )

        cls.program = ProgramFactory(status=Program.ACTIVE)

        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=business_area,
            program=cls.program,
            import_data=cls.import_data,
        )
        cls.string_attribute = create_pdu_flexible_attribute(
            label="PDU String Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )

        cls.string_attribute = create_pdu_flexible_attribute(
            label="PDU Date Attribute",
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )
        cls.business_area = BusinessArea.objects.first()
        DocumentType.objects.create(
            label="Tax Number Identification",
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        )

    def test_execute_xd(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        assert households_count == 3
        assert individuals_count == 6

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

    def test_execute_with_postpone_deduplication(self) -> None:
        task = self.RdiXlsxCreateTask()
        self.business_area.postpone_deduplication = True
        self.business_area.save()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        assert households_count == 3
        assert individuals_count == 6

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

    def test_execute_with_flex_field_and_pdu(self) -> None:
        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_data/test_file/new_reg_data_import_flex_field.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import_flex_field.xlsx")

        import_data = ImportData.objects.create(
            file=file,
            number_of_households=3,
            number_of_individuals=6,
        )

        registration_data_import = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=self.program,
            import_data=import_data,
        )
        registration_data_import.created_at = datetime.datetime(2021, 3, 7)
        registration_data_import.save()
        task = self.RdiXlsxCreateTask()
        task.execute(
            registration_data_import.id,
            import_data.id,
            self.business_area.id,
            self.program.id,
        )

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        assert households_count == 3
        assert individuals_count == 6

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

    def test_execute_handle_identities(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
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

    def test_handle_document_fields(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.documents = {}
        individual = PendingIndividualFactory()

        header = "birth_certificate_no_i_c"
        row_num = 14

        # when value is empty
        value = None
        task._handle_document_fields(
            value,
            header,
            row_num,
            individual,
        )
        assert task.documents == {}

        # when value is valid for header of not other type
        value = "AB1247246Q12W"
        task._handle_document_fields(
            value,
            header,
            row_num,
            individual,
        )
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
        task._handle_document_fields(
            number,
            header,
            row_num,
            individual,
        )
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

    @mock.patch(
        "hope.apps.registration_data.tasks.rdi_xlsx_create.SheetImageLoader",
        ImageLoaderMock,
    )
    @mock.patch(
        "hope.apps.registration_data.tasks.rdi_xlsx_create.timezone.now",
        return_value=parse_datetime("2020-06-22 12:00:00-0000"),
    )
    def test_handle_document_photo_fields(self, mock_now) -> None:
        task = self.RdiXlsxCreateTask()
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

    def test_handle_geopoint_field(self) -> None:
        empty_geopoint = ""
        valid_geopoint = "51.107883, 17.038538"
        task = self.RdiXlsxCreateTask()

        result = task._handle_geopoint_field(empty_geopoint)
        assert result is None

        expected = 51.107883, 17.038538
        result = task._handle_geopoint_field(valid_geopoint)
        assert result == expected

    def test_create_documents(self) -> None:
        task = self.RdiXlsxCreateTask()
        individual = IndividualFactory(rdi_merge_status=MergeStatusModel.PENDING)
        task.business_area = self.business_area
        doc_type = DocumentType.objects.create(
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

    def test_cast_value(self) -> None:
        task = self.RdiXlsxCreateTask()

        # None and ""
        result = task._cast_value(None, "test_header")
        assert result is None

        result = task._cast_value("", "test_header")
        assert result == ""

        # INTEGER - header: size_h_c
        result = task._cast_value("12", "size_h_c")
        assert result == 12

        result = task._cast_value(12.0, "size_h_c")
        assert result == 12

        # SELECT_ONE - header: gender_i_c
        result = task._cast_value("male", "gender_i_c")
        assert result == "MALE"

        result = task._cast_value("Male", "gender_i_c")
        assert result == "MALE"

        result = task._cast_value("MALE", "gender_i_c")
        assert result == "MALE"

        result = task._cast_value("TRUE", "estimated_birth_date_i_c")
        assert result is True

        result = task._cast_value("true", "estimated_birth_date_i_c")
        assert result is True

        result = task._cast_value("True", "estimated_birth_date_i_c")
        assert result is True

    def test_store_row_id(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )

        households = PendingHousehold.objects.all()
        for household in households:
            assert int(household.detail_id) in [3, 4, 6]

        individuals = PendingIndividual.objects.all()
        for individual in individuals:
            assert int(individual.detail_id) in [3, 4, 5, 7, 8, 9]

    def test_create_tax_id_document(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )

        document = PendingDocument.objects.filter(individual__detail_id=5).first()
        assert document.type.key == IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID]
        assert document.document_number == "CD1247246Q12W"

    def test_import_empty_cell_as_blank_cell(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )

        individual = PendingIndividual.objects.get(detail_id=3)
        assert individual.seeing_disability == ""
        assert individual.hearing_disability == ""

    def test_create_receiver_poi_document(self) -> None:
        task = self.RdiXlsxCreateTask()
        individual = IndividualFactory(rdi_merge_status=MergeStatusModel.PENDING)
        task.business_area = self.business_area
        doc_type = DocumentType.objects.get_or_create(
            label="Receiver POI",
            key="receiver_poi",
        )[0]
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

    def test_create_delivery_mechanism_data(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
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

    def test_get_obj_and_validate_sheet_title_sheet(self) -> None:
        task = self.RdiXlsxCreateTask()
        wb = openpyxl.load_workbook(self.import_data.file, data_only=True)
        obj_hh = task._get_obj_and_validate_sheet_title(self.registration_data_import, wb["Households"], "households")
        assert obj_hh.func is PendingHousehold

        obj_ind = task._get_obj_and_validate_sheet_title(
            self.registration_data_import, wb["Individuals"], "individuals"
        )
        assert obj_ind.func is PendingIndividual

        with pytest.raises(ValueError, match=re.escape("Unhandled sheet label ''Individuals''")):
            task._get_obj_and_validate_sheet_title(self.registration_data_import, wb["Individuals"], "Invalid")

    def test_set_relationship_col_if_no_value_or_no_hh(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.households = {"fake_id_123": PendingHousehold}
        households_to_update = []

        # value None in cell
        task._set_relationship_col("123_id", households_to_update, PendingIndividual, SimpleNamespace(value=None))
        assert len(households_to_update) == 0

        # value in cell not string
        task._set_relationship_col("hh_id", households_to_update, PendingIndividual, SimpleNamespace(value=777))
        assert len(households_to_update) == 0

        # value in cell not HEAD
        task._set_relationship_col("hh_id", households_to_update, PendingIndividual, SimpleNamespace(value="not_HEAD"))
        assert len(households_to_update) == 0

        # value no HH in self.households or wrong household_id arg
        task._set_relationship_col(
            "wrong_123_id", households_to_update, PendingIndividual, SimpleNamespace(value="HEAD")
        )
        assert len(households_to_update) == 0

        # everything is perfect, got HH for update household.head_of_household value
        task._set_relationship_col(
            "fake_id_123", households_to_update, PendingIndividual, SimpleNamespace(value="HEAD")
        )
        assert len(households_to_update) == 1

    def test_set_household_id_cell_if_no_value_or_wrong_value(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.households = {"fake_id_777": PendingHouseholdFactory()}

        # value in the cell is None
        hh_id = task._set_household_id_cell("hh_id", SimpleNamespace(value=None), PendingHousehold, "sheet_title")
        assert hh_id == "hh_id"

        # value in the cell is float and is_integer()
        hh_id = task._set_household_id_cell("hh_id", SimpleNamespace(value=1.0), PendingHousehold, "sheet_title")
        assert hh_id == "1"

        # value in the cell is real HH id so set PendingIndividual.household
        obj_to_create = PendingIndividualFactory(household=None)
        assert obj_to_create.household is None
        hh_id = task._set_household_id_cell("hh_id", SimpleNamespace(value="fake_id_777"), obj_to_create, "individuals")
        assert hh_id == "fake_id_777"
        assert obj_to_create.household is not None

    def test_exception_with_cell_processing(self) -> None:
        task = self.RdiXlsxCreateTask()

        class BrokenHeaderCell:
            def __repr__(self):
                return "<BrokenHeaderCell>"

            @property
            def value(self):
                raise ValueError("boomXD")

        wb = openpyxl.load_workbook(self.import_data.file, data_only=True)
        sheet = wb["Households"]

        real_first_row = list(sheet[1])
        real_first_row[0] = BrokenHeaderCell()  # break first header

        original_getitem = sheet.__getitem__

        def fake_getitem(idx):
            if idx == 1:
                return tuple(real_first_row)
            return original_getitem(idx)

        with patch.object(sheet, "__getitem__", side_effect=fake_getitem):
            with pytest.raises(
                Exception,
                match=re.escape(
                    "Error processing cell <Cell 'Households'.A1> with `<Cell 'Households'.A3>`: "
                    "TypeError('NoneType' object is not iterable)"
                ),
            ):
                task._create_objects(sheet, self.registration_data_import)
