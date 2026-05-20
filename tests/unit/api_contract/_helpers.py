import json
import re

from drf_api_checker.recorder import Recorder
import drf_api_checker.utils as _checker_utils

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _assert_uuid(value, field, view):
    assert isinstance(value, str), f"{view}: `{field}` is not a valid UUID: {value!r}"
    assert UUID_RE.match(value), f"{view}: `{field}` is not a valid UUID: {value!r}"


class HopeRecorder(Recorder):
    """Recorder subclass shared by all api_contract tests.

    - Accepts an optional ``api_token`` (needed for HOPEAuthentication
      endpoints) and passes it to ``force_authenticate``.
    - Normalizes the live response through a JSON roundtrip so
      Python-typed values (UUID, Decimal ...) become plain
      strings/ints/floats before comparison with the stored baseline.
    - Skips Content-Length header check because body size can vary.
    - Time is frozen via conftest so all timestamps are deterministic.
    """

    headers = ["Content-Type", "Allow"]

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

    def assert_unicef_id(self, response, expected, path):
        pass

    def assert_payment_verification_plan_unicef_id(self, response, expected, path):
        pass


class JsonPostRecorder(HopeRecorder):
    """Recorder for POST endpoints that send JSON bodies."""

    @property
    def client(self):
        c = super().client
        c.default_format = "json"
        return c


class PostRecorder(HopeRecorder):
    """Recorder for POST endpoints where newly-created object IDs are non-deterministic."""

    @property
    def client(self):
        from rest_framework.test import APIClient

        client = APIClient()
        client.default_format = "multipart"
        if self.user:
            client.force_authenticate(user=self.user, token=self._api_token)
        return client

    def assert_id(self, response, expected, path):
        value = response["id"]
        if isinstance(expected["id"], str):
            _assert_uuid(value, "id", self.view)
        else:
            assert isinstance(value, int), f"{self.view}: `id` is not an int: {value!r}"

    def assert_import_data_id(self, response, expected, path):
        _assert_uuid(response["import_data_id"], "import_data_id", self.view)

    def assert_rdi_id(self, response, expected, path):
        _assert_uuid(response["rdi_id"], "rdi_id", self.view)

    def assert_file(self, response, expected, path):
        value = response["file"]
        assert isinstance(value, str), f"{self.view}: `file` is empty or not a string: {value!r}"
        assert value, f"{self.view}: `file` is empty or not a string: {value!r}"
