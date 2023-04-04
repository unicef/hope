from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
    Document,
    DocumentType,
)


class TestHousehold(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

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
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code="area3", parent=cls.area2)
        cls.area4 = AreaFactory(name="City Test4", area_type=area_type_level_4, p_code="area4", parent=cls.area3)

    def test_household_admin_areas_set(self) -> None:
        household, (individual) = create_household(household_args={"size": 1, "business_area": self.business_area})
        household.admin_area = self.area1
        household.admin1 = self.area1
        household.save()

        household.set_admin_areas()
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area1)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, None)
        self.assertEqual(household.admin3, None)
        self.assertEqual(household.admin4, None)

        household.set_admin_areas(self.area4)
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area4)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, self.area2)
        self.assertEqual(household.admin3, self.area3)
        self.assertEqual(household.admin4, self.area4)

        household.set_admin_areas(self.area3)
        household.refresh_from_db()

        self.assertEqual(household.admin_area, self.area3)
        self.assertEqual(household.admin1, self.area1)
        self.assertEqual(household.admin2, self.area2)
        self.assertEqual(household.admin3, self.area3)
        self.assertEqual(household.admin4, None)


class TestDocument(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("loadcountries")
        business_area = create_afghanistan()
        afghanistan = Country.objects.get(name="Afghanistan")
        _, (individual,) = create_household(household_args={"size": 1, "business_area": business_area})

        cls.country = afghanistan
        cls.individual = individual

    def test_raise_error_on_creating_duplicated_documents_with_the_same_number_not_unique_for_individual(self) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_OTHER,
            defaults=dict(
                label="Other",
                unique_for_individual=False,
            ),
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
        )

        with self.assertRaises(IntegrityError):
            Document.objects.create(
                document_number="213123",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
            )

    def test_create_duplicated_documents_with_different_numbers_and_not_unique_for_individual(self) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_OTHER,
            defaults=dict(
                label="Other",
                unique_for_individual=False,
            ),
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
        )

        try:
            Document.objects.create(
                document_number="213124",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
            )
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")

    def test_raise_error_on_creating_duplicated_documents_with_the_same_number_unique_for_individual(self) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
            defaults=dict(
                label="National Passport",
                unique_for_individual=True,
            ),
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
        )

        with self.assertRaises(IntegrityError):
            Document.objects.create(
                document_number="213123",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
            )

    def test_raise_error_on_creating_duplicated_documents_with_different_numbers_and_unique_for_individual(
        self,
    ) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
            defaults=dict(
                label="National Passport",
                unique_for_individual=True,
            ),
        )

        Document.objects.create(
            document_number="123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
        )

        with self.assertRaises(IntegrityError):
            Document.objects.create(
                document_number="456",
                individual=self.individual,
                country=self.country,
                type=document_type,
                status=Document.STATUS_VALID,
            )

    def test_create_duplicated_documents_with_different_numbers_and_types_and_unique_for_individual(self) -> None:
        document_type, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
            defaults=dict(
                label="National Passport",
                unique_for_individual=True,
            ),
        )
        document_type2, _ = DocumentType.objects.update_or_create(
            type=IDENTIFICATION_TYPE_TAX_ID,
            defaults=dict(
                label="Tax Number Identification",
                unique_for_individual=True,
            ),
        )

        Document.objects.create(
            document_number="213123",
            individual=self.individual,
            country=self.country,
            type=document_type,
            status=Document.STATUS_VALID,
        )

        try:
            Document.objects.create(
                document_number="213124",
                individual=self.individual,
                country=self.country,
                type=document_type2,
                status=Document.STATUS_VALID,
            )
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")
