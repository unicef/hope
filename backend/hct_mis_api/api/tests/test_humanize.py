import json
from unittest import TestCase
from unittest.mock import Mock

from django.http import JsonResponse

from hct_mis_api.api.endpoints.upload import RDINestedSerializer
from hct_mis_api.api.utils import humanize_errors

MEMBER = {
    "birth_date": "2000-01-01",
    "full_name": "Full Name",
    "residence_status": "IDP",
    "role": "PRIMARY",
    "sex": "MALE",
    "relationship": "HEAD",
}
HOUSEHOLD = {
    "country": "AF",
    "residence_status": "IDP",
    "size": 1,
    "collect_individual_data": "FULL",
    "members": [MEMBER],
}


class ValidatorTest(TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = RDINestedSerializer

    def _run(self, data):
        serializer = self.validator(data=data, business_area=Mock(slug="afghanistan"))
        serializer.is_valid()
        r = JsonResponse(serializer.errors)
        return humanize_errors(json.loads(r.content))

    def assertErrors(self, post_data, expected):
        res = self._run(post_data)
        self.assertDictEqual(res, expected)

    def test_empty_post(self):
        self.assertErrors(
            {},
            {
                "households": ["This field is required."],
                "name": ["This field is required."],
            },
        )

    def test_empty_households(self):
        data = {"households": [], "name": "Test1"}
        self.assertErrors(data, {"households": ["This field is required."]})

    def test_empty_household_value(self):
        data = {"households": [{}], "name": "Test1"}
        self.assertErrors(
            data,
            {
                "households": [
                    {
                        "Household #1": [
                            {
                                "collect_individual_data": ["This field is required."],
                                "country": ["This field is required."],
                                "members": ["This field is required."],
                                "residence_status": ["This field is required."],
                                # "size": ["This field is required."],
                            }
                        ]
                    }
                ]
            },
        )

    def test_empty_members(self):
        data = {
            "households": [
                {"country": "AF", "collect_individual_data": "N", "residence_status": "IDP", "size": 1, "members": []},
            ],
            "name": "Test1",
        }
        self.assertErrors(data, {"households": [{"Household #1": [{"members": ["This field is required"]}]}]})

    def test_double_entries(self):
        h1 = dict(**HOUSEHOLD)
        h1["members"] = [MEMBER, MEMBER]

        data = {"name": "Test1", "households": [h1]}
        self.assertErrors(
            data,
            {
                "households": [
                    {
                        "Household #1": [
                            {
                                "head_of_household": ["Only one HoH allowed"],
                                "primary_collector": ["Only one Primary Collector allowed"],
                            },
                        ]
                    }
                ]
            },
        )

    def test_double_entry_multiple_hh(self):
        h1 = dict(**HOUSEHOLD)
        h1["members"] = [MEMBER, MEMBER]
        data = {"collect_individual_data": "N", "name": "Test1", "households": [HOUSEHOLD, HOUSEHOLD, h1]}
        self.assertErrors(
            data,
            {
                "households": [
                    {
                        "Household #3": [
                            {
                                "head_of_household": ["Only one HoH allowed"],
                                "primary_collector": ["Only one Primary Collector allowed"],
                            },
                        ]
                    }
                ]
            },
        )
