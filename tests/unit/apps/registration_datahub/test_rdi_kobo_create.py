from io import BytesIO
import json
from pathlib import Path
import secrets
from typing import Any, Dict
from unittest import mock

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.db.models.fields.files import ImageFieldFile
from django.forms import model_to_dict
from django.test import TestCase
from django_countries.fields import Country
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.payment import generate_delivery_mechanisms
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.geo import models as geo_models
from hope.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hope.apps.payment.models import PendingAccount
from hope.apps.registration_data.models import ImportData, RegistrationDataImport
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRdiKoboCreateTask(TestCase):
    @staticmethod
    def _return_test_image(*args: Any, **kwargs: Any) -> BytesIO:
        return BytesIO(Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/image.png").read_bytes())

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init_geo_fixtures")
        create_afghanistan()
        from hope.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        cls.RdiKoboCreateTask = RdiKoboCreateTask

        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))
        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

        content = Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/kobo_submissions.json").read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )

        content = Path(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/kobo_submissions_collectors.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions_collectors.json")
        cls.import_data_collectors = ImportData.objects.create(
            file=file,
            number_of_households=2,
            number_of_individuals=5,
        )

        cls.business_area = BusinessArea.objects.first()
        cls.business_area.kobo_username = "1234ABC"
        cls.business_area.save()

        country = geo_models.Country.objects.first()

        admin1_type = geo_models.AreaType.objects.create(name="Bakool", area_level=1, country=country)
        admin1 = geo_models.Area.objects.create(p_code="SO25", name="SO25", area_type=admin1_type)

        admin2_type = geo_models.AreaType.objects.create(name="Ceel Barde", area_level=2, country=country)
        geo_models.Area.objects.create(p_code="SO2502", name="SO2502", parent=admin1, area_type=admin2_type)

        cls.program = ProgramFactory(status="ACTIVE")
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area,
            program=cls.program,
            import_data=cls.import_data,
            number_of_individuals=99,
            number_of_households=33,
        )
        rebuild_search_index()
        generate_delivery_mechanisms()

    @mock.patch(
        "hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute(self) -> None:
        self.business_area.postpone_deduplication = True
        self.business_area.save()
        # just random number of HH and Ind
        assert self.registration_data_import.number_of_households == 33
        assert self.registration_data_import.number_of_individuals == 99

        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
        task.execute(self.import_data.id, self.program.id)

        self.registration_data_import.refresh_from_db(
            fields=["status", "number_of_households", "number_of_individuals"]
        )
        assert self.registration_data_import.status == RegistrationDataImport.IN_REVIEW
        assert self.registration_data_import.number_of_households == 1
        assert self.registration_data_import.number_of_individuals == 2

        households = PendingHousehold.objects.all()
        individuals = PendingIndividual.objects.all()
        documents = PendingDocument.objects.all()

        assert households.count() == 1
        assert individuals.count() == 2
        assert documents.count() == 3

        individual = individuals.get(full_name="Test Testowski")

        individuals_obj_data = model_to_dict(
            individual,
            ("country", "sex", "age", "marital_status", "relationship"),
        )
        expected_ind: Dict = {
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
        expected_hh: Dict = {
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

    @mock.patch(
        "hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute_multiple_collectors(self) -> None:
        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
        task.execute(self.import_data_collectors.id, self.program.id)
        households = PendingHousehold.objects.all()
        individuals = PendingIndividual.objects.all()

        assert households.count() == 3  # related to AB#171697
        assert individuals.count() == 7  # related to AB#171697

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
        second_household = households.get(
            size=2,
        )

        first_household_collectors = first_household.individuals_and_roles.order_by(
            "individual__full_name"
        ).values_list("individual__full_name", "role")
        assert list(first_household_collectors) == [
            ("Tesa Testowski 222", "ALTERNATE"),
            ("Test Testowski 222", "PRIMARY"),
        ]
        second_household_collectors = second_household.individuals_and_roles.values_list(
            "individual__full_name", "role"
        )
        assert list(second_household_collectors) == [("Test Testowski", "PRIMARY")]

    @mock.patch(
        "hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_image_field(self) -> None:
        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
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

        result = task._handle_image_field("image_is_not_there.gif", False)
        assert result is None

        result = task._handle_image_field("signature-14_59_24.png", False)
        assert isinstance(result, File)
        assert result.name == "signature-14_59_24.png"

        result = task._handle_image_field("signature-21_37.png", False)
        assert isinstance(result, File)
        assert result.name == "signature-21_37.png"

    def test_handle_geopoint_field(self) -> None:
        geopoint = "51.107883 17.038538"
        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)

        expected = 51.107883, 17.038538
        result = task._handle_geopoint_field(geopoint, False)
        assert result == expected

    def test_cast_boolean_value(self) -> None:
        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)

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

    @mock.patch(
        "hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_documents_and_identities(self) -> None:
        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
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
        individual = IndividualFactory(rdi_merge_status=MergeStatusModel.PENDING)
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

    def _generate_huge_file(self) -> None:
        base_form = {
            "_notes": [],
            "household_questions/household_location/address_h_c": "Some Address 12",
            "household_questions/group_qo2zo48/f_0_5_age_group_h_c": "0",
            "monthly_income_questions/total_inc_h_f": "0",
            "household_questions/group_qo2zo48/m_6_11_age_group_h_c": "0",
            "household_questions/group_cu1lc89/m_6_11_disability_h_c": "0",
            "_xform_id_string": "ayp9jVNe5crcGerVjCjGj4",
            "_bamboo_dataset_id": "",
            "_tags": [],
            "household_questions/group_qo2zo48/pregnant_h_c": "0",
            "health_questions/pregnant_member_h_c": "0",
            "enumerator/name_enumerator": "Test",
            "monthly_expenditures_questions/total_expense_h_f": "0",
            "individual_questions": [
                {
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "65",
                    "individual_questions/more_information/marital_status_i_c": "single",
                    "individual_questions/more_information/id_type_i_c": "birth_certificate drivers_license",
                    "individual_questions/individual_index": "1",
                    "individual_questions/full_name_i_c": "Jan Kowalski",
                    "individual_questions/more_information/birth_certificate_photo_i_c": "test-11_53_20.png",
                    "individual_questions/relationship_i_c": "head",
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "1",
                    "individual_questions/more_information/drivers_license_no_i_c": "ASD12367432Q",
                    "individual_questions/gender_i_c": "male",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                    "individual_questions/more_information/birth_certificate_no_i_c": "89671532",
                    "individual_questions/birth_date_i_c": "1955-07-28",
                }
            ],
            "household_questions/group_cu1lc89/f_12_17_disability_h_c": "0",
            "meta/instanceID": "uuid:84366d01-770a-42f0-b0f8-d498e35dd9e8",
            "household_questions/group_qo2zo48/f_12_17_age_group_h_c": "0",
            "end": "2020-06-18T12:05:31.700+02:00",
            "household_questions/group_qo2zo48/f_6_11_age_group_h_c": "0",
            "household_questions/group_cu1lc89/f_adults_disability_h_c": "0",
            "household_questions/group_qo2zo48/m_0_5_age_group_h_c": "0",
            "household_questions/group_qo2zo48/f_adults_h_c": "0",
            "household_questions/group_cu1lc89/m_adults_disability_h_c": "0",
            "start": "2020-06-15T11:49:14.246+02:00",
            "_attachments": [
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/test-11_53_31.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "id": 35910755,
                    "xform": 560567,
                },
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/test-11_53_20.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "id": 35910754,
                    "xform": 560567,
                },
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/signature-11_53_11.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "id": 35910753,
                    "xform": 560567,
                },
            ],
            "_version_": "v8ia7fyHZNkkaUxuE28vDv",
            "_status": "submitted_via_web",
            "__version__": "vDTUHL6mTgLv2BPcBoRu5v",
            "meta/deprecatedID": "uuid:2946bbb1-27fd-438a-b716-d864591808b2",
            "wash_questions/total_liter_yesterday_h_f": "0",
            "food_security_questions/FCS_h_f": "NaN",
            "food_security_questions/cereals_tuber_score_h_f": "NaN",
            "_validation_status": {},
            "_uuid": "84366d01-770a-42f0-b0f8-d498e35dd9e8",
            "consent/consent_sign_h_c": "signature-11_53_11.png",
            "household_questions/household_location/country_h_c": "POL",
            "household_questions/group_cu1lc89/f_6_11_disability_h_c": "0",
            "_submitted_by": None,
            "household_questions/size_h_c": "1",
            "household_questions/group_cu1lc89/f_0_5_disability_h_c": "0",
            "household_questions/household_location/country_origin_h_c": "AFG",
            "household_questions/group_cu1lc89/m_0_5_disability_h_c": "0",
            "formhub/uuid": "a716ab3cdfbc411aac9fa081874b6aa1",
            "enumerator/group_fl9ht28/org_enumerator": "unicef",
            "household_questions/household_location/hh_geopoint_h_c": "51.106648 17.033256 0 0",
            "monthly_income_questions/round_total_income_h_f": "0",
            "_submission_time": "2020-06-15T09:54:07",
            "household_questions/household_location/residence_status_h_c": "refugee",
            "_geolocation": [51.106648, 17.033256],
            "monthly_expenditures_questions/round_total_expense_h_f": "0",
            "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
            "household_questions/group_qo2zo48/m_12_17_age_group_h_c": "0",
            "individual_questions_count": "1",
            "_id": 104545171,
            "household_questions/group_qo2zo48/m_adults_h_c": "1",
            "household_questions/group_cu1lc89/m_12_17_disability_h_c": "0",
        }

        result = []

        for _ in range(10000):
            copy: Dict = {**base_form}

            new_individuals = []
            for x in range(4):
                individual: Dict = {
                    **copy["individual_questions"][0],
                    "individual_questions/more_information/drivers_license_no_i_c": secrets.token_hex(15),
                    "individual_questions/more_information/birth_certificate_no_i_c": secrets.token_hex(15),
                    "individual_questions/relationship_i_c": "head" if x == 0 else "NON_BENEFICIARY",
                }
                new_individuals.append(individual)

            copy["individual_questions"] = new_individuals

            result.append(copy)

        with open(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/big_json.json",
            "w+",
        ) as json_file:
            json_file.write(json.dumps(result))

    def test_handle_household_dict(self) -> None:
        households_to_create = []
        collectors_to_create, head_of_households_mapping, individuals_ids_hash_dict = (
            {},
            {},
            {},
        )
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

        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
        task.handle_household(
            collectors_to_create,
            head_of_households_mapping,
            household,
            households_to_create,
            individuals_ids_hash_dict,
            submission_meta_data,
            1,
        )
        hh = households_to_create[0]

        assert len(households_to_create) == 1
        assert hh.detail_id == "kobo_asset_id_string_OR_detail_id"
        assert hh.kobo_submission_time.isoformat() == "2022-02-22T12:22:22"
        assert hh.kobo_submission_uuid == "5b6f30ee-010b-4bd5-a510-e78f062af155"

    def test_handle_household_drc_hotfix_dict(self) -> None:
        program = ProgramFactory(id="f5a67047-714f-459a-8ead-911d21f7925c", status="ACTIVE")
        self.registration_data_import.program = program
        self.registration_data_import.save()
        country = geo_models.Country.objects.first()
        admin4_type = geo_models.AreaType.objects.create(name="Bakool", area_level=4, country=country)
        admin4 = geo_models.Area.objects.create(p_code="CD8309ZS01AS01", name="CD8309ZS01AS01", area_type=admin4_type)
        admin4_mapped = geo_models.Area.objects.create(
            p_code="CD8311ZS02AS04", name="CD8311ZS02AS04", area_type=admin4_type
        )

        households_to_create = []
        collectors_to_create, head_of_households_mapping, individuals_ids_hash_dict = (
            {},
            {},
            {},
        )
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
            "admin4_h_c": admin4.p_code,
            "village_h_c": "VillageName",
            "nearest_school_h_f": "next",
            "hh_geopoint_h_c": "46.123 6.312 0 0",
            "size_h_c": "5",
            "children_under_18_h_f": "2",
            "children_6_to_11_h_f": "1",
            "hohh_is_caregiver_h_f": "0",
            "alternate_collector": "1",
            "_xform_id_string": "kobo_asset_id_string_OR_detail_id",
            "_uuid": "123123-411d-85f1-123123",
            "_submission_time": "2022-02-22T12:22:22",
        }
        submission_meta_data = {
            "kobo_submission_uuid": "123123-411d-85f1-123123",
            "kobo_asset_id": "kobo_asset_id_string_OR_detail_id",
            "kobo_submission_time": "2022-02-22T12:22:22",
        }

        task = self.RdiKoboCreateTask(self.registration_data_import.id, self.business_area.id)
        task.handle_household(
            collectors_to_create,
            head_of_households_mapping,
            household,
            households_to_create,
            individuals_ids_hash_dict,
            submission_meta_data,
            1,
        )
        hh = households_to_create[0]

        assert len(households_to_create) == 1
        assert hh.admin4 == admin4_mapped
