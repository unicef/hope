import logging
import re
from functools import cached_property
from typing import Any, Dict, Generator, List, Optional, Union
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.utils import unquote
from django.core.mail import send_mail
from django.db import router, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.crypto import get_random_string

import requests
from admin_extra_buttons.decorators import button
from constance import config
from requests import Response

from hct_mis_api.apps.account.models import User

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

    class ResponseException(Exception):
        pass

    def __init__(self, kf_host: str = settings.KOBO_KF_URL, kc_host: str = settings.KOBO_KC_URL) -> None:
        self.admin_path = "/admin/"
        self.admin_url = f"{kf_host}{self.admin_path}"
        self.login_url = f"{self.admin_url}login/"

        self.admin_url_kc = f"{kc_host}{self.admin_path}"
        self.login_url_kc = f"{self.admin_url_kc}login/"
        self._logged = False
        self._last_error: Optional[Response] = None
        self._last_response: Optional[Response] = None
        self._username = None
        self._password = None
        self.form_errors = []

    def extract_errors(self, res: Response) -> List:
        self.form_errors = [msg for msg in self.regex.findall(res.content.decode())]
        return self.form_errors

    def assert_response(
        self, status: Union[int, List[int]], location: Optional[str] = None, custom_error: str = ""
    ) -> None:
        if not isinstance(status, (list, tuple)):
            status = [status]
        if self._last_response.status_code not in status:
            msg = f"Unexpected code:{self._last_response.status_code} not in {status}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseException(msg)

        if location and (redir_to := self._last_response.headers.get("location", "N/A")) != location:
            msg = f"Unexpected redirect:{redir_to} <> {location}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseException(msg)

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

    def login(self, request: Optional[HttpRequest] = None, twin: Optional[Any] = None) -> None:
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
            except Exception as e:
                raise self.ResponseException(
                    f"Unable to login to Kobo at "
                    f"{self.login_url}: {e.__class__.__name__} {e}. "
                    f"Check KOBO_ADMIN_CREDENTIALS value"
                )

        except Exception as e:
            logger.exception(e)
            raise

    def _get(self, url: str) -> Any:
        self._last_response = self.client.get(url, allow_redirects=False)
        self.client.headers["Referer"] = url
        return self._last_response

    def _post(self, url: str, data: Dict) -> Any:
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
        except Exception:
            raise ValueError("Unable to get CSRF token from Kobo")

    def delete_user(self, username: str, pk: UUID) -> None:
        self.login()
        for url in (f"{self.admin_url_kc}auth/user/{pk}/delete/", f"{self.admin_url}auth/user/{pk}/delete/"):
            self._get(url)
            self.assert_response([200, 404, 302], custom_error=url)
            if self._last_response.status_code == 302 and "/login/" in self._last_response.headers["Location"]:
                raise Exception(f"Cannot access to {url}")

            if self._last_response.status_code == 200:
                # csrftoken = self.client.cookies.get_dict()['csrftoken']
                csrftoken = self.get_csrfmiddlewaretoken()
                self._post(url, {"csrfmiddlewaretoken": csrftoken, "post": "yes"})
                self.assert_response(302, custom_error=f"{url} - {csrftoken}")


