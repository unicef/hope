from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import \
    create_household_and_individuals
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.add_pdu_fields import \
    add_specific_fields_and_populate_round


class TestAddPDUFields(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area, id="dedece11-b654-4092-bd06-3ac4c9bdea95")
        ProgramFactory(business_area=cls.business_area)  # additional program
        _, individuals = create_household_and_individuals(
            household_data={"business_area": cls.business_area, "program": cls.program},
            individuals_data=[
                {
                    "business_area": cls.business_area,
                },
                {
                    "business_area": cls.business_area,
                },
            ],
        )
        _, individuals2 = create_household_and_individuals(
            household_data={"business_area": cls.business_area, "program": cls.program},
            individuals_data=[
                {
                    "business_area": cls.business_area,
                },
                {
                    "business_area": cls.business_area,
                },
            ],
        )

        cls.individual_with_flex_field = individuals2[0]
        flex_field_existing = FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "flex_field_1"},
        )
        cls.individual_with_flex_field.flex_fields = {
            flex_field_existing.name: "value1",
        }
        cls.individual_with_flex_field.save()

    def test_add_specific_fields_and_populate_round(self) -> None:
        self.assertEqual(
            self.individual_with_flex_field.flex_fields,
            {
                "flex_field_1": "value1",
            },
        )
        self.assertEqual(FlexibleAttribute.objects.count(), 1)
        self.assertEqual(PeriodicFieldData.objects.count(), 0)
        individuals_flex_fields_before = {}
        for individual in Individual.objects.filter(program=self.program).exclude(
            id=self.individual_with_flex_field.id
        ):
            individuals_flex_fields_before[individual] = individual.flex_fields

        add_specific_fields_and_populate_round()

        self.assertEqual(FlexibleAttribute.objects.count(), 2)
        self.assertEqual(FlexibleAttribute.objects.filter(program=self.program).count(), 1)
        self.assertEqual(PeriodicFieldData.objects.count(), 1)

        pdu_field = PeriodicFieldData.objects.first()
        self.assertEqual(pdu_field.subtype, PeriodicFieldData.BOOL)
        self.assertEqual(pdu_field.number_of_rounds, 12)
        self.assertEqual(
            pdu_field.rounds_names,
            [
                "July 2024 Payment",
                "August 2024 Payment",
                "September 2024 Payment",
                "October 2024 Payment",
                "November 2024 Payment",
                "December 2024 Payment",
                "January 2025 Payment",
                "February 2025 Payment",
                "March 2025 Payment",
                "April 2025 Payment",
                "May 2025 Payment",
                "June 2025 Payment",
            ],
        )

        flex_field = pdu_field.flex_field
        self.assertEqual(flex_field.name, "valid_for_payment")
        self.assertEqual(flex_field.type, FlexibleAttribute.PDU)
        self.assertEqual(flex_field.associated_with, FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)
        self.program.refresh_from_db()
        self.assertEqual(flex_field.program, self.program)
        self.assertEqual(flex_field.label, {"English(EN)": "valid for payment"})

        rounds_data = {
            "1": {
                "value": True,
                "collection_date": "2024-07-31",
            },
            **{
                str(round): {
                    "value": None,
                }
                for round in range(2, 13)
            },
        }
        self.individual_with_flex_field.refresh_from_db()
        self.assertEqual(
            self.individual_with_flex_field.flex_fields,
            {
                "flex_field_1": "value1",
                "valid_for_payment": rounds_data,
            },
        )
        for individual in Individual.objects.filter(program=self.program).exclude(
            id=self.individual_with_flex_field.id
        ):
            self.assertEqual(
                individual.flex_fields,
                {"valid_for_payment": rounds_data, **individuals_flex_fields_before[individual]},
            )
