import logging

from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.widgets import AutocompleteMixin
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from admin_extra_urls.api import ExtraUrlMixin, button
from adminfilters.filters import TextFieldFilter

from hct_mis_api.apps.steficon.forms import RuleForm
from hct_mis_api.apps.steficon.models import MONITORED_FIELDS, Rule, RuleCommit
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.admin import SmartFieldsetMixin

logger = logging.getLogger(__name__)


class GenericAutocompleteMixin(AutocompleteMixin):
    url_name = "%s:%s_%s_autocomplete"

    def __init__(self, form_field, admin_site, attrs=None, choices=(), using=None):
        self.form_field = form_field
        self.empty_values = [""]
        super().__init__(None, admin_site, attrs, choices, using)

    def get_url(self):
        model = self.form_field.queryset.model
        return reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name))

    def optgroups(self, name, value, attr=None):
        """Return selected options based on the ModelChoiceIterator."""
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = {str(v) for v in value if str(v) not in self.empty_values}
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))
        choices = (
            (obj.pk, self.choices.field.label_from_instance(obj))
            for obj in self.form_field.queryset.using(self.db).filter(pk__in=selected_choices)
        )
        for option_value, option_label in choices:
            selected = str(option_value) in value and (has_selected is False or self.allow_multiple_selected)
            has_selected |= selected
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(self.create_option(name, option_value, option_label, selected_choices, index))
        return groups


class GenericAutocompleteSelect(GenericAutocompleteMixin, forms.Select):
    pass


class RuleTestForm(forms.Form):
    target_population = forms.ModelChoiceField(queryset=TargetPopulation.objects.all().order_by("name"))

    def __init__(self, *args, **kwargs):
        admin_site = kwargs.pop("admin_site")
        super().__init__(*args, **kwargs)
        tp = self.fields["target_population"]
        tp.widget = GenericAutocompleteSelect(tp, admin_site)


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

    @button()
    def used_by(self, request, pk):
        context = self.get_common_context(request, pk, title="Used By")
        if request.method == "GET":
            return TemplateResponse(request, "admin/steficon/rule/used_by.html", context)

    @button()
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

    @button()
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
            except RuleCommit.DoesNotExist:
                context["prev"] = None

            try:
                context["next"] = state.get_next_by_timestamp()
            except RuleCommit.DoesNotExist:
                context["next"] = None

            context["state"] = state
            context["title"] = (
                f"Change #{state.version} on " f"{state.timestamp.strftime('%d, %b %Y at %H:%M')} by {state.updated_by}"
            )
            return TemplateResponse(request, "admin/steficon/rule/diff.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

    @button(label="Test")
    def preview(self, request, pk):
        try:
            context = self.get_common_context(request, pk, title="Test")
            context["media"] = self.media
            if request.method == "GET":
                context["title"] = f"Test `{self.object.name}` against target population"
                context["form"] = RuleTestForm(admin_site=self.admin_site)
                return TemplateResponse(request, "admin/steficon/rule/preview_rule.html", context)
            else:
                form = RuleTestForm(request.POST, admin_site=self.admin_site)
                if form.is_valid():
                    target_population = form.cleaned_data["target_population"]
                    context["title"] = f"Test results of `{self.object.name}` against `{target_population}`"
                    context["target_population"] = target_population
                    elements = []
                    context["elements"] = elements
                    entries = context["target_population"].selections.all()[:100]
                    if entries:
                        for tp in entries:
                            value = context["original"].execute(hh=tp.household)
                            tp.vulnerability_score = value
                            elements.append(tp)
                        self.message_user(request, "%s scores calculated" % len(elements))
                    else:
                        self.message_user(request, "No records found", messages.WARNING)
                return TemplateResponse(request, "admin/steficon/rule/preview_rule.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

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
