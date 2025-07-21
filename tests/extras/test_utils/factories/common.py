import base64
from typing import Callable

import pytest

from tests.extras.test_utils.factories.account import BusinessAreaFactory


@pytest.fixture()
def afghanistan() -> BusinessAreaFactory:
    return BusinessAreaFactory(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "kobo_token": "XXX",
            "active": True,
        },
    )


@pytest.fixture()
def id_to_base64() -> Callable:
    def _id_to_base64(object_id: str, name: str) -> str:
        return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()

    return _id_to_base64
