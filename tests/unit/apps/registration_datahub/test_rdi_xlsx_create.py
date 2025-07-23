import datetime
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.forms import model_to_dict
from django.test import TestCase
from django.utils.dateparse import parse_datetime

import pytest
from django_countries.fields import Country
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from extras.test_utils.factories.household import (
    IndividualFactory,
    PendingIndividualFactory,
)
from extras.test_utils.factories.payment import generate_delivery_mechanisms
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from PIL import Image

from hct_mis_api.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    SheetImageLoader,
)
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.geo.models import Country as GeoCountry
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_TAX_ID,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
)
from hct_mis_api.apps.payment.models import PendingAccount
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import ImportData
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


def create_document_image() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/image.png").read_bytes()
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


@pytest.mark.elasticsearch
class TestRdiXlsxCreateTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
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
        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/new_reg_data_import.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        business_area = create_afghanistan()
        parent = AreaFactory(p_code="AF11", name="Name")
        AreaFactory(p_code="AF1115", name="Name2", parent=parent)

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
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
        rebuild_search_index()

    def test_execute_xd(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

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

        self.assertEqual(matching_individuals.count(), 1)

        household_data = {
            "residence_status": "REFUGEE",
            "country": GeoCountry.objects.get(iso_code2="AF").id,
            "zip_code": "2153",
            "flex_fields": {"enumerator_id": "UNICEF"},
        }
        household = matching_individuals.first().household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

        roles = household.individuals_and_roles(manager="pending_objects").all()
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "PRIMARY")
        self.assertEqual(role.individual.full_name, "Some Full Name")

        self.assertEqual(household_obj_data, household_data)

    def test_execute_with_postpone_deduplication(self) -> None:
        task = self.RdiXlsxCreateTask()
        self.business_area.postpone_deduplication = True
        self.business_area.save()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

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

        self.assertEqual(matching_individuals.count(), 1)

        household_data = {
            "residence_status": "REFUGEE",
            "country": GeoCountry.objects.get(iso_code2="AF").id,
            "zip_code": "2153",
            "flex_fields": {"enumerator_id": "UNICEF"},
        }
        household = matching_individuals.first().household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

        roles = household.individuals_and_roles(manager="pending_objects").all()
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "PRIMARY")
        self.assertEqual(role.individual.full_name, "Some Full Name")

        self.assertEqual(household_obj_data, household_data)

    def test_execute_with_flex_field_and_pdu(self) -> None:
        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/new_reg_data_import_flex_field.xlsx"
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
        task.execute(registration_data_import.id, import_data.id, self.business_area.id, self.program.id)

        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

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

        self.assertEqual(matching_individuals.count(), 1)

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
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "PRIMARY")
        self.assertEqual(role.individual.full_name, "Some Full Name")

        self.assertEqual(household_obj_data, household_data)
        self.assertEqual(
            individual.flex_fields,
            {
                "muac_i_f": 1,
                "jan_decimal_i_f": 12.376,
                "pdu_date_attribute": {"1": {"value": "1996-06-26", "collection_date": "2021-03-07"}},
                "pdu_string_attribute": {"1": {"value": "Test PDU Value", "collection_date": "2020-01-08"}},
            },
        )

    def test_execute_handle_identities(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )
        self.assertEqual(PendingIndividualIdentity.objects.count(), 2)
        self.assertEqual(
            PendingIndividualIdentity.objects.filter(
                number="TEST", country__iso_code2="PL", partner__name="WFP", individual__full_name="Some Full Name"
            ).count(),
            1,
        )
        self.assertEqual(
            PendingIndividualIdentity.objects.filter(
                number="WTG", country__iso_code2="PL", partner__name="UNHCR", individual__full_name="Some Full Name"
            ).count(),
            1,
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
        self.assertEqual(task.documents, {})

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

        self.assertEqual(task.documents, expected)

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
            "individual_14_other_id_i_c": {"individual": individual, "key": "other_id", "value": number},
        }
        self.assertEqual(task.documents, expected)

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.SheetImageLoader",
        ImageLoaderMock,
    )
    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.timezone.now",
        lambda: parse_datetime("2020-06-22 12:00:00-0000"),
    )
    def test_handle_document_photo_fields(self) -> None:
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
        self.assertIn("individual_14_birth_certificate_i_c", task.documents.keys())
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        self.assertEqual(birth_certificate["individual"], individual)
        self.assertEqual(birth_certificate["photo"].name, "12-2020-06-22 12:00:00+00:00.jpg")

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

        self.assertIn("individual_14_birth_certificate_i_c", task.documents.keys())
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        self.assertEqual(birth_certificate["name"], "Birth Certificate")
        self.assertEqual(birth_certificate["type"], "BIRTH_CERTIFICATE")
        self.assertEqual(birth_certificate["value"], "CD1247246Q12W")
        self.assertEqual(birth_certificate["photo"].name, "12-2020-06-22 12:00:00+00:00.jpg")

    def test_handle_geopoint_field(self) -> None:
        empty_geopoint = ""
        valid_geopoint = "51.107883, 17.038538"
        task = self.RdiXlsxCreateTask()

        result = task._handle_geopoint_field(empty_geopoint)
        self.assertEqual(result, None)

        expected = 51.107883, 17.038538
        result = task._handle_geopoint_field(valid_geopoint)
        self.assertEqual(result, expected)

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
        self.assertEqual(documents.count(), 1)

        expected = [{"document_number": "CD1247246Q12W", "type_id": doc_type.id}]
        self.assertEqual(list(documents), expected)

        document = PendingDocument.objects.first()
        photo = document.photo.name
        self.assertTrue(photo.startswith("image"))
        self.assertTrue(photo.endswith(".png"))

    def test_cast_value(self) -> None:
        task = self.RdiXlsxCreateTask()

        # None and ""
        result = task._cast_value(None, "test_header")
        self.assertIsNone(result)

        result = task._cast_value("", "test_header")
        self.assertEqual(result, "")

        # INTEGER - header: size_h_c
        result = task._cast_value("12", "size_h_c")
        self.assertEqual(result, 12)

        result = task._cast_value(12.0, "size_h_c")
        self.assertEqual(result, 12)

        # SELECT_ONE - header: gender_i_c
        result = task._cast_value("male", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("Male", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("MALE", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("TRUE", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("true", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("True", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

    def test_store_row_id(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households = PendingHousehold.objects.all()
        for household in households:
            self.assertTrue(int(household.detail_id) in [3, 4, 6])

        individuals = PendingIndividual.objects.all()
        for individual in individuals:
            self.assertTrue(int(individual.detail_id) in [3, 4, 5, 7, 8, 9])

    def test_create_tax_id_document(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        document = PendingDocument.objects.filter(individual__detail_id=5).first()
        self.assertEqual(document.type.key, IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        self.assertEqual(document.document_number, "CD1247246Q12W")

    def test_import_empty_cell_as_blank_cell(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        individual = PendingIndividual.objects.get(detail_id=3)
        self.assertEqual(individual.seeing_disability, "")
        self.assertEqual(individual.hearing_disability, "")

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
        self.assertEqual(documents.count(), 1)

        expected = [{"document_number": "TEST123_qwerty", "type_id": doc_type.id}]
        self.assertEqual(list(documents), expected)

    def test_create_delivery_mechanism_data(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)
        self.assertEqual(PendingAccount.objects.count(), 3)

        dmd1 = PendingAccount.objects.get(individual__detail_id=3)
        dmd2 = PendingAccount.objects.get(individual__detail_id=4)
        dmd3 = PendingAccount.objects.get(individual__detail_id=5)
        self.assertEqual(dmd1.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd2.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd3.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(
            dmd1.data,
            {"card_number": "164260858", "card_expiry_date": "1995-06-03T00:00:00"},
        )
        self.assertEqual(
            dmd2.data,
            {
                "card_number": "1975549730",
                "card_expiry_date": "2022-02-17T00:00:00",
                "name_of_cardholder": "Name1",
            },
        )
        self.assertEqual(
            dmd3.data,
            {
                "card_number": "870567340",
                "card_expiry_date": "2016-06-27T00:00:00",
                "name_of_cardholder": "Name2",
            },
        )
