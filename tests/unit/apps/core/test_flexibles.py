from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

from xlrd import XLRDError

from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter
from hct_mis_api.apps.core.models import (
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)


class MockSuperUser:
    def has_perm(self, perm: Any) -> bool:
        return True


class TestFlexibles(TestCase):
    def load_xls(self, name: str) -> None:
        task = FlexibleAttributeImporter()
        task.import_xls(f"{settings.TESTS_ROOT}/apps/core/test_files/{name}")

    def test_flexible_init_update_delete(self) -> None:
        self.load_xls("flex_init.xls")
        # Check if created correct amount of objects
        expected_attributes_count = 45
        expected_groups_count = 10
        expected_repeated_groups = 2
        expected_choices_count = 441

        attrs_from_db = FlexibleAttribute.objects.all()
        groups_from_db = FlexibleAttributeGroup.objects.all()
        choices_from_db = FlexibleAttributeChoice.objects.all()

        self.assertEqual(expected_attributes_count, len(attrs_from_db))
        self.assertEqual(expected_groups_count, len(groups_from_db))
        self.assertEqual(expected_choices_count, len(choices_from_db))
        self.assertEqual(
            expected_repeated_groups,
            len(groups_from_db.filter(repeatable=True)),
        )

        """
        How group tree should look like:

        consent
        household_questions
            header_hh_size
            composition_female
            composition_male
            household_vulnerabilities
        individual_questions
            contact_details_i_c
            id_questions
            vulnerability_questions
        """

        household_questions_group = FlexibleAttributeGroup.objects.get(name="household_questions")
        individual_questions_group = FlexibleAttributeGroup.objects.get(name="individual_questions")
        groups_tree_dict = {
            "consent": None,
            "household_questions": None,
            "header_hh_size": household_questions_group,
            "composition_female": household_questions_group,
            "composition_male": household_questions_group,
            "household_vulnerabilities": household_questions_group,
            "individual_questions": None,
            "contact_details_i_c": individual_questions_group,
            "id_questions": individual_questions_group,
            "vulnerability_questions": individual_questions_group,
        }

        for name, group in groups_tree_dict.items():
            current_group = FlexibleAttributeGroup.objects.get(name=name)
            assert current_group.parent == group

        """
        Flex Attributes that should be attached to Yes_No Flex Choice
        """
        selected_attribs = [
            "unaccompanied_child_h_f",
            "recent_illness_child_h_f",
            "difficulty_breathing_h_f",
            "treatment_h_f",
            "school_enrolled_before_i_f",
            "school_enrolled_i_f",
        ]

        # English labels for attributes mentioned above
        attrib_english_labels = [
            "Does your family host an unaccompanied child / fosterchild?",
            "Has any of your children been ill with cough and fever at any time in the last 2 weeks?",
            "If any child was sick, When he/she had an illness with a cough, did he/she breathe "
            "faster than usual with short, rapid breaths or have difficulty breathing?",
            "If above is Yes, did you seek advice or treatment for the illness from any source?",
            "If member is a child, does he/she ever been enrolled in school?",
            "If member is a child, does he/she currently enrolled in school",
        ]

        yes_choice = FlexibleAttributeChoice.objects.get(list_name="yes_no", name=1)
        no_choice = FlexibleAttributeChoice.objects.get(list_name="yes_no", name=0)

        for name, label in zip(selected_attribs, attrib_english_labels):
            attrib = FlexibleAttribute.objects.get(name=name)
            expected_associated_with = 0 if attrib.name[-4:] == "_h_f" else 1
            self.assertEqual(attrib.label["English(EN)"], label)
            self.assertEqual(attrib.associated_with, expected_associated_with)
            self.assertTrue(yes_choice.flex_attributes.filter(id=attrib.id).exists())
            self.assertTrue(no_choice.flex_attributes.filter(id=attrib.id).exists())

        # Test updating/deleting values
        self.load_xls("flex_updated.xls")

        deleted_groups = [
            "household_questions",
            "header_hh_size",
            "composition_female",
            "composition_male",
            "household_vulnerabilities",
        ]

        groups_from_db = FlexibleAttributeGroup.objects.filter(name__in=deleted_groups)

        deleted_groups_from_db = FlexibleAttributeGroup.all_objects.filter(name__in=deleted_groups)
        self.assertEqual(len(groups_from_db), 0)

        # check if they are soft deleted
        self.assertEqual(len(deleted_groups_from_db), 5)

        consent_group = FlexibleAttributeGroup.objects.get(name="consent")
        self.assertEqual(consent_group.label["English(EN)"], "Consent Edited")

        introduction = FlexibleAttribute.objects.filter(type="note", name="introduction_h_f").exists()
        self.assertFalse(introduction)

    def test_flexibles_type_validation(self) -> None:
        # import valid file
        self.load_xls("flex_init_valid_types.xls")

        groups_from_db = FlexibleAttributeGroup.objects.all()
        flex_attrs_from_db = FlexibleAttribute.objects.all()

        self.assertEqual(len(groups_from_db), 1)
        self.assertEqual(len(flex_attrs_from_db), 1)

        assert flex_attrs_from_db.filter(
            type="STRING",
            name="introduction_h_f",
            label={
                "French(FR)": "",
                "English(EN)": "1) Greeting    "
                "2) Introduce yourself politely    "
                "3) I represent UNICEF    "
                "4) You have been selected to help us conduct "
                "a household needs assessment in your area.    "
                "5) This survey is voluntary and the information"
                " you provide will remain strictly "
                "confidential.    "
                "6) Participating in the evaluation does not "
                "mean that you are entitled to assistance. "
                "UNICEF will analyze the data for "
                "possible eligibility.    "
                "7) I will ask you a few questions "
                "and observe your installations in the house.",
            },
        )

        self.assertRaises(ValidationError, self.load_xls, "flex_update_invalid_types.xls")
        group = FlexibleAttributeGroup.objects.all()
        attribs = FlexibleAttribute.objects.all()
        self.assertEqual(len(group), 1)
        self.assertEqual(len(attribs), 1)

    def test_flexibles_missing_name(self) -> None:
        self.assertRaisesMessage(ValidationError, "Name is required", self.load_xls, "flex_field_missing_name.xls")
        group = FlexibleAttributeGroup.objects.all()
        attribs = FlexibleAttribute.objects.all()
        self.assertEqual(len(group), 0)
        self.assertEqual(len(attribs), 0)

    def test_flexibles_missing_english_label(self) -> None:
        self.assertRaisesMessage(
            ValidationError, "English label cannot be empty", self.load_xls, "flex_field_missing_english_label.xls"
        )
        group = FlexibleAttributeGroup.objects.all()
        attribs = FlexibleAttribute.objects.all()
        self.assertEqual(len(group), 0)
        self.assertEqual(len(attribs), 0)

    def test_load_invalid_file(self) -> None:
        self.assertRaises(XLRDError, self.load_xls, "erd arrows.jpg")

    def test_reimport_soft_deleted_objects(self) -> None:
        self.load_xls("flex_init_valid_types.xls")
        field = FlexibleAttribute.objects.get(name="introduction_h_f")
        group = FlexibleAttributeGroup.objects.get(name="consent")

        self.assertTrue(field)
        self.assertTrue(group)

        field.delete()
        group.delete()

        self.assertTrue(field.is_removed)
        self.assertTrue(group.is_removed)

        self.load_xls("flex_init_valid_types.xls")

        self.assertEqual(field.group, group)
