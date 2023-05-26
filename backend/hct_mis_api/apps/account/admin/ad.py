import logging
from collections import namedtuple
from typing import Any

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.forms import Form
from django.http import Http404, HttpRequest
from django.template.response import TemplateResponse

from admin_extra_buttons.decorators import button
from requests import HTTPError

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import build_arg_dict_from_dict
from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.microsoft_graph import DJANGO_USER_MAP, MicrosoftGraphAPI
from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea, help_text="Emails must be space separated")
    role = forms.ModelChoiceField(queryset=account_models.Role.objects.all())
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    enable_kobo = forms.BooleanField(required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_emails(self) -> dict:
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            raise ValidationError("Invalid emails {}".format(", ".join(errors)))
        return self.cleaned_data["emails"]


class ADUSerMixin:
    ad_form_class = LoadUsersForm
    Results = namedtuple("Results", "created,missing,updated,errors")

    def _get_ad_form(self, request: HttpRequest) -> Form:
        if request.method == "POST":
            return self.ad_form_class(request.POST, request=request)
        else:
            return self.ad_form_class(request=request)

    def _sync_ad_data(self, user: User) -> None:
        ms_graph = MicrosoftGraphAPI()
        if user.ad_uuid:
            filters = [{"uuid": user.ad_uuid}, {"email": user.email}]
        else:
            filters = [{"email": user.email}]

        for _filter in filters:
            try:
                user_data = ms_graph.get_user_data(**_filter)
                user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                for field, value in user_args.items():
                    setattr(user, field, value or "")
                user.save()
                break
            except Http404:
                pass
        else:
            raise Http404

    @button(label="AD Sync", permission="account.can_sync_with_ad")
    def sync_multi(self, request: HttpRequest) -> None:
        not_found = []
        try:
            for user in self.get_queryset(request):
                try:
                    self._sync_ad_data(user)
                except Http404:
                    not_found.append(str(user))
            if not_found:
                self.message_user(
                    request,
                    f"These users were not found: {', '.join(not_found)}",
                    messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    "Active Directory data successfully fetched",
                    messages.SUCCESS,
                )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Sync", permission="account.can_sync_with_ad")
    def sync_single(self, request: HttpRequest, pk: int) -> None:
        try:
            self._sync_ad_data(self.get_object(request, pk))
            self.message_user(request, "Active Directory data successfully fetched", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(permission="account.can_load_from_ad")
    def load_ad_users(self, request: HttpRequest) -> TemplateResponse:
        ctx = self.get_common_context(
            request,
            None,
            **{
                "change": True,
                "is_popup": False,
                "save_as": False,
                "has_delete_permission": False,
                "has_add_permission": False,
                "has_change_permission": True,
            },
        )
        form = self._get_ad_form(request)
        if request.method == "POST":
            if form.is_valid():
                emails = set(form.cleaned_data["emails"].split())
                role = form.cleaned_data["role"]
                business_area = form.cleaned_data["business_area"]
                users_to_bulk_create = []
                users_role_to_bulk_create = []
                existing = set(account_models.User.objects.filter(email__in=emails).values_list("email", flat=True))
                results = self.Results([], [], [], [])
                try:
                    ms_graph = MicrosoftGraphAPI()
                    for email in emails:
                        try:
                            if email in existing:
                                user = account_models.User.objects.get(email=email)
                                self._sync_ad_data(user)
                                results.updated.append(user)
                            else:
                                user_data = ms_graph.get_user_data(email=email)
                                user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                                user = account_models.User(**user_args)
                                if user.first_name is None:
                                    user.first_name = ""
                                if user.last_name is None:
                                    user.last_name = ""
                                job_title = user_data.get("jobTitle")
                                if job_title is not None:
                                    user.job_title = job_title
                                user.set_unusable_password()
                                users_to_bulk_create.append(user)
                                global_business_area = BusinessArea.objects.filter(slug="global").first()
                                basic_role = account_models.Role.objects.filter(name="Basic User").first()
                                if global_business_area and basic_role:
                                    users_role_to_bulk_create.append(
                                        account_models.UserRole(
                                            business_area=global_business_area,
                                            user=user,
                                            role=basic_role,
                                        )
                                    )
                                results.created.append(user)

                            users_role_to_bulk_create.append(
                                account_models.UserRole(role=role, business_area=business_area, user=user)
                            )
                        except HTTPError as e:
                            if e.response.status_code != 404:
                                raise
                            results.missing.append(email)
                        except Http404:
                            results.missing.append(email)
                    account_models.User.objects.bulk_create(users_to_bulk_create)
                    account_models.UserRole.objects.bulk_create(users_role_to_bulk_create, ignore_conflicts=True)
                    ctx["results"] = results
                    return TemplateResponse(request, "admin/load_users.html", ctx)
                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), messages.ERROR)
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)
