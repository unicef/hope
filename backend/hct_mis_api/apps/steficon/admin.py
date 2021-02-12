from admin_extra_urls.api import ExtraUrlMixin, action
from adminfilters.filters import TextFieldFilter
from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from hct_mis_api.apps.utils.admin import SmartFieldsetMixin
from hct_mis_api.apps.steficon.forms import RuleForm
from hct_mis_api.apps.steficon.models import Rule, RuleCommit, MONITORED_FIELDS
from hct_mis_api.apps.targeting.models import TargetPopulation


class RuleTestForm(forms.Form):
    target_population = forms.ModelChoiceField(
        queryset=TargetPopulation.objects.filter(status=TargetPopulation.STATUS_DRAFT)
    )


@register(Rule)
class RuleAdmin(ExtraUrlMixin, SmartFieldsetMixin, ModelAdmin):
    list_display = ("name", "version", "language", "enabled", "deprecated", "created_by", "updated_by")
    list_filter = ("language", "enabled", "deprecated")
    search_fields = ("name",)
    form = RuleForm

    readonly_fields = ("updated_by", "created_by", "version")
    change_form_template = None
    fieldsets = [
        (
            None,
            {
                "fields": (
                    ("name", "version"),
                    ("enabled", "deprecated"),
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
        ("Others", {"classes": ("collapse",), "fields": ("__all__",)}),
    ]

    @action()
    def used_by(self, request, pk):
        context = self.get_common_context(request, pk, title="Used By")
        if request.method == "GET":
            context["form"] = RuleTestForm()
            return TemplateResponse(request, "admin/steficon/rule/used_by.html", context)

    @action()
    def changelog(self, request, pk):
        context = self.get_common_context(request, pk, title="Changelog", state_opts=RuleCommit._meta)
        return TemplateResponse(request, "admin/steficon/rule/changelog.html", context)

    @action(urls=[r"^aaa/(?P<pk>.*)/(?P<state>.*)/$", r"^bbb/(?P<pk>.*)/$"])
    def revert(self, request, pk, state=None):
        context = self.get_common_context(
            request,
            pk,
            # title="Revert",
            action="Revert",
            MONITORED_FIELDS=MONITORED_FIELDS,
        )
        state = self.object.history.get(pk=state)
        if request.method == "GET":
            context["state"] = state
            return TemplateResponse(request, "admin/steficon/rule/revert.html", context)
        else:
            if "_restore" in request.POST:
                state.revert()
            else:
                state.revert(["definition"])
            url = reverse("admin:steficon_rule_change", args=[self.object.id])
            return HttpResponseRedirect(url)

    @action()
    def diff(self, request, pk):
        context = self.get_common_context(request, pk, action="Code history")
        state_pk = request.GET.get("state_pk")
        if state_pk:
            state = self.object.history.get(pk=state_pk)
        else:
            state = self.object.history.first()
        try:
            context["prev"] = state.get_previous_by_timestamp()
        except RuleCommit.DoesNotExist:
            context["prev"] = None

        try:
            context["next"] = state.get_next_by_timestamp()
        except RuleCommit.DoesNotExist:
            context["next"] = None

        context["state"] = state
        # context["action"] = "Code history"
        context["title"] = (
            f"Change #{state.id} on " f"{state.timestamp.strftime('%d, %b %Y at %H:%M')} by {state.updated_by}"
        )

        return TemplateResponse(request, "admin/steficon/rule/diff.html", context)

    @action(label="Test")
    def preview(self, request, pk):
        context = self.get_common_context(request, pk, title="Test")
        if request.method == "GET":
            context["title"] = f"Test `{self.object.name}` against target population"
            context["form"] = RuleTestForm()
            return TemplateResponse(request, "admin/steficon/rule/preview_rule.html", context)
        else:
            form = RuleTestForm(request.POST)
            if form.is_valid():
                target_population = form.cleaned_data["target_population"]
                context["title"] = f"Test results of `{self.object.name}` against `{target_population}`"
                context["target_population"] = target_population
                elements = []
                context["elements"] = elements
                entries = context["target_population"].selections.all()[:100]
                if entries:
                    for tp in entries:
                        value = context["rule"].execute(hh=tp.household)
                        tp.vulnerability_score = value
                        elements.append(tp)
                    self.message_user(request, "%s scores calculated" % len(elements))
                else:
                    self.message_user(request, "No records found", messages.WARNING)
            return TemplateResponse(request, "admin/steficon/rule/preview_rule.html", context)

    @atomic()
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)


@register(RuleCommit)
class RuleCommitAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ("timestamp", "rule", "version", "updated_by", "affected_fields")
    list_filter = (TextFieldFilter.factory("rule__id__iexact", "Rule"),)
    search_fields = ("name",)
    readonly_fields = ("updated_by", "rule", "affected_fields", "version")
    change_form_template = None
