import json

from drf_api_checker.recorder import Recorder
import drf_api_checker.utils as _checker_utils


class HopeRecorder(Recorder):
    """Recorder subclass shared by all api_contract tests.

    - Accepts an optional ``api_token`` (needed for HOPEAuthentication
      endpoints) and passes it to ``force_authenticate``.
    - Normalizes the live response through a JSON roundtrip so
      Python-typed values (UUID, Decimal ...) become plain
      strings/ints/floats before comparison with the stored baseline.
    - Skips ``created_at`` / ``updated_at`` dynamic-field assertions.
    """

    def __init__(self, *args, api_token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_token = api_token

    @property
    def client(self):
        from rest_framework.test import APIClient

        client = APIClient()
        if self.user:
            client.force_authenticate(user=self.user, token=self._api_token)
        return client

    def compare(self, response, expected, filename, view=None):
        normalized = json.loads(json.dumps(response, cls=_checker_utils.ResponseEncoder))
        super().compare(normalized, expected, filename, view=view)

    def assert_created_at(self, response, expected, path):
        pass

    def assert_updated_at(self, response, expected, path):
        pass

    def assert_unicef_id(self, response, expected, path):
        pass
