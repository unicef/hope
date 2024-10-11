from typing import Callable, Optional

import pytest
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory


@pytest.fixture()
def api_client() -> Callable:
    def _api_client(user_account: Optional[UserFactory] = None) -> APIClient:
        if not user_account:
            user_account = UserFactory()
        client = APIClient()
        client.force_authenticate(user_account)
        return client

    return _api_client
