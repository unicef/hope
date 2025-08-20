from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.steficon import RuleFactory

from hope.apps.core.base_test_case import APITestCase
from hope.apps.steficon.forms import RuleForm
from hope.apps.steficon.models import Rule


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
        assert form.is_valid()

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
            assert form_with_black.is_valid()
            cleaned_data_with_black = form_with_black.clean()
            assert cleaned_data_with_black.get("definition", "") != "result.value=0"

    def test_clean_method_for_update_allowed_business_areas(self) -> None:
        # update only 'allowed_business_areas' field
        rule = RuleFactory(
            name="Rule_1",
            type=Rule.TYPE_TARGETING,
            language="python",
            flags={"individual_data_needed": False},
        )
        rule.refresh_from_db()
        assert rule.allowed_business_areas.all().count() == 0

        form_data = {"allowed_business_areas": [self.business_area]}
        form = RuleForm(instance=rule, initial=form_data)

        # mock some responses to do nothing
        form.is_valid = lambda: True  # type: ignore
        form.full_clean = lambda: None  # type: ignore
        form.is_valid()
        form.full_clean()
        form.cleaned_data = form_data

        cleaned_data = form.clean()

        assert "allowed_business_areas" in cleaned_data

        # save and check if allowed_business_areas updated
        form.save()
        rule.refresh_from_db()
        assert rule.allowed_business_areas.all().count() == 1
        assert rule.allowed_business_areas.all().first().slug == "afghanistan"
