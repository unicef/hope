from functools import cached_property
import logging
import re
from typing import Any, Generator
from uuid import UUID

from constance import config
from django.conf import settings
from django.http import HttpRequest
import requests
from requests import Response

from hope.models import User

logger = logging.getLogger(__name__)


def get_valid_kobo_username(user: User) -> str:
    return user.username.replace("@", "_at_").replace(".", "_").replace("+", "_").lower()


KOBO_ACCESS_EMAIL = """

You have been authorised to access to HOPE/Kobo

Follow this link {kobo_url} and use below credentials:

Username:{email}
Password:{password}

The HOPE team.
"""


class DjAdminManager:
    regex = re.compile(r'class="errorlist"><li>(.*)(?=<\/li>)')

    class ResponseError(Exception):
        pass

    def __init__(self, kf_host: str = settings.KOBO_URL) -> None:
        self.admin_path = "/admin/"
        self.admin_url = f"{kf_host}{self.admin_path}"
        self.login_url = f"{self.admin_url}login/"

        self._logged = False
        self._last_error: Response | None = None
        self._last_response: Response | None = None
        self._username = None
        self._password = None
        self.form_errors = []

    def extract_errors(self, res: Response) -> list:
        self.form_errors = list(self.regex.findall(res.content.decode()))
        return self.form_errors

    def assert_response(
        self,
        status: int | list[int],
        location: str | None = None,
        custom_error: str = "",
    ) -> None:
        if not isinstance(status, list | tuple):
            status = [status]
        if self._last_response.status_code not in status:
            msg = f"Unexpected code:{self._last_response.status_code} not in {status}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseError(msg)

        if location and (redir_to := self._last_response.headers.get("location", "N/A")) != location:
            msg = f"Unexpected redirect:{redir_to} <> {location}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseError(msg)

    @cached_property
    def client(self) -> requests.Session:
        client = requests.Session()
        client.headers["Referer"] = self.admin_url
        client.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.77 Safari/537.36"
        )
        return client

    def logout(self, request: HttpRequest) -> None:
        self._username = request.session["kobo_username"] = None
        self._password = request.session["kobo_password"] = None

    def login(self, request: HttpRequest | None = None, twin: Any | None = None) -> None:
        try:
            username, password = config.KOBO_ADMIN_CREDENTIALS.split(":")
        except ValueError:
            raise ValueError("Invalid KOBO_ADMIN_CREDENTIALS")
        try:
            try:
                self._get(self.login_url)
                csrftoken = self.get_csrfmiddlewaretoken()
                self._post(
                    self.login_url,
                    {
                        "username": username,
                        "password": password,
                        "next": self.admin_url,
                        "csrfmiddlewaretoken": csrftoken,
                    },
                )
                self.assert_response(302, self.admin_url)
            except self.ResponseError as e:
                raise self.ResponseError(
                    f"Unable to login to Kobo at "
                    f"{self.login_url}: {e.__class__.__name__} {e}. "
                    f"Check KOBO_ADMIN_CREDENTIALS value"
                )

        except Exception as e:
            logger.warning(e)
            raise

    def _get(self, url: str) -> Any:
        self._last_response = self.client.get(url, allow_redirects=False)
        self.client.headers["Referer"] = url
        return self._last_response

    def _post(self, url: str, data: dict) -> Any:
        self._last_response = self.client.post(url, data, allow_redirects=False)
        return self._last_response

    def list_users(self, q: str = "") -> Generator:
        regex = re.compile(
            r'action-checkbox.*value="(?P<id>\d+)".*</td>.*field-username.*<a.*?>(?P<username>.*)</a></t.>.*field-email">(?P<mail>.*?)<',
            re.MULTILINE + re.IGNORECASE,
        )
        page = 1
        last_match = None
        while True:
            url = f"{self.admin_url}auth/user/?q={q}&p={page}"
            res = self._get(url)
            self.assert_response(200)
            matches = regex.findall(res.content.decode())
            if matches[0] == last_match:
                break
            last_match = matches[0]
            yield from matches

            page += 1

    def get_csrfmiddlewaretoken(self) -> Any:
        regex = re.compile("""csrfmiddlewaretoken["'] +value=["'](.*)["']""")
        try:
            m = regex.search(self._last_response.content.decode("utf8"))
            return m.groups()[0]
        except (AttributeError, IndexError):
            raise ValueError("Unable to get CSRF token from Kobo")

    def delete_user(self, username: str, pk: UUID) -> None:
        self.login()
        url = f"{self.admin_url}auth/user/{pk}/delete/"
        self._get(url)
        self.assert_response([200, 404, 302], custom_error=url)
        if self._last_response.status_code == 302 and "/login/" in self._last_response.headers["Location"]:
            raise Exception(f"Cannot access to {url}")

        if self._last_response.status_code == 200:
            csrftoken = self.get_csrfmiddlewaretoken()
            self._post(url, {"csrfmiddlewaretoken": csrftoken, "post": "yes"})
            self.assert_response(302, custom_error=f"{url} - {csrftoken}")
