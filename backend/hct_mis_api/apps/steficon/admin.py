import csv
import json
import logging
from io import StringIO

from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_urls.api import ExtraUrlMixin, button
from admin_extra_urls.utils import labelize
from adminfilters.autocomplete import AutoCompleteFilter
from smart_admin.mixins import LinkedObjectsMixin

from .forms import (
    RuleDownloadCSVFileProcessForm,
    RuleFileProcessForm,
    RuleForm,
    RuleTestForm,
)
from .models import MONITORED_FIELDS, Rule, RuleCommit
from .security import clean_context

logger = logging.getLogger(__name__)


@register(Rule)
class RuleAdmin(ExtraUrlMixin, LinkedObjectsMixin, ModelAdmin):
    list_display = ("name", "version", "language", "enabled", "deprecated", "created_by", "updated_by", "stable")
    list_filter = ("language", "enabled", "deprecated")
    search_fields = ("name",)
    form = RuleForm
    readonly_fields = (
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "version",
    )

    change_form_template = None
    fieldsets = [
        (
            None,
            {
                "fields": (
                    ("name", "version"),
                    ("enabled", "deprecated"),
                    ("description",),
                )
            },
        ),
        (
            "code",
            {
                "classes": ("collapse", "open"),
                "fields": (
                    "language",
                    "definition",
                ),
            },
        ),
        (
            "Data",
            {
                "classes": ("collapse",),
                "fields": (
                    ("created_by", "created_at"),
                    ("updated_by", "updated_at"),
                ),
            },
        ),
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        return super().get_form(request, obj, change, **kwargs)

    def stable(self, obj):
        try:
            url = reverse("admin:steficon_rulecommit_change", args=[obj.latest.pk])
            return mark_safe(f'<a href="{url}">{obj.latest.version}</a>')
        except (RuleCommit.DoesNotExist, AttributeError):
            pass

    @button(visible=lambda o, r: "/test/" not in r.path)
    def test(self, request, pk):
        context = self.get_common_context(
            request,
            pk,
            title="Test",
            state_opts=RuleCommit._meta,
        )
        if request.method == "POST":
            rule: Rule = self.get_object(request, pk)
            form = RuleTestForm(request.POST, request.FILES)
            if form.is_valid():
                selection = form.cleaned_data["opt"]
                if selection == "optFile":
                    data = form.cleaned_data.get("file")
                elif selection == "optData":
                    data = form.cleaned_data.get("raw_data")
                elif selection == "optContentType":
                    ct: ContentType = form.cleaned_data["content_type"]
                    filters = json.loads(form.cleaned_data.get("content_type_filters") or "{}")
                    qs = ct.model_class().objects.filter(**filters)
                    data = qs.all()
                else:
                    raise Exception("Invalid option")
                if not isinstance(data, (list, tuple, QuerySet)):
                    data = [data]
                results = []
                for values in data:
                    row = [values, None, True]
                    try:
                        entry = clean_context(values)
                        row[1] = rule.execute(entry, only_enabled=False, only_release=False)
                    except Exception as e:
                        row[1] = "%s: %s" % (e.__class__.__name__, str(e))
                        row[2] = False
                    results.append(row)
                context["results"] = results
            else:
                context["form"] = form
        else:
            context["form"] = RuleTestForm(initial={"raw_data": '{"a": 1, "b":2}', "opt": "optFile"})

        return TemplateResponse(request, "admin/steficon/rule/test.html", context)

    def _get_csv_config(self, form):
        return dict(
            quoting=int(form.cleaned_data["quoting"]),
            delimiter=form.cleaned_data["delimiter"],
            quotechar=form.cleaned_data["quotechar"],
            escapechar=form.cleaned_data["escapechar"],
        )

    @button(visible=lambda o, r: "/process_file/" not in r.path)
    def process_file(self, request, pk):
        context = self.get_common_context(
            request,
            pk,
            step=1,
            title="Process CSV file",
            state_opts=RuleCommit._meta,
        )
        if request.method == "POST":
            rule: Rule = self.get_object(request, pk)
            if request.POST["step"] == "1":
                form = RuleFileProcessForm(request.POST, request.FILES)
                if form.is_valid():
                    csv_config = self._get_csv_config(form)
                    f = request.FILES["file"]
                    input = f.read().decode("utf-8")
                    data = csv.DictReader(StringIO(input), fieldnames=None, **csv_config)
                    context["fields"] = data.fieldnames
                    for attr in form.cleaned_data["results"]:
                        context["fields"].append(labelize(attr))
                    info_col = labelize(form.cleaned_data["results"][0])
                    results = []
                    for entry in data:
                        try:
                            result = rule.execute(entry, only_enabled=False, only_release=False)
                            for attr in form.cleaned_data["results"]:
                                entry[labelize(attr)] = getattr(result, attr, "<ATTR NOT FOUND>")
                        except Exception as e:
                            entry[info_col] = str(e)
                        results.append(entry)
                    context["results"] = results
                    context["step"] = 2
                    context["form"] = RuleDownloadCSVFileProcessForm(
                        initial={
                            "quoting": csv_config["quoting"],
                            "delimiter": csv_config["delimiter"],
                            "quotechar": csv_config["quotechar"],
                            "escapechar": csv_config["escapechar"],
                            "data": json.dumps(results),
                            "fields": ",".join(context["fields"]),
                            "filename": f.name,
                        }
                    )
                else:
                    context["form"] = form

            elif request.POST["step"] == "2":
                form = RuleDownloadCSVFileProcessForm(request.POST)
                if form.is_valid():
                    try:
                        csv_config = self._get_csv_config(form)
                        data = form.cleaned_data["data"]
                        fields = form.cleaned_data["fields"]
                        response = HttpResponse(
                            content_type="text/csv",
                            headers={
                                "Content-Disposition": 'attachment; filename="%s"' % form.cleaned_data["filename"]
                            },
                        )

                        writer = csv.DictWriter(response, fieldnames=fields, **csv_config)
                        writer.writeheader()
                        writer.writerows(data)
                        return response
                    except Exception:
                        raise
                else:
                    context["form"] = form
        else:
            context["form"] = RuleFileProcessForm(initial={"results": "value"})

        return TemplateResponse(request, "admin/steficon/rule/file_process.html", context)

    @button(visible=lambda o, r: "/changelog/" not in r.path)
    def changelog(self, request, pk):
        context = self.get_common_context(request, pk, title="Changelog", state_opts=RuleCommit._meta)
        return TemplateResponse(request, "admin/steficon/rule/changelog.html", context)

    @button(urls=[r"^aaa/(?P<pk>.*)/(?P<state>.*)/$", r"^bbb/(?P<pk>.*)/$"])
    def revert(self, request, pk, state=None):
        try:
            context = self.get_common_context(
                request,
                pk,
                action="Revert",
                MONITORED_FIELDS=MONITORED_FIELDS,
            )
            state = self.object.history.get(pk=state)
            if request.method == "GET":
                context["state"] = state
                return TemplateResponse(request, "admin/steficon/rule/revert.html", context)
            else:
                with atomic():
                    if "_restore" in request.POST:
                        state.revert()
                    else:
                        state.revert(["definition"])
                url = reverse("admin:steficon_rule_change", args=[self.object.id])
                return HttpResponseRedirect(url)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

    @button(visible=lambda o, r: "/diff/" not in r.path)
    def diff(self, request, pk):
        try:
            context = self.get_common_context(request, pk, action="Code history")
            state_pk = request.GET.get("state_pk")
            if state_pk:
                state = self.object.history.get(pk=state_pk)
            else:
                state = self.object.history.first()

            try:
                context["prev"] = state.get_previous_by_timestamp()
            except (RuleCommit.DoesNotExist, AttributeError):
                context["prev"] = None

            try:
                context["next"] = state.get_next_by_timestamp()
            except (RuleCommit.DoesNotExist, AttributeError):
                context["next"] = None

            context["state"] = state
            context["title"] = (
                f"Change #{state.version} on " f"{state.timestamp.strftime('%d, %b %Y at %H:%M')} by {state.updated_by}"
            )
            return TemplateResponse(request, "admin/steficon/rule/diff.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

    @atomic()
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)


@register(RuleCommit)
class RuleCommitAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = (
        "timestamp",
        "rule",
        "version",
        "updated_by",
        "affected_fields",
        "is_release",
    )
    list_filter = (
        ("rule", AutoCompleteFilter),
        "is_release",
    )
    search_fields = ("name",)
    readonly_fields = ("updated_by", "rule", "affected_fields", "version")
    change_form_template = None
