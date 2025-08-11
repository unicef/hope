import json
import logging
from typing import Any, Collection
from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import get_language

from admin_extra_buttons.api import button

from hope.apps.payment.models import PaymentPlan
from hope.apps.steficon.forms import (
    RuleTestForm,
)
from hope.apps.steficon.models import Rule, RuleCommit


logger = logging.getLogger(__name__)


class AutocompleteWidget(forms.Widget):
    template_name = "steficon/widgets/autocomplete.html"

    def __init__(
        self,
        model: type,
        admin_site: str,
        attrs: Collection[Any] | None = None,
        choices: tuple = (),
        using: Any | None = None,
        pk_field: str = "id",
        business_area: UUID | None = None,
    ) -> None:
        self.model = model
        self.pk_field = pk_field
        self.admin_site = admin_site
        self.db = using
        self.choices = choices
        self.attrs = {} if attrs is None else attrs.copy()
        self.business_area = business_area

    class Media:
        extra = "" if settings.DEBUG else ".min"
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file: list = [f"admin/js/vendor/select2/i18n/{i18n_name}.js"] if i18n_name else []
        js = tuple(
            [
                f"admin/js/vendor/jquery/jquery{extra}.js",
                f"admin/js/vendor/select2/select2.full{extra}.js",
            ]
            + i18n_file
            + [
                "admin/js/jquery.init.js",
                "admin/js/autocomplete.js",
                f"adminfilters/adminfilters{extra}.js",
            ]
        )
        css = {
            "screen": [
                f"admin/css/vendor/select2/select2{extra}.css",
                "adminfilters/adminfilters.css",
            ]
        }

    def get_url(self) -> str:
        url = reverse("admin:autocomplete")
        if self.business_area:
            url += f"?business_area={self.business_area}"
        return url

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict:
        return {
            "widget": {
                "query_string": f"business_area__exact={self.business_area}" if self.business_area else "",
                "lookup_kwarg": "term",
                "url": self.get_url(),
                "target_opts": {
                    "app_label": self.model._meta.app_label,
                    "model_name": self.model._meta.model_name,
                    "target_field": self.pk_field,
                },
                "name": name,
                "media": self.media,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            }
        }


class TestRuleMixin:
    @button(permission="steficon.view_rule")
    def test(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        rule: Rule = self.get_object(request, str(pk))
        context = self.get_common_context(
            request,
            pk,
            title=f"{rule}",
            state_opts=RuleCommit._meta,
        )

        if request.method == "POST":
            form = RuleTestForm(request.POST, request.FILES)
            if form.is_valid():
                selection = form.cleaned_data["opt"]
                if selection == "optFile":
                    data = form.cleaned_data.get("file")
                    title = f"Test result for '{rule}' using file"
                elif selection == "optData":
                    data = form.cleaned_data.get("raw_data")
                    title = f"Test result for '{rule}' using sample data"
                elif selection == "optTargetPopulation":
                    tp = form.cleaned_data.get("target_population")
                    context["target_population"] = tp
                    data = [{"household": e.household} for e in tp.payment_items.all()]
                    title = f"Test result for '{rule}' using TargetPopulation '{tp}'"
                elif selection == "optContentType":
                    ct: ContentType = form.cleaned_data["content_type"]
                    filters = json.loads(form.cleaned_data.get("content_type_filters") or "{}")
                    qs = ct.model_class().objects.filter(**filters)
                    data = qs.all()
                    title = f"Test result for '{rule}' using ContentType '{ct}'"
                else:
                    raise Exception(f"Invalid option '{selection}'")
                if not isinstance(data, list | tuple | QuerySet):
                    data = [data]
                context["title"] = title
                context["selection"] = selection
                results = []
                for values in data:
                    row = {
                        "input": values,
                        "input_type": values.__class__.__name__,
                        "data": "",
                        "error": None,
                        "success": True,
                        "result": None,
                    }
                    try:
                        if isinstance(rule, Rule):
                            row["result"] = rule.interpreter.execute({"data": values})
                        else:
                            row["result"] = rule.execute({"data": values})
                    except Exception as e:
                        row["error"] = f"{e.__class__.__name__}: {str(e)}"
                        row["success"] = False
                    results.append(row)
                context["results"] = results
            else:
                context["form"] = form
        else:
            context["form"] = RuleTestForm(initial={"raw_data": '{"a": 1, "b":2}', "opt": "optData"})
        if "form" in context:
            context["form"].fields["target_population"].widget = AutocompleteWidget(PaymentPlan, self.admin_site)
            context["form"].fields["content_type"].widget = AutocompleteWidget(ContentType, self.admin_site)
        return TemplateResponse(request, "admin/steficon/rule/test.html", context)
