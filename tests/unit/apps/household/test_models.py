from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.models.business_area import BusinessArea
from hope.models.country import Country
from hope.models.document import Document
from hope.models.document_type import DocumentType
from hope.models.household import (
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
    Household,
)
from hope.models.utils import MergeStatusModel


class TestHousehold(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area)

        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area_type_level_3 = AreaTypeFactory(
            name="State3",
            area_level=3,
        )
        area_type_level_4 = AreaTypeFactory(
            name="State4",
            area_level=4,
        )
        cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
        cls.area2 = AreaFactory(
            name="City Test2",
            area_type=area_type_level_2,
            p_code="area2",
            parent=cls.area1,
        )
        cls.area3 = AreaFactory(
            name="City Test3",
            area_type=area_type_level_3,
            p_code="area3",
            parent=cls.area2,
        )
        cls.area4 = AreaFactory(
            name="City Test4",
            area_type=area_type_level_4,
            p_code="area4",
            parent=cls.area3,
        )

    def test_household_admin_areas_set(self) -> None:
        household, (individual) = create_household(household_args={"size": 1, "business_area": self.business_area})
        household.admin1 = self.area1
        household.save()

        household.set_admin_areas()
        household.refresh_from_db()

        assert household.admin_area == self.area1
        assert household.admin1 == self.area1
        assert household.admin2 is None
        assert household.admin3 is None
        assert household.admin4 is None

        household.set_admin_areas(self.area4)
        household.refresh_from_db()

        assert household.admin_area == self.area4
        assert household.admin1 == self.area1
        assert household.admin2 == self.area2
        assert household.admin3 == self.area3
        assert household.admin4 == self.area4

        household.set_admin_areas(self.area3)
        household.refresh_from_db()

        assert household.admin_area == self.area3
        assert household.admin1 == self.area1
        assert household.admin2 == self.area2
        assert household.admin3 == self.area3
        assert household.admin4 is None

    def test_household_set_admin_area_based_on_lowest_admin(self) -> None:
        household, _ = create_household(household_args={"size": 1, "business_area": self.business_area})
        household.admin1 = None
        household.admin2 = None
        household.admin3 = None
        household.admin4 = self.area4

        household.set_admin_areas()
        household.refresh_from_db()

        assert household.admin_area == self.area4
        assert household.admin1 == self.area1
        assert household.admin2 == self.area2
        assert household.admin3 == self.area3
        assert household.admin4 == self.area4

    def test_remove_household(self) -> None:
        household1, _ = create_household(
            household_args={
                "size": 1,
                "business_area": self.business_area,
                "unicef_id": "HH-9090",
            }
        )
        household2, _ = create_household(
            household_args={
                "size": 1,
                "business_area": self.business_area,
                "unicef_id": "HH-9191",
            }
        )
        household1.delete()
        assert Household.all_objects.filter(unicef_id="HH-9090").first().is_removed is True
        household2.delete(soft=False)
        assert Household.all_objects.filter(unicef_id="HH-9191").first() is None

    def test_unique_unicef_id_per_program_constraint(self) -> None:
        HouseholdFactory(unicef_id="HH-123", program=self.program)
        HouseholdFactory(unicef_id="HH-000", program=self.program)
        with pytest.raises(IntegrityError):
            HouseholdFactory(unicef_id="HH-123", program=self.program)

    def test_geopoint(self) -> None:
        household, _ = create_household(household_args={"size": 1, "business_area": self.business_area})
        household.geopoint = 1.2, 0.5  # type: ignore
        assert household.longitude == 1.2
        assert household.latitude == 0.5
        household.geopoint = None
        assert household.longitude is None
        assert household.latitude is None


class TestDocument(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        cls.business_area = create_afghanistan()
        afghanistan = Country.objects.get(name="Afghanistan")
        _, (individual,) = create_household(household_args={"size": 1, "business_area": cls.business_area})

        cls.country = afghanistan
        cls.individual = individual
        cls.program = ProgramFactory()

    def test_raise_error_on_creating_duplicated_documents_with_the_same_number_not_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_OTHER],
            defaults={
                "label": "Other",
                "unique_for_individual": False,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        with pytest.raises(IntegrityError):
            Document.objects.create(
                document_number="213123",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
                rdi_merge_status=MergeStatusModel.MERGED,
            )

    def test_create_duplicated_documents_with_different_numbers_and_not_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_OTHER],
            defaults={
                "label": "Other",
                "unique_for_individual": False,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        try:
            Document.objects.create(
                document_number="213124",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
                rdi_merge_status=MergeStatusModel.MERGED,
            )
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")

    def test_raise_error_on_creating_duplicated_documents_with_the_same_number_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            defaults={
                "label": "National Passport",
                "unique_for_individual": True,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        with pytest.raises(IntegrityError):
            Document.objects.create(
                document_number="213123",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
                rdi_merge_status=MergeStatusModel.MERGED,
            )

    def test_create_document_of_the_same_type_for_individual_not_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            defaults={
                "label": "National Passport",
                "unique_for_individual": False,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
        )

        try:
            Document.objects.create(
                document_number="11111",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
            )
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")

    def test_raise_error_on_creating_document_of_the_same_type_for_individual_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            defaults={
                "label": "National Passport",
                "unique_for_individual": True,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
        )

        with pytest.raises(IntegrityError):
            Document.objects.create(
                document_number="11111",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
            )

    def test_raise_error_on_creating_duplicated_documents_with_different_numbers_and_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            defaults={
                "label": "National Passport",
                "unique_for_individual": True,
            },
        )

        Document.objects.create(
            document_number="123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        with pytest.raises(IntegrityError):
            Document.objects.create(
                document_number="456",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
                program=self.program,
                rdi_merge_status=MergeStatusModel.MERGED,
            )

    def test_create_duplicated_documents_with_different_numbers_and_types_and_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
            defaults={
                "label": "National Passport",
                "unique_for_individual": True,
            },
        )
        document_type2, _ = DocumentType.objects.update_or_create(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
            defaults={
                "label": "Tax Number Identification",
                "unique_for_individual": True,
            },
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
            program=self.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        try:
            Document.objects.create(
                document_number="213124",
                individual=self.individual,
                country=self.country,
                type=document_type2,
                status=Document.STATUS_VALID,
                program=self.program,
                rdi_merge_status=MergeStatusModel.MERGED,
            )
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")


class TestIndividualModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=business_area)

    def test_unique_unicef_id_per_program_constraint(self) -> None:
        IndividualFactory(unicef_id="IND-123", program=self.program)
        IndividualFactory(unicef_id="IND-000", program=self.program)
        with pytest.raises(IntegrityError):
            IndividualFactory(unicef_id="IND-123", program=self.program)

    def test_mark_as_distinct_raise_errors(self) -> None:
        ind = IndividualFactory(unicef_id="IND-333", program=self.program)
        doc_type = DocumentTypeFactory(key="registration_token")
        country = CountryFactory()
        DocumentFactory(
            status=Document.STATUS_VALID,
            program=self.program,
            type=doc_type,
            document_number="123456ABC",
            individual=ind,
            country=country,
        )
        doc_2 = DocumentFactory(
            status=Document.STATUS_INVALID,
            program=self.program,
            type=doc_type,
            document_number="aaa",
            individual=ind,
            country=country,
        )
        doc_2.document_number = "123456ABC"
        doc_2.save()

        with pytest.raises(Exception, match="IND-333: Valid Document already exists: 123456ABC."):
            ind.mark_as_distinct()
