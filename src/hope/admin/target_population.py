from typing import Any

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from django.contrib import admin
from django.http import HttpRequest

from hope.admin.payment_plan import FundsCommitmentItemInline, PaymentInstructionInline
from hope.admin.utils import HOPEModelAdminBase, ViewOnUiMixin
from hope.apps.activity_log.utils import copy_model_object, create_diff
from hope.apps.utils.security import is_root
from hope.models import PaymentPlan, TargetPopulation, log_create


@admin.register(TargetPopulation)
class TargetPopulationAdmin(ViewOnUiMixin, HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "name",
        "business_area",
        "program_cycle",
        "status",
        "use_payment_gateway",
        "background_action_status",
        "build_status",
        "plan_type",
    )
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program_cycle__program", AutoCompleteFilter),
        ("program_cycle__program__id", ValueFilter),
        ("currency__code", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
        "use_payment_gateway",
        ("background_action_status", ChoicesFieldComboFilter),
        ("build_status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
        ("plan_type", ChoicesFieldComboFilter),
    )
    search_fields = ("id", "unicef_id", "name")
    date_hierarchy = "updated_at"
    filter_horizontal = ("payment_plan_purposes",)
    inlines = [FundsCommitmentItemInline, PaymentInstructionInline]
    raw_id_fields = (
        "imported_file",
        "export_file_entitlement",
        "export_pdf_file_summary",
        "reconciliation_import_file",
    )
    readonly_fields = (
        "is_removed",
        "id",
        "created_at",
        "updated_at",
        "version",
        "unicef_id",
        "internal_data",
        "business_area",
        "program_cycle",
        "steficon_rule",
        "steficon_rule_targeting",
        "created_by",
        "closed_by",
        "closure_comment",
        "source_payment_plan",
        "follow_up_instruction",
        "name",
        "start_date",
        "end_date",
        "currency",
        "dispersion_start_date",
        "dispersion_end_date",
        "excluded_ids",
        "exclusion_reason",
        "vulnerability_score_min",
        "vulnerability_score_max",
        "abort_comment",
        "flat_amount_value",
        "built_at",
        "exchange_rate",
        "custom_exchange_rate",
        "custom_exchange_rate_set_by",
        "female_children_count",
        "male_children_count",
        "female_adults_count",
        "male_adults_count",
        "total_households_count",
        "total_individuals_count",
        "imported_file_date",
        "total_entitled_quantity",
        "total_entitled_quantity_usd",
        "total_entitled_quantity_revised",
        "total_entitled_quantity_revised_usd",
        "total_delivered_quantity",
        "total_delivered_quantity_usd",
        "total_undelivered_quantity",
        "total_undelivered_quantity_usd",
        "steficon_targeting_applied_date",
        "steficon_applied_date",
        "plan_type",
        "export_tag",
        "exclude_household_error",
        "status_date",
    )

    def frontend_url(self, obj: TargetPopulation) -> str:
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/target-population/{obj.id}"

    def get_form(self, request: HttpRequest, obj: Any | None = None, change: bool = False, **kwargs: Any) -> Any:
        request._payment_plan_obj = obj
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request: HttpRequest, obj: TargetPopulation, form: Any, change: bool) -> None:
        old_payment_plan = copy_model_object(PaymentPlan.objects.get(pk=obj.pk)) if change and obj.pk else None
        super().save_model(request, obj, form, change)
        # skip a no-op log when an edit touched only fields outside ACTIVITY_LOG_MAPPING
        if old_payment_plan is not None and not create_diff(old_payment_plan, obj, PaymentPlan.ACTIVITY_LOG_MAPPING):
            return
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=obj.program.pk,
            old_object=old_payment_plan,
            new_object=obj,
        )

    def formfield_for_manytomany(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "payment_plan_purposes":
            obj = getattr(request, "_payment_plan_obj", None)
            if obj is not None:
                kwargs["queryset"] = obj.program_cycle.program.payment_plan_purposes.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return is_root(request)
