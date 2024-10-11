from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.steficon.fixtures import RuleFactory
from hct_mis_api.apps.steficon.forms import RuleForm
from hct_mis_api.apps.steficon.models import Rule


class TestRuleForm(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()

    def test_clean_method(self) -> None:
        # check with all fields
        form_data = {
            "allowed_business_areas": [self.business_area],
            "definition": "result.value=0",
            "deprecated": False,
            "description": "Some text here",
            "enabled": True,
            "flags": None,
            "language": "python",
            "name": "Test 123",
            "security": 0,
            "type": "TARGETING",
        }
        form = RuleForm(data=form_data)
        self.assertTrue(form.is_valid())

        # config.USE_BLACK = True
        with self.settings(USE_BLACK=True):
            form_data_with_black = {
                "name": "Test",
                "definition": "result.value = 0",
                "language": "python",
                "description": "Some text here",
                "enabled": True,
                "deprecated": False,
                "security": 0,
                "type": "TARGETING",
                "allowed_business_areas": [self.business_area],
            }
            form_with_black = RuleForm(data=form_data_with_black)
            self.assertTrue(form_with_black.is_valid())
            cleaned_data_with_black = form_with_black.clean()
            self.assertNotEqual(cleaned_data_with_black.get("definition", ""), "result.value=0")

    def test_clean_method_for_update_allowed_business_areas(self) -> None:
        # update only 'allowed_business_areas' field
        rule = RuleFactory(
            name="Rule_1", type=Rule.TYPE_TARGETING, language="python", flags={"individual_data_needed": False}
        )
        rule.refresh_from_db()
        self.assertEqual(rule.allowed_business_areas.all().count(), 0)

        form_data = {"allowed_business_areas": [self.business_area]}
        form = RuleForm(instance=rule, initial=form_data)

        # mock some responses to do nothing
        form.is_valid = lambda: True  # type: ignore
        form.full_clean = lambda: None  # type: ignore
        form.is_valid()
        form.full_clean()
        form.cleaned_data = form_data

        cleaned_data = form.clean()

        self.assertIn("allowed_business_areas", cleaned_data)

        # save and check if allowed_business_areas updated
        form.save()
        rule.refresh_from_db()
        self.assertEqual(rule.allowed_business_areas.all().count(), 1)
        self.assertEqual(rule.allowed_business_areas.all().first().slug, "afghanistan")
