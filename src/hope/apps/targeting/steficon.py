import logging

from admin_extra_buttons.decorators import button
from django import forms
from django.contrib import messages
from django.db import transaction
from django.db.transaction import atomic
from django.template.response import TemplateResponse

from hope.apps.payment.celery_tasks import payment_plan_apply_steficon_hh_selection
from hope.models.payment import Payment
from hope.models.payment_plan import PaymentPlan
from hope.apps.steficon.debug import get_error_info


logger = logging.getLogger(__name__)


try:  # pragma: no cover
    from hope.models.rule import RuleCommit

    class RuleReRunForm(forms.Form):
        rule = forms.ModelChoiceField(
            queryset=RuleCommit.objects.filter(enabled=True, deprecated=False, is_release=True)
        )
        background = forms.BooleanField(required=False)
        number_of_records = forms.IntegerField(required=False)

    class RuleTestForm(forms.Form):
        rule = forms.ModelChoiceField(
            queryset=RuleCommit.objects.filter(enabled=True, deprecated=False, is_release=True)
        )
        number_of_records = forms.IntegerField(help_text="Only test # records")

    class SteficonExecutorMixin:
        @button(
            visible=lambda o, r: o.status == PaymentPlan.Status.TP_STEFICON_ERROR,
            permission="steficon.rerun_rule",
        )
        def re_run_steficon(self, request: "HttpRequest", pk: "UUID") -> TemplateResponse:
            context = self.get_common_context(request, pk)
            tp = context["original"]
            if request.method == "POST":
                form = RuleReRunForm(request.POST)
                if form.is_valid():
                    tp.steficon_rule = form.cleaned_data["rule"]
                    tp.save()
                    if form.cleaned_data["background"]:
                        payment_plan_apply_steficon_hh_selection.delay(pk)
                    else:
                        payment_plan_apply_steficon_hh_selection(pk)
            else:
                context["form"] = RuleReRunForm()
            return TemplateResponse(request, "admin/targeting/targetpopulation/steficon_rerun.html", context)

        @button(permission="steficon.rerun_rule")
        def test_steficon(self, request: "HttpRequest", pk: "UUID") -> TemplateResponse:
            context = self.get_common_context(request, pk)
            if request.method == "GET":
                context["title"] = "Test Steficon rule"
                context["form"] = RuleTestForm(
                    initial={
                        "number_of_records": 100,
                        "dry_run": True,
                        "rule": self.object.steficon_rule,
                    }
                )
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
                            for entry in entries:
                                result = rule.execute(
                                    {
                                        "household": entry.household,
                                        "payment_plan": self.object,
                                    }
                                )
                                entry.vulnerability_score = result.value
                                elements.append(entry)
                            with atomic():
                                Payment.objects.bulk_update(elements, ["vulnerability_score"])
                                transaction.set_rollback(True)
                            self.message_user(request, f"{len(elements)} scores calculated")
                        else:
                            self.message_user(request, "No records found", messages.WARNING)
                    except Exception as e:
                        logger.warning(e)
                        context["exception"] = e
                        context["rule_error"] = get_error_info(e)
                        context["form"] = form
            return TemplateResponse(request, "admin/targeting/targetpopulation/steficon_test.html", context)

except ImportError:  # pragma: no cover

    class SteficonExecutorMixin:  # type: ignore # intentional
        pass
