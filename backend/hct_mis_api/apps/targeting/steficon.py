from django import forms
from django.contrib import messages
from django.template.response import TemplateResponse

from admin_extra_urls.decorators import button

from hct_mis_api.apps.steficon.debug import get_error_info, render_exception
from hct_mis_api.apps.targeting.models import TargetPopulation

try:
    from hct_mis_api.apps.steficon.models import RuleCommit

    class RuleTestForm(forms.Form):
        rule = forms.ModelChoiceField(
            queryset=RuleCommit.objects.filter(enabled=True, deprecated=False, is_release=True)
        )
        number_of_records = forms.IntegerField()

    class SteficonExecutorMixin:
        @button()
        def test_steficon(self, request, pk):
            context = self.get_common_context(request, pk)
            if request.method == "GET":
                context["title"] = f"Test Steficon rule"
                context["form"] = RuleTestForm(initial={"number_of_records": 100, "rule": self.object.steficon_rule})
            else:
                form = RuleTestForm(request.POST)
                if form.is_valid():
                    try:
                        rule: RuleCommit = form.cleaned_data["rule"]
                        records = form.cleaned_data["number_of_records"]
                        context["title"] = f"Test results of `{rule.rule.name}` against `{self.object}`"
                        context["target_population"] = self.object
                        context["rule"] = rule
                        elements = []
                        context["elements"] = elements
                        entries = self.object.selections.all()[:records]
                        if entries:
                            for tp in entries:
                                value = rule.execute({"household": tp.household})
                                tp.vulnerability_score = value
                                elements.append(tp)
                            self.message_user(request, "%s scores calculated" % len(elements))
                        else:
                            self.message_user(request, "No records found", messages.WARNING)
                    except Exception as e:
                        from hct_mis_api.apps.steficon.debug import process_exception

                        context["exception"] = e
                        context["rule_error"] = get_error_info(e)
                        context["form"] = form
            return TemplateResponse(request, "admin/targeting/steficon.html", context)


except ImportError:

    class SteficonExecutorMixin:
        pass
