from unittest.mock import Mock

from admin_extra_urls.extras import ExtraUrlMixin, link, action
from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin, site, register
from django.db.transaction import atomic
from django.template import Template, Context
from django.template.response import TemplateResponse
from django.utils.module_loading import import_string

from steficon.forms import RuleForm
from steficon.interpreters import mapping
from steficon.models import Rule
from steficon.score import Score
from household.models import Household
from targeting.models import TargetPopulation, HouseholdSelection


@register(Rule)
class RuleAdmin(ExtraUrlMixin, ModelAdmin):
    list_display = ('name', 'language')
    form = RuleForm

    @action(label="Preview")
    def _preview(self, request, pk):
        opts = self.model._meta
        app_label = opts.app_label

        rule = Rule.objects.get(pk=pk)
        interpreter = mapping[rule.language](rule.definition)
        elements = []
        for tp in TargetPopulation.objects.all()[:100]:
            value = interpreter.execute(hh=tp.household)
            tp.vulnerability_score = value
            elements.append(tp)
        self.message_user(request, "%s scores calculated" % len(elements))

        context = {'elements': elements,
                   'opts': opts,
                   'app_label': app_label,
                   'rule': rule}
        return TemplateResponse(request, 'preview_rule.html', context)

    @action()
    def run(self, request, pk):
        rule = Rule.objects.get(pk=pk)
        interpreter = mapping[rule.language](rule.definition)

        i = 0

        for selection in HouseholdSelection.objects.all():
            i += 1
            value = interpreter.execute(hh=selection.household)
            selection.vulnerability_score = value
            selection.save(update_fields=['vulnerability_score'])
        self.message_user(request, f"{i} scores calculated")

    @link()
    def preview(self, request):
        pass