class KoboAccessMixin:
    def _grant_kobo_accesss_to_user(self, user: User, notify: bool = True, sync: bool = True) -> None:
        password = get_random_string(length=12)
        url = f"{settings.KOBO_KF_URL}/authorized_application/users/"
        username = get_valid_kobo_username(user)
        res = requests.post(
            url,
            headers={"Authorization": f"Token {config.KOBO_APP_API_TOKEN}"},
            json={
                "username": username,
                "email": user.email,
                "password": password,
                "last_name": user.last_name,
                "first_name": user.first_name,
            },
        )
        if res.status_code != 201:
            raise Exception(res.content)
        if res.status_code == 400:
            raise Exception(res.content)

        if sync:
            api = DjAdminManager()
            api.login()
            for entry in api.list_users(q=username):
                if entry[1] == username and entry[2] == user.email:
                    user.custom_fields["kobo_pk"] = entry[0]
                    user.custom_fields["kobo_username"] = entry[1]
                    user.save()
        if res.status_code == 201 and notify:
            send_mail(
                "Kobo credentials",
                KOBO_ACCESS_EMAIL.format(email=user.email, password=password, kobo_url=settings.KOBO_KF_URL),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        user.custom_fields["kobo_username"] = user.username
        user.save()

    def create_kobo_user_qs(self, request: HttpRequest, queryset: QuerySet) -> None:
        for user in queryset.all():
            try:
                self._grant_kobo_accesss_to_user(user)
            except Exception as e:
                logger.exception(e)
                self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
        self.message_user(
            request,
            f"User successfully `{user.username}` created on Kobo",
            messages.SUCCESS,
        )

    @button(
        permission="account.can_create_kobo_user",
        enabled=lambda b: not b.original.custom_fields.get("kobo_username"),
    )
    def create_kobo_user(self, request: HttpRequest, pk: "UUID") -> None:
        try:
            self._grant_kobo_accesss_to_user(self.get_queryset(request).get(pk=pk))
            self.message_user(request, f"Granted access to {settings.KOBO_KF_URL}", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)

    def delete_view(self, request: HttpRequest, object_id: str, extra_context: Optional[Dict] = None) -> HttpResponse:
        if request.POST:  # The user has confirmed the deletion.
            with transaction.atomic(using=router.db_for_write(self.model)):
                res = self._delete_view(request, object_id, extra_context)
        else:
            if not (obj := self.get_object(request, unquote(object_id))):
                raise Exception("Object not found")
            kobo_pk = obj.custom_fields.get("kobo_pk", None)
            extra_context = extra_context or {}
            try:
                api = DjAdminManager()
                api.login(request)
                extra_context["kobo_pk"] = kobo_pk
                self.message_user(
                    request,
                    "This action will also delete linked Kobo account",
                    messages.WARNING,
                )
            except Exception as e:
                extra_context["kobo_failed"] = True
                self.message_user(request, str(e), messages.ERROR)
            res = super().delete_view(request, object_id, extra_context)

        return res

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        try:
            if "kobo_username" in obj.custom_fields:
                api = DjAdminManager()
                api.login(request)
                api.delete_user(obj.custom_fields["kobo_username"], obj.custom_fields["kobo_pk"])
            super().delete_model(request, obj)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
            raise

    @button(
        permission="account.can_create_kobo_user",
        enabled=lambda b: not b.custom_fields.get("kobo_username"),
    )
    def remove_kobo_access(self, request: HttpRequest, pk: "UUID") -> None:
        try:
            obj = self.get_object(request, pk)
            api = DjAdminManager()
            api.delete_user(obj.custom_fields["kobo_username"], obj.custom_fields["kobo_pk"])
            obj.custom_fields["kobo_username"] = None
            obj.custom_fields["kobo_pk"] = None
            obj.save()
            self.message_user(
                request,
                f"Kobo Access removed from {settings.KOBO_KF_URL}",
                messages.WARNING,
            )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)

    @button(label="Sync users from Kobo", permission="account.can_import_from_kobo")
    def kobo_users_sync(self, request: HttpRequest) -> TemplateResponse:
        ctx = self.get_common_context(request)
        users = []
        if request.method == "POST":
            selected = request.POST.getlist("kobo_id")
            api = DjAdminManager()
            api.login(request)
            results = []
            for entry in api.list_users():
                if entry[0] in selected:
                    local, created = User.objects.get_or_create(
                        email=entry[2],
                        defaults={
                            "username": entry[1],
                            "custom_fields": {
                                "kobo_pk": entry[0],
                                "kobo_username": entry[1],
                            },
                        },
                    )
                    local.custom_fields["kobo_pk"] = entry[0]
                    local.custom_fields["kobo_username"] = entry[1]
                    local.save()
                    results.append([local, created])
            ctx["results"] = results
        else:
            try:
                api = DjAdminManager()
                api.login(request)
                for entry in api.list_users():
                    local = User.objects.filter(email=entry[2]).first()
                    if entry[1] not in ["__sys__", "superuser"]:
                        users.append([entry[0], entry[1], entry[2], local])
                ctx["users"] = users

            except Exception as e:
                logger.exception(e)
                self.message_user(request, str(e), messages.ERROR)
        return TemplateResponse(request, "admin/kobo_users.html", ctx)
