from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase

from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    create_afghanistan,
)
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.core.models import BusinessArea, FlexibleAttribute
from hct_mis_api.apps.program.models import Program


class TestFlexibleAttribute(TransactionTestCase):
    def setUp(self) -> None:
        create_afghanistan()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")

        self.program1 = ProgramFactory(
            business_area=self.business_area,
            name="Program 1",
            status=Program.ACTIVE,
        )
        self.program2 = ProgramFactory(
            business_area=self.business_area,
            name="Program 2",
            status=Program.ACTIVE,
        )

        self.flex_field = FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )

        self.pdu_field = FlexibleAttributeForPDUFactory(
            program=self.program1,
            label="PDU Field 1",
        )

    def test_unique_name_rules_for_flex_fields(self) -> None:
        # Possible to have flex fields with the same name in different programs
        pdu_field2 = FlexibleAttributeForPDUFactory(
            program=self.program2,
            label="PDU Field 1",
        )
        self.assertEqual(FlexibleAttribute.objects.filter(name=pdu_field2.name).count(), 2)

        # Not possible to have flex fields with the same name in the same program
        with self.assertRaises(IntegrityError) as ie_context:
            FlexibleAttributeForPDUFactory(
                program=self.program1,
                label="PDU Field 1",
            )
        self.assertIn(
            'duplicate key value violates unique constraint "unique_name_program"',
            str(ie_context.exception),
        )

        # Not possible to have flex fields with the same name without a program
        with self.assertRaises(IntegrityError) as ie_context:
            FlexibleAttribute.objects.create(
                name=self.flex_field.name,
                type=FlexibleAttribute.STRING,
                associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
                label={"English(EN)": "value"},
            )
        self.assertIn(
            'duplicate key value violates unique constraint "unique_name_without_program"',
            str(ie_context.exception),
        )

        # Not possible to have flex fields with the same name in a program and without a program
        with self.assertRaises(ValidationError) as ve_context:
            FlexibleAttribute.objects.create(
                name=self.pdu_field.name,
                type=FlexibleAttribute.STRING,
                associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
                label={"English(EN)": "value"},
            )
        self.assertIn(
            f'Flex field with name "{self.pdu_field.name}" already exists inside a program.',
            str(ve_context.exception),
        )

        with self.assertRaises(ValidationError) as ve_context:
            FlexibleAttributeForPDUFactory(
                program=self.program1,
                label="Flex Field 1",
            )
        self.assertIn(
            f'Flex field with name "{self.flex_field.name}" already exists without a program.',
            str(ve_context.exception),
        )

    def test_flexible_attribute_label_without_english_en_key(self) -> None:
        with self.assertRaisesMessage(ValidationError, 'The "English(EN)" key is required in the label.'):
            FlexibleAttribute.objects.create(
                name="flex_field_2",
                type=FlexibleAttribute.STRING,
                associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
                label={"other value": "value"},
            )
        flexible_attribute = FlexibleAttribute.objects.create(
            name="flex_field_2",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "value"},
        )
        with self.assertRaisesMessage(ValidationError, 'The "English(EN)" key is required in the label.'):
            flexible_attribute.label = {"wrong": "value"}
            flexible_attribute.save()
