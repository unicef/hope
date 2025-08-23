import json
from typing import Dict
from unittest import TestCase
from unittest.mock import Mock

import pytest
from django.http import JsonResponse

from hope.api.endpoints.rdi.upload import RDINestedSerializer
from hope.api.utils import humanize_errors

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
    "members": [MEMBER],
}


@pytest.mark.django_db
class ValidatorTest(TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = RDINestedSerializer

    def _run(self, data: Dict) -> Dict:
        serializer = self.validator(data=data, business_area=Mock(slug="afghanistan"))
        serializer.is_valid()
        return humanize_errors(json.loads(JsonResponse(serializer.errors).content))

    def assert_errors(self, post_data: Dict, expected: Dict) -> None:
        res = self._run(post_data)
        assert res == expected

    def test_empty_post(self) -> None:
        self.assert_errors(
            {},
            {
                "households": ["This field is required."],
                "name": ["This field is required."],
                "program": ["This field is required."],
            },
        )

    def test_empty_households(self) -> None:
        data = {"households": [], "name": "Test1"}
        self.assert_errors(
            data,
            {
                "households": ["This field is required."],
                "program": ["This field is required."],
            },
        )

    def test_empty_household_value(self) -> None:
        data = {"households": [{}], "name": "Test1"}
        self.assert_errors(
            data,
            {
                "households": [
                    {
                        "Household #1": [
                            {
                                "country": ["This field is required."],
                                "members": ["This field is required."],
                            }
                        ]
                    }
                ],
                "program": ["This field is required."],
            },
        )

    def test_empty_members(self) -> None:
        data = {
            "households": [
                {"country": "AF", "residence_status": "IDP", "size": 1, "members": []},
            ],
            "name": "Test1",
        }
        self.assert_errors(
            data,
            {
                "households": [{"Household #1": [{"members": ["This field is required"]}]}],
                "program": ["This field is required."],
            },
        )

    def test_double_entries(self) -> None:
        h1 = dict(**HOUSEHOLD)
        h1["members"] = [MEMBER, MEMBER]

        data = {"name": "Test1", "households": [h1]}
        self.assert_errors(
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
                ],
                "program": ["This field is required."],
            },
        )

    def test_double_entry_multiple_hh(self) -> None:
        h1 = dict(**HOUSEHOLD)
        h1["members"] = [MEMBER, MEMBER]
        data = {"name": "Test1", "households": [HOUSEHOLD, HOUSEHOLD, h1]}
        self.assert_errors(
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
                ],
                "program": ["This field is required."],
            },
        )
