from django.test import TestCase

from extras.test_utils.factories.core import StorageFileFactory
from extras.test_utils.factories.household import (
    DocumentAllowDuplicatesFactory,
    DocumentTypeFactory,
    create_household,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hope.apps.core.models import BusinessArea
from hope.apps.household.management.commands.detect_paid_households import (
    find_paid_households,
)


class TestDetectingAlreadyPaidHouseholds(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.storage_file = StorageFileFactory()

        cls.business_area = BusinessArea.objects.create(
            slug="ukraine",
            code="1234",
            name="Ukraine",
            long_name="the long name of ukraine",
            region_code="3245",
            region_name="UA",
            has_data_sharing_agreement=True,
        )

        cls.payment_plan = PaymentPlanFactory(business_area=cls.business_area)
        cls.document_type = DocumentTypeFactory(key="tax_id")

        ##

        cls.household_1, cls.individuals_1 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_1.storage_obj = cls.storage_file
        cls.household_1.save()
        cls.individuals_1[0].documents.add(
            DocumentAllowDuplicatesFactory(
                individual=cls.individuals_1[0],
                type=cls.document_type,
                document_number="1",
            )
        )

        cls.household_2, cls.individuals_2 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_2.storage_obj = None
        cls.household_2.save()
        PaymentFactory(
            household=cls.household_2,
            collector=cls.individuals_2[0],
            business_area=cls.business_area,
            parent=cls.payment_plan,
            currency="PLN",
        )
        cls.individuals_2[0].documents.add(
            DocumentAllowDuplicatesFactory(
                individual=cls.individuals_2[0],
                type=cls.document_type,
                document_number="1",
            )
        )

        cls.household_3, cls.individuals_3 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_3.storage_obj = cls.storage_file
        cls.household_3.save()
        cls.individuals_3[0].documents.add(
            DocumentAllowDuplicatesFactory(
                individual=cls.individuals_3[0],
                type=cls.document_type,
                document_number="1",
            )
        )

        ##

        cls.household_4, cls.individuals_4 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_4.storage_obj = None
        cls.household_4.save()
        cls.individuals_4[0].documents.add(
            DocumentAllowDuplicatesFactory(
                individual=cls.individuals_4[0],
                type=cls.document_type,
                document_number="2",
            )
        )

        cls.household_5, cls.individuals_5 = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_5.storage_obj = cls.storage_file
        cls.household_5.save()
        cls.individuals_5[0].documents.add(
            DocumentAllowDuplicatesFactory(
                individual=cls.individuals_5[0],
                type=cls.document_type,
                document_number="2",
            )
        )

    def test_detecting_paid_hhs_loaded_via_sf(self) -> None:
        hhs = find_paid_households(self.storage_file.pk)

        # hh1 and hh3 were loaded via SF and hh2 (e.g. from RDI)
        # was already paid and had the same doc number for individual
        # so we see hh2 as a "paid household"
        assert str(self.household_1.id) not in hhs
        assert str(self.household_2.id) in hhs
        assert str(self.household_3.id) not in hhs

        # and we see hh1 and hh3 as a matching hh for hh2
        assert str(self.household_1.id) in hhs[str(self.household_2.id)]
        assert str(self.household_3.id) in hhs[str(self.household_2.id)]

        # hh3 has no payment record, so it won't be seen as paid even though hh4 has the same doc number
        assert str(self.household_4.id) not in hhs
        assert str(self.household_5.id) not in hhs
