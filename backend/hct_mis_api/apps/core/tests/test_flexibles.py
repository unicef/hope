from django.contrib.admin import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, RequestFactory

from core.admin import FlexibleAttributeAdmin
from core.models import (
    FlexibleAttribute,
    BusinessArea,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)


class MockSuperUser:
    def has_perm(self, perm):
        return True


class TestFlexibles(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        site = AdminSite()
        self.admin = FlexibleAttributeAdmin(FlexibleAttribute, site)
        call_command("loadbusinessareas")

    def test_flexible_init_update_delete(self):
        business_area = BusinessArea.objects.first()
        data = {"business_area": business_area.id}
        with open(
            f"hct_mis_api/apps/core/tests/test_files/flex_init.xls", "rb"
        ) as f:
            file_upload = SimpleUploadedFile(
                "xls_file", f.read(), content_type="text/html"
            )
            data["xls_file"] = file_upload
        request = self.factory.post(
            "import-xls/", data=data, format="multipart"
        )
        request.user = MockSuperUser()
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = self.admin.import_xls(request)

        # Check if created correct amount of objects
        expected_attributes_count = 66
        expected_groups_count = 10
        expected_repeated_groups = 2
        expected_choices_count = 441

        attrs_from_db = FlexibleAttribute.objects.filter(
            business_area=business_area
        )
        groups_from_db = FlexibleAttributeGroup.objects.filter(
            business_area=business_area
        )
        choices_from_db = FlexibleAttributeChoice.objects.filter(
            business_area=business_area
        )

        assert expected_attributes_count == len(attrs_from_db)
        assert expected_groups_count == len(groups_from_db)
        assert expected_choices_count == len(choices_from_db)
        assert expected_repeated_groups == len(
            groups_from_db.filter(repeatable=True)
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

        household_questions_group = FlexibleAttributeGroup.objects.get(
            name="household_questions"
        )
        individual_questions_group = FlexibleAttributeGroup.objects.get(
            name="individual_questions"
        )
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
            "If any child was sick, When he/she had an illness with a cough, did he/she breathe faster than usual with short, rapid breaths or have difficulty breathing?",
            "If above is Yes, did you seek advice or treatment for the illness from any source?",
            "If member is a child, does he/she ever been enrolled in school?",
            "If member is a child, does he/she currently enrolled in school",
        ]

        yes_choice = FlexibleAttributeChoice.objects.get(
            list_name="yes_no", name=1
        )
        no_choice = FlexibleAttributeChoice.objects.get(
            list_name="yes_no", name=0
        )

        for name, label in zip(selected_attribs, attrib_english_labels):
            attrib = FlexibleAttribute.objects.get(name=name)
            assert attrib.label["English(EN)"] == label
            assert yes_choice.flex_attributes.filter(id=attrib.id).exists()
            assert no_choice.flex_attributes.filter(id=attrib.id).exists()

        # Test updating/deleting values
        with open(
            f"hct_mis_api/apps/core/tests/test_files/flex_updated.xls", "rb"
        ) as f:
            file_upload = SimpleUploadedFile(
                "xls_file", f.read(), content_type="text/html"
            )
            data["xls_file"] = file_upload
        request = self.factory.post(
            "import-xls/", data=data, format="multipart"
        )
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = self.admin.import_xls(request)

        deleted_groups = [
            "household_questions",
            "header_hh_size",
            "composition_female",
            "composition_male",
            "household_vulnerabilities",
        ]

        groups_from_db = FlexibleAttributeGroup.objects.filter(
            name__in=deleted_groups
        )

        assert len(groups_from_db) == 0

        consent_group = FlexibleAttributeGroup.objects.get(name="consent")
        assert consent_group.label["English(EN)"] == "Consent Edited"

        introduction = FlexibleAttribute.objects.filter(
            type="note", name="introduction"
        ).exists()
        assert introduction is False
