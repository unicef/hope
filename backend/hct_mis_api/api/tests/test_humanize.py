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
HOUSEHOLD = {"country": "AF", "residence_status": "IDP", "size": 1, "members": [MEMBER]}


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

    def test_1(self):
        self.assertErrors(
            {},
            {
                "collect_individual_data": ["This field is required."],
                "households": ["This field is required."],
                "name": ["This field is required."],
            },
        )

    def test_2(self):
        data = {"households": [], "collect_individual_data": "N", "name": "Test1"}
        self.assertErrors(data, {"households": ["This field is required."]})

    def test_3(self):
        data = {"households": [{}], "collect_individual_data": "N", "name": "Test1"}
        self.assertErrors(
            data,
            {
                "households": [
                    {
                        "Household #1": [
                            {
                                "country": ["This field is required."],
                                "members": ["This field is required."],
                                "residence_status": ["This field is required."],
                                "size": ["This field is required."],
                            }
                        ]
                    }
                ]
            },
        )

    def test_4(self):
        data = {
            "households": [
                {"country": "AF", "residence_status": "IDP", "size": 1, "members": []},
            ],
            "collect_individual_data": "N",
            "name": "Test1",
        }
        self.assertErrors(data, {"households": [{"Household #1": [{"members": ["This field is required"]}]}]})

    def test_5(self):
        h1 = dict(**HOUSEHOLD)
        h1["members"] = [MEMBER, MEMBER]

        data = {"collect_individual_data": "N", "name": "Test1", "households": [h1]}
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

    def test_6(self):
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
