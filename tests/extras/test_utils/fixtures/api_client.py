from typing import Any, Callable, Optional

import pytest
from extras.test_utils.factories.account import UserFactory
from rest_framework.test import APIClient

from hope.apps.account.models import User


class ReauthenticateAPIClient(APIClient):
    def reauthenticate_user(self) -> None:
        self.force_authenticate(user=User.objects.get(id=self.handler._force_user.id))

    def get(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().get(*args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().post(*args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().put(*args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().patch(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().delete(*args, **kwargs)

    def options(self, *args: Any, **kwargs: Any) -> Any:
        self.reauthenticate_user()
        return super().options(*args, **kwargs)


@pytest.fixture
def api_client() -> Callable:
    def _api_client(user_account: Optional[UserFactory] = None) -> ReauthenticateAPIClient:
        if not user_account:
            user_account = UserFactory()
        client = ReauthenticateAPIClient()
        client.force_authenticate(user=User.objects.get(id=user_account.id))
        return client

    return _api_client
