from admin_extra_urls.extras import ExtraUrlMixin, action
from adminfilters.filters import TextFieldFilter
from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.db.transaction import atomic
from django.template.response import TemplateResponse
from hct_mis_api.apps.steficon.forms import RuleForm
from hct_mis_api.apps.steficon.models import Rule, RuleCommit, MONITORED_FIELDS
from hct_mis_api.apps.targeting.models import TargetPopulation


class RuleTestForm(forms.Form):
    target_population = forms.ModelChoiceField(
        queryset=TargetPopulation.objects.filter(status=TargetPopulation.STATUS_DRAFT))


@register(Rule)
class RuleAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('name', 'version', 'language', 'enabled', 'deprecated', 'created_by', 'updated_by')
    list_filter = ('language', 'enabled', 'deprecated')
    search_fields = ('name',)
    form = RuleForm
    readonly_fields = ('updated_by',)
    change_form_template = None

    def get_context(self, request, pk=None, **kwargs):
        opts = self.model._meta
        app_label = opts.app_label
        self.object = None

        context = {**self.admin_site.each_context(request),
                   **kwargs,
                   'opts': opts,
                   'state_opts': RuleCommit._meta,
                   'app_label': app_label,
                   }
        if pk:
            self.object = self.get_object(request, pk)
            context['rule'] = self.object
        return context

    @action()
    def _used_by(self, request, pk):
        context = self.get_context(request, pk)
        if request.method == 'GET':
            context['form'] = RuleTestForm()
            return TemplateResponse(request, 'admin/steficon/rule/used_by.html', context)

    @action(label='changelog')
    def chagelog(self, request, pk):
        context = self.get_context(request, pk)
        context['title'] = f"Rule `{context['rule']}` change history"
        return TemplateResponse(request, 'admin/steficon/rule/changelog.html', context)

    @action()
    def _code(self, request, pk):
        context = self.get_context(request, pk)
        state_pk = request.GET.get('state_pk')
        if state_pk:
            state = self.object.history.get(pk=state_pk)
        else:
            state = self.object.history.latest()
        try:
            context['prev'] = state.get_previous_by_timestamp()
        except RuleCommit.DoesNotExist:
            context['prev'] = None

        try:
            context['next'] = state.get_next_by_timestamp()
        except RuleCommit.DoesNotExist:
            context['next'] = None

        context['state'] = state
        context['title'] = f"Change #{state.id} on {state.timestamp} by {state.updated_by}"

        return TemplateResponse(request, 'admin/steficon/rule/diff.html', context)

    @action(label="Test")
    def _preview(self, request, pk):
        context = self.get_context(request, pk)
        if request.method == 'GET':
            context['title'] = f"Test `{self.object.name}` against target population"
            context['form'] = RuleTestForm()
            return TemplateResponse(request, 'admin/steficon/rule/preview_rule.html', context)
        else:
            form = RuleTestForm(request.POST)
            if form.is_valid():
                target_population = form.cleaned_data['target_population']
                context['title'] = f"Test results of `{self.object.name}` against `{target_population}`"
                context['target_population'] = target_population
                elements = []
                context['elements'] = elements
                entries = context['target_population'].selections.all()[:100]
                if entries:
                    for tp in entries:
                        value = context['rule'].execute(hh=tp.household)
                        tp.vulnerability_score = value
                        elements.append(tp)
                    self.message_user(request, "%s scores calculated" % len(elements))
                else:
                    self.message_user(request, "No records found", messages.WARNING)
            return TemplateResponse(request, 'admin/steficon/rule/preview_rule.html', context)

    @atomic()
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)


@register(RuleCommit)
class RuleCommitAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('timestamp', 'rule', 'version', 'updated_by', 'affected_fields')
    list_filter = (TextFieldFilter.factory("rule__id__iexact", "Rule"),)
    search_fields = ('name',)
    readonly_fields = ('updated_by', 'rule', 'affected_fields', 'version')
    change_form_template = None

    def get_context(self, request, pk=None, **kwargs):
        opts = self.model._meta
        app_label = opts.app_label
        self.object = None

        context = {**self.admin_site.each_context(request),
                   **kwargs,
                   'opts': opts,
                   'app_label': app_label,
                   }
        if pk:
            self.object = self.get_object(request, pk)
            context['state'] = self.object
        return context

    @action()
    def revert(self, request, pk):
        context = self.get_context(request, pk, MONITORED_FIELDS=MONITORED_FIELDS)
        if request.method == 'GET':
            return TemplateResponse(request, 'admin/steficon/RuleCommit/revert.html', context)

    @action()
    def diff(self, request, pk):
        context = self.get_context(request, pk)
        context['state'] = self.object
        context['title'] = f"Change #{self.object.id} on {self.object.timestamp} by {self.object.updated_by}"

        return TemplateResponse(request, 'admin/steficon/RuleCommit/diff.html', context)
