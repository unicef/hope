from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib.postgres.forms import DecimalRangeField
from django.db.models import Prefetch, Q

from hope.contrib.vision.models import FundsCommitmentGroup, FundsCommitmentItem
from hope.models import AcceptanceProcessThreshold, FinancialServiceProviderXlsxTemplate

if TYPE_CHECKING:
    from hope.models import PaymentPlan, PaymentPlanGroup


class VisionFundsCommitmentItemAssignmentForm(forms.Form):
    funds_commitment_group = forms.ModelChoiceField(
        queryset=FundsCommitmentGroup.objects.none(),
        label="Funds Commitment Group",
    )
    funds_commitment_items = forms.ModelMultipleChoiceField(
        queryset=FundsCommitmentItem.objects.none(),
        label="Funds Commitment Items",
    )

    def __init__(self, *args: Any, payment_plan: "PaymentPlan", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        available_items = FundsCommitmentItem.objects.filter(
            Q(payment_plan__isnull=True) | Q(payment_plan=payment_plan),
            office=payment_plan.business_area,
        ).order_by("funds_commitment_item")
        groups = (
            FundsCommitmentGroup.objects.filter(funds_commitment_items__in=available_items)
            .distinct()
            .order_by("funds_commitment_number")
            .prefetch_related(
                Prefetch(
                    "funds_commitment_items",
                    queryset=available_items,
                    to_attr="available_items",
                )
            )
        )
        self.fields["funds_commitment_group"].queryset = groups

        selected_group_id = self.data.get(self.add_prefix("funds_commitment_group")) if self.is_bound else None
        if selected_group_id and str(selected_group_id).isdigit():
            self.fields["funds_commitment_items"].queryset = available_items.filter(
                funds_commitment_group_id=selected_group_id
            )

        self.funds_commitment_options = [
            {
                "id": group.pk,
                "number": group.funds_commitment_number,
                "items": [
                    {
                        "id": item.pk,
                        "number": item.funds_commitment_item,
                        "serialNumber": item.rec_serial_number,
                        "currency": item.currency_code or "-",
                        "commitmentAmountLocal": str(item.commitment_amount_local or "-"),
                        "totalOpenAmountLocal": str(item.total_open_amount_local or "-"),
                    }
                    for item in getattr(group, "available_items", [])
                ],
            }
            for group in groups
        ]


class AcceptanceProcessThresholdForm(forms.ModelForm):
    payments_range_usd = DecimalRangeField(
        fields=[
            forms.IntegerField(required=True),
            forms.IntegerField(required=False),
        ],
    )

    class Meta:
        model = AcceptanceProcessThreshold
        fields = [
            "payments_range_usd",
            "approval_number_required",
            "authorization_number_required",
            "finance_release_number_required",
        ]


class BatchReexportForm(forms.Form):
    export_tag = forms.ChoiceField(choices=[], label="Batch to re-export")
    template = forms.ModelChoiceField(
        queryset=FinancialServiceProviderXlsxTemplate.objects.all(),
        required=False,
        label="FSP XLSX Template (optional override)",
    )

    def __init__(self, *args: Any, payment_plan_group: "PaymentPlanGroup | None" = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if payment_plan_group is not None:
            tags = (
                payment_plan_group.payment_plans.filter(export_tag__isnull=False)
                .values_list("export_tag", flat=True)
                .distinct()
                .order_by("export_tag")
            )
            self.fields["export_tag"].choices = [(t, f"Batch {t}") for t in tags]


class TemplateSelectForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=FinancialServiceProviderXlsxTemplate.objects.none(),
        label="Select FSP XLSX Template",
        required=False,
    )

    def __init__(self, *args: Any, payment_plan: Any = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if payment_plan:
            self.fields["template"].queryset = FinancialServiceProviderXlsxTemplate.objects.filter(
                financial_service_providers__allowed_business_areas__slug=payment_plan.business_area.slug
            ).distinct()
