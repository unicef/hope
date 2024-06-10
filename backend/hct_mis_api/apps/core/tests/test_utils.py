from django.contrib.admin.views.main import ChangeList
from django.test import RequestFactory, TestCase

from hct_mis_api.apps.core.utils import AutoCompleteFilterTemp, get_count_and_percentage
from hct_mis_api.apps.targeting.admin import HouseholdSelectionAdmin
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestCoreUtils(TestCase):
    def test_get_count_and_percentage(self) -> None:
        self.assertEqual(get_count_and_percentage(1), {"count": 1, "percentage": 100.0})
        self.assertEqual(get_count_and_percentage(0), {"count": 0, "percentage": 0.0})
        self.assertEqual(get_count_and_percentage(5, 1), {"count": 5, "percentage": 500.0})
        self.assertEqual(get_count_and_percentage(20, 20), {"count": 20, "percentage": 100.0})
        self.assertEqual(get_count_and_percentage(5, 25), {"count": 5, "percentage": 20.0})


# temporary added test for AutoCompleteFilterTemp
class AutoCompleteFilterTempTest(TestCase):
    def setUp(self) -> None:
        targeting = TargetPopulationFactory(name="Test TP for test", is_removed=True)
        self.factory = RequestFactory()
        self.model_instance = targeting
        self.filter = AutoCompleteFilterTemp(
            field=TargetPopulation._meta.get_field("name"),
            request=self.factory.get("/"),
            params={},
            model=TargetPopulation,
            model_admin=HouseholdSelectionAdmin,
            field_path="name",
        )

    def test_choices_method(self) -> None:
        changelist = ChangeList(
            self.factory.get("/"),
            self.filter.model,
            list_display=[],
            list_display_links=[],
            list_filter=[],
            date_hierarchy=None,
            search_fields=[],
            list_select_related=False,
            list_per_page=10,
            list_max_show_all=10,
            list_editable=[],
            model_admin=None,  # type: ignore
            sortable_by=["id"],
        )
        self.filter.lookup_val = "name"
        choices = self.filter.choices(changelist)
        self.assertEqual(choices, [str(self.model_instance)])

        changelist = ChangeList(
            self.factory.get("/"),
            self.filter.model,
            list_display=[],
            list_display_links=[],
            list_filter=[],
            date_hierarchy=None,
            search_fields=[],
            list_select_related=False,
            list_per_page=100,
            list_max_show_all=200,
            list_editable=[],
            model_admin=None,  # type: ignore
            sortable_by=["id"],
        )
        self.filter.lookup_val = ""
        choices = self.filter.choices(changelist)
        self.assertEqual(choices, [])
