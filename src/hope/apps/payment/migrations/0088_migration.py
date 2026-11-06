from decimal import Decimal

from django.conf import settings
import django.core.validators
from django.db import migrations, models
from django.db.models import Case, F, Value, When
import django.db.models.deletion

# Celery tasks and job actions renamed with the payment list rename: periodic tasks and jobs store these paths.
TASK_RENAMES = {
    "hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_async_task": "hope.apps.payment.celery_tasks.create_payment_list_xlsx_async_task",
    "hope.apps.payment.celery_tasks.create_payment_plan_payment_list_xlsx_async_task_action": "hope.apps.payment.celery_tasks.create_payment_list_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task": "hope.apps.payment.celery_tasks.export_payment_plan_delivery_xlsx_async_task",
    "hope.apps.payment.celery_tasks.export_payment_plan_group_delivery_xlsx_async_task_action": "hope.apps.payment.celery_tasks.export_payment_plan_delivery_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.export_pdf_payment_plan_group_summary_async_task": "hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task",
    "hope.apps.payment.celery_tasks.export_pdf_payment_plan_group_summary_async_task_action": "hope.apps.payment.celery_tasks.export_pdf_payment_plan_summary_async_task_action",
    "hope.apps.payment.celery_tasks.import_payment_plan_group_delivery_from_xlsx_async_task": "hope.apps.payment.celery_tasks.import_payment_plan_delivery_from_xlsx_async_task",
    "hope.apps.payment.celery_tasks.import_payment_plan_group_delivery_from_xlsx_async_task_action": "hope.apps.payment.celery_tasks.import_payment_plan_delivery_from_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.import_payment_plan_group_fsp_extra_fields_from_xlsx_async_task": "hope.apps.payment.celery_tasks.import_payment_plan_fsp_extra_fields_from_xlsx_async_task",
    "hope.apps.payment.celery_tasks.import_payment_plan_group_fsp_extra_fields_from_xlsx_async_task_action": "hope.apps.payment.celery_tasks.import_payment_plan_fsp_extra_fields_from_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.import_payment_plan_payment_list_from_xlsx_async_task": "hope.apps.payment.celery_tasks.import_payment_list_from_xlsx_async_task",
    "hope.apps.payment.celery_tasks.import_payment_plan_payment_list_from_xlsx_async_task_action": "hope.apps.payment.celery_tasks.import_payment_list_from_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.mark_payment_plan_rebuild_error": "hope.apps.payment.celery_tasks.mark_payment_list_rebuild_error",
    "hope.apps.payment.celery_tasks.notify_payment_plan_group_reconciliation_import_failure": "hope.apps.payment.celery_tasks.notify_payment_plan_reconciliation_import_failure",
    "hope.apps.payment.celery_tasks.payment_plan_apply_engine_rule_async_task": "hope.apps.payment.celery_tasks.payment_list_apply_engine_rule_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_apply_engine_rule_async_task_action": "hope.apps.payment.celery_tasks.payment_list_apply_engine_rule_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_apply_steficon_hh_selection_async_task": "hope.apps.payment.celery_tasks.payment_list_apply_steficon_hh_selection_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_apply_steficon_hh_selection_async_task_action": "hope.apps.payment.celery_tasks.payment_list_apply_steficon_hh_selection_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_exclude_beneficiaries_async_task": "hope.apps.payment.celery_tasks.payment_list_exclude_beneficiaries_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_exclude_beneficiaries_async_task_action": "hope.apps.payment.celery_tasks.payment_list_exclude_beneficiaries_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_full_rebuild_async_task": "hope.apps.payment.celery_tasks.payment_list_full_rebuild_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_full_rebuild_async_task_action": "hope.apps.payment.celery_tasks.payment_list_full_rebuild_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_rebuild_stats_async_task": "hope.apps.payment.celery_tasks.payment_list_rebuild_stats_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_rebuild_stats_async_task_action": "hope.apps.payment.celery_tasks.payment_list_rebuild_stats_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_refresh_payees_async_task": "hope.apps.payment.celery_tasks.payment_list_refresh_payees_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_refresh_payees_async_task_action": "hope.apps.payment.celery_tasks.payment_list_refresh_payees_async_task_action",
    "hope.apps.payment.celery_tasks.payment_plan_set_entitlement_flat_amount_async_task": "hope.apps.payment.celery_tasks.payment_list_set_entitlement_flat_amount_async_task",
    "hope.apps.payment.celery_tasks.payment_plan_set_entitlement_flat_amount_async_task_action": "hope.apps.payment.celery_tasks.payment_list_set_entitlement_flat_amount_async_task_action",
    "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task": "hope.apps.payment.celery_tasks.periodic_send_payment_list_reconciliation_overdue_emails_async_task",
    "hope.apps.payment.celery_tasks.periodic_send_payment_plan_reconciliation_overdue_emails_async_task_action": "hope.apps.payment.celery_tasks.periodic_send_payment_list_reconciliation_overdue_emails_async_task_action",
    "hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp_async_task": "hope.apps.payment.celery_tasks.periodic_sync_payment_list_invoices_western_union_ftp_async_task",
    "hope.apps.payment.celery_tasks.periodic_sync_payment_plan_invoices_western_union_ftp_async_task_action": "hope.apps.payment.celery_tasks.periodic_sync_payment_list_invoices_western_union_ftp_async_task_action",
    "hope.apps.payment.celery_tasks.prepare_child_payment_plan_async_task": "hope.apps.payment.celery_tasks.prepare_child_payment_list_async_task",
    "hope.apps.payment.celery_tasks.prepare_child_payment_plan_async_task_action": "hope.apps.payment.celery_tasks.prepare_child_payment_list_async_task_action",
    "hope.apps.payment.celery_tasks.prepare_payment_plan_async_task": "hope.apps.payment.celery_tasks.prepare_payment_list_async_task",
    "hope.apps.payment.celery_tasks.prepare_payment_plan_async_task_action": "hope.apps.payment.celery_tasks.prepare_payment_list_async_task_action",
    "hope.apps.payment.celery_tasks.remove_old_payment_plan_payment_list_xlsx_async_task": "hope.apps.payment.celery_tasks.remove_old_payment_list_xlsx_async_task",
    "hope.apps.payment.celery_tasks.remove_old_payment_plan_payment_list_xlsx_async_task_action": "hope.apps.payment.celery_tasks.remove_old_payment_list_xlsx_async_task_action",
    "hope.apps.payment.celery_tasks.send_payment_plan_group_delivery_xlsx_password_async_task": "hope.apps.payment.celery_tasks.send_payment_plan_delivery_xlsx_password_async_task",
    "hope.apps.payment.celery_tasks.send_payment_plan_group_delivery_xlsx_password_async_task_action": "hope.apps.payment.celery_tasks.send_payment_plan_delivery_xlsx_password_async_task_action",
    "hope.apps.payment.celery_tasks.send_payment_plan_group_notification_emails_async_task": "hope.apps.payment.celery_tasks.send_payment_plan_notification_emails_async_task",
    "hope.apps.payment.celery_tasks.send_payment_plan_group_notification_emails_async_task_action": "hope.apps.payment.celery_tasks.send_payment_plan_notification_emails_async_task_action",
    "hope.apps.payment.celery_tasks.send_payment_plan_reconciliation_overdue_email_async_task": "hope.apps.payment.celery_tasks.send_payment_list_reconciliation_overdue_email_async_task",
    "hope.apps.payment.celery_tasks.send_payment_plan_reconciliation_overdue_email_async_task_action": "hope.apps.payment.celery_tasks.send_payment_list_reconciliation_overdue_email_async_task_action",
    "hope.contrib.vision.tasks.notify_payment_plan_group_status_to_vision_async_task": "hope.contrib.vision.tasks.notify_payment_plan_status_to_vision_async_task",
    "hope.contrib.vision.tasks.notify_payment_plan_group_status_to_vision_async_task_action": "hope.contrib.vision.tasks.notify_payment_plan_status_to_vision_async_task_action",
    "hope.contrib.vision.tasks.send_payment_plan_group_to_vision_async_task": "hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task",
    "hope.contrib.vision.tasks.send_payment_plan_group_to_vision_async_task_action": "hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task_action",
}
# Job config keys, applied in this order: the plan takes the list's old key.
CONFIG_KEY_RENAMES = (("payment_plan_id", "payment_list_id"), ("payment_plan_group_id", "payment_plan_id"))
CONFIG_KEY_SQL = (
    "UPDATE core_asyncjob SET config = (config - %s) || jsonb_build_object(%s, config -> %s) WHERE config ? %s",
    "UPDATE core_periodicasyncjob SET config = (config - %s) || jsonb_build_object(%s, config -> %s) WHERE config ? %s",
)
DEFAULT_ACTIONS = ("add", "change", "delete", "view")
MODEL_PERMISSION_RENAMES = (
    ("paymentlistsplit", "paymentplansplit", "paymentlistsplit", "payment list split", "payment plan split"),
    (
        "paymentlistsplitpayments",
        "paymentplansplitpayments",
        "paymentlistsplitpayments",
        "payment list split payments",
        "payment plan split payments",
    ),
    (
        "westernunionpaymentlistreport",
        "westernunionpaymentplanreport",
        "westernunionpaymentlistreport",
        "Western Union Payment List Report",
        "Western Union Payment Plan Report",
    ),
)
CUSTOM_PERMISSION_RENAMES = (
    (
        "restart_preparing_payment_plan",
        "restart_preparing_payment_list",
        "Can restart Preparing Payment Plans",
        "Can restart Preparing Payment Lists",
    ),
    (
        "restart_exporting_payment_plan_list",
        "restart_exporting_payment_list",
        "Can restart Exporting Payment Plans",
        "Can restart Exporting Payment Lists",
    ),
    (
        "pm_sync_payment_plan_with_pg",
        "pm_sync_payment_list_with_pg",
        "Can sync payment plan with payment gateway",
        "Can sync payment list with payment gateway",
    ),
)


def _rename_permissions(apps, forward: bool) -> None:
    content_type_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    content_types = dict(content_type_model.objects.filter(app_label="payment").values_list("model", "id"))
    for model_name, old_suffix, new_suffix, new_label, old_label in MODEL_PERMISSION_RENAMES:
        source, target, label = (old_suffix, new_suffix, new_label) if forward else (new_suffix, old_suffix, old_label)
        for action in DEFAULT_ACTIONS:
            permission_model.objects.filter(
                content_type_id=content_types.get(model_name), codename=f"{action}_{source}"
            ).update(codename=f"{action}_{target}", name=f"Can {action} {label}")
    for old_codename, new_codename, old_name, new_name in CUSTOM_PERMISSION_RENAMES:
        source, target, name = (
            (old_codename, new_codename, new_name) if forward else (new_codename, old_codename, old_name)
        )
        permission_model.objects.filter(content_type_id=content_types.get("paymentlist"), codename=source).update(
            codename=target, name=name
        )


def _rename_tasks(apps, schema_editor, renames: dict[str, str], key_renames) -> None:
    periodic_task_model = apps.get_model("django_celery_beat", "PeriodicTask")
    periodic_task_model.objects.filter(task__in=renames).update(task=_mapped("task", renames))
    job_names = {old.rsplit(".", 1)[-1]: new.rsplit(".", 1)[-1] for old, new in renames.items()}
    # Beat finds its row by name, which is the schedule key: a row left under the old key would get a second row
    # created next to it and the task would run twice.
    periodic_task_model.objects.filter(name__in=job_names).update(name=_mapped("name", job_names))
    for job_model_name in ("AsyncJob", "PeriodicAsyncJob"):
        job_model = apps.get_model("core", job_model_name)
        job_model.objects.filter(action__in=renames).update(action=_mapped("action", renames))
        job_model.objects.filter(job_name__in=job_names).update(job_name=_mapped("job_name", job_names))
    for sql in CONFIG_KEY_SQL:
        for old_key, new_key in key_renames:
            schema_editor.execute(sql, [old_key, new_key, old_key, old_key])


def _mapped(field: str, renames: dict[str, str]) -> Case:
    return Case(*(When(**{field: old}, then=Value(new)) for old, new in renames.items()), default=F(field))


def forwards(apps, schema_editor) -> None:
    _rename_permissions(apps, forward=True)
    _rename_tasks(apps, schema_editor, TASK_RENAMES, CONFIG_KEY_RENAMES)


def backwards(apps, schema_editor) -> None:
    _rename_permissions(apps, forward=False)
    reverse_keys = tuple((new, old) for old, new in reversed(CONFIG_KEY_RENAMES))
    _rename_tasks(apps, schema_editor, {new: old for old, new in TASK_RENAMES.items()}, reverse_keys)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("core", "0041_migration"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
        ("payment", "0087_migration"),
    ]

    operations = [
        migrations.AlterModelTable(name="paymentplansplit", table="payment_paymentplansplit"),
        migrations.AlterModelTable(name="paymentplansplitpayments", table="payment_paymentplansplitpayments"),
        migrations.AlterModelTable(name="westernunionpaymentplanreport", table="payment_westernunionpaymentplanreport"),
        migrations.RenameModel(old_name="PaymentPlanSplit", new_name="PaymentListSplit"),
        migrations.RenameModel(old_name="PaymentPlanSplitPayments", new_name="PaymentListSplitPayments"),
        migrations.RenameModel(old_name="WesternUnionPaymentPlanReport", new_name="WesternUnionPaymentListReport"),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameField(model_name="approvalprocess", old_name="payment_plan", new_name="payment_list"),
                migrations.RenameField(
                    model_name="approvalprocess", old_name="payment_plan_group", new_name="payment_plan"
                ),
                migrations.RenameField(
                    model_name="paymentlist", old_name="source_payment_plan", new_name="source_payment_list"
                ),
                migrations.RenameField(
                    model_name="paymentlist", old_name="payment_plan_group", new_name="payment_plan"
                ),
                migrations.RenameField(
                    model_name="paymentplan", old_name="source_group", new_name="source_payment_plan"
                ),
                migrations.RenameField(model_name="paymentlistsplit", old_name="payment_plan", new_name="payment_list"),
                migrations.RenameField(
                    model_name="paymentlistsplitpayments", old_name="payment_plan_split", new_name="payment_list_split"
                ),
                migrations.RenameField(
                    model_name="paymentplansupportingdocument", old_name="payment_plan_group", new_name="payment_plan"
                ),
                migrations.RenameField(
                    model_name="paymentverificationplan", old_name="payment_plan", new_name="payment_list"
                ),
                migrations.RenameField(
                    model_name="paymentverificationsummary", old_name="payment_plan", new_name="payment_list"
                ),
                migrations.RenameField(
                    model_name="westernunionpaymentlistreport", old_name="payment_plan", new_name="payment_list"
                ),
                migrations.AlterModelOptions(
                    name="westernunionpaymentlistreport",
                    options={
                        "ordering": ("id",),
                        "verbose_name": "Western Union Payment List Report",
                        "verbose_name_plural": "Western Union Payment List Reports",
                    },
                ),
                migrations.AlterModelOptions(
                    name="paymentlist",
                    options={
                        "ordering": ["created_at"],
                        "permissions": (
                            (
                                "recalculate_exchange_rate",
                                "Can recalculate USD values based on exchange rate",
                            ),
                            (
                                "restart_preparing_payment_list",
                                "Can restart Preparing Payment Lists",
                            ),
                            (
                                "restart_exporting_template_for_entitlement",
                                "Can restart Exporting Template for Entitlements",
                            ),
                            (
                                "restart_exporting_payment_list",
                                "Can restart Exporting Payment Lists",
                            ),
                            (
                                "restart_importing_reconciliation_xlsx_file",
                                "Can restart Importing Reconciliation XLSX File",
                            ),
                            (
                                "pm_sync_payment_list_with_pg",
                                "Can sync payment list with payment gateway",
                            ),
                            (
                                "pm_manage_vision_workflow",
                                "Can manage Payment Plan Vision workflow",
                            ),
                            (
                                "download_payment_instruction",
                                "Can download payment instruction from payment gateway",
                            ),
                        ),
                        "verbose_name": "Payment List",
                    },
                ),
                migrations.RemoveConstraint(
                    model_name="approvalprocess",
                    name="approval_process_has_one_owner",
                ),
                migrations.RemoveConstraint(
                    model_name="paymentlist",
                    name="payment_plan_in_group_or_instruction_unless_removed",
                ),
                migrations.RemoveConstraint(
                    model_name="paymentplan",
                    name="payment_plan_group_source_group_only_on_linked",
                ),
                migrations.RemoveConstraint(
                    model_name="paymentplansupportingdocument",
                    name="supporting_document_has_one_owner",
                ),
                migrations.AlterField(
                    model_name="approvalprocess",
                    name="payment_list",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_process",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="approvalprocess",
                    name="payment_plan",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_group_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_process",
                        to="payment.paymentplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="closed_by",
                    field=models.ForeignKey(
                        blank=True,
                        help_text="User who closed the payment plan",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="closed_payment_lists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="created_by",
                    field=models.ForeignKey(
                        help_text="Created by user",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_payment_lists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="follow_up_instruction",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_lists",
                        to="payment.followupinstruction",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="payment_plan",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_group_id",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_lists",
                        to="payment.paymentplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="payment_plan_purposes",
                    field=models.ManyToManyField(
                        blank=True,
                        help_text="Payment plan purposes",
                        related_name="payment_lists",
                        to="payment.paymentplanpurpose",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="program_cycle",
                    field=models.ForeignKey(
                        help_text="Program Cycle",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_lists",
                        to="program.programcycle",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="source_payment_list",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="source_payment_plan_id",
                        help_text="Source Payment Plan (applicable for follow-up and top-up Payment Plans)",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="child_plans",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="steficon_rule",
                    field=models.ForeignKey(
                        blank=True,
                        help_text="Engine Formula for calculation entitlement value",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_lists",
                        to="steficon.rulecommit",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="steficon_rule_targeting",
                    field=models.ForeignKey(
                        blank=True,
                        help_text="Engine Formula for calculation vulnerability score value",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_lists_target",
                        to="steficon.rulecommit",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlistsplit",
                    name="payment_list",
                    field=models.ForeignKey(
                        db_column="payment_plan_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="splits",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlistsplitpayments",
                    name="payment",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_list_split_payment",
                        to="payment.payment",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlistsplitpayments",
                    name="payment_list_split",
                    field=models.ForeignKey(
                        db_column="payment_plan_split_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_list_split",
                        to="payment.paymentlistsplit",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="currency",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_plans",
                        to="core.currency",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="cycle",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_plans",
                        to="program.programcycle",
                        verbose_name="Programme Cycle",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="financial_service_provider",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payment_plans",
                        to="payment.financialserviceprovider",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="source_payment_plan",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="source_group_id",
                        help_text="The group this Follow-Up / Top-Up / Amendment group was created from [sys]",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="linked_payment_plans",
                        to="payment.paymentplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplansupportingdocument",
                    name="payment_plan",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="payment_plan_group_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="payment.paymentplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentverificationplan",
                    name="payment_list",
                    field=models.ForeignKey(
                        db_column="payment_plan_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_verification_plans",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentverificationsummary",
                    name="payment_list",
                    field=models.OneToOneField(
                        blank=True,
                        db_column="payment_plan_id",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_verification_summary",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="westernunionpaymentlistreport",
                    name="payment_list",
                    field=models.ForeignKey(
                        db_column="payment_plan_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="western_union_reports",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="approvalprocess",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            models.Q(
                                ("follow_up_instruction__isnull", True),
                                ("payment_list__isnull", False),
                                ("payment_plan__isnull", True),
                            ),
                            models.Q(
                                ("follow_up_instruction__isnull", True),
                                ("payment_list__isnull", True),
                                ("payment_plan__isnull", False),
                            ),
                            models.Q(
                                ("follow_up_instruction__isnull", False),
                                ("payment_list__isnull", True),
                                ("payment_plan__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="approval_process_has_one_owner",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymentlist",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            ("is_removed", True),
                            models.Q(
                                ("follow_up_instruction__isnull", True),
                                ("payment_plan__isnull", False),
                            ),
                            models.Q(
                                ("follow_up_instruction__isnull", False),
                                ("payment_plan__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="payment_plan_in_group_or_instruction_unless_removed",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymentplan",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("plan_type", "REGULAR"), ("source_payment_plan__isnull", True)),
                            models.Q(
                                models.Q(("plan_type", "REGULAR"), _negated=True),
                                ("source_payment_plan__isnull", False),
                            ),
                            _connector="OR",
                        ),
                        name="payment_plan_group_source_group_only_on_linked",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="paymentplansupportingdocument",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            models.Q(
                                ("follow_up_instruction__isnull", True),
                                ("payment_plan__isnull", False),
                            ),
                            models.Q(
                                ("follow_up_instruction__isnull", False),
                                ("payment_plan__isnull", True),
                            ),
                            _connector="OR",
                        ),
                        name="supporting_document_has_one_owner",
                    ),
                ),
                migrations.AlterField(
                    model_name="followupinstruction",
                    name="background_action_status",
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ("RECALCULATING", "Recalculating Payment List data"),
                            ("RECALCULATING_ERROR", "Payment List recalculation error"),
                            ("XLSX_EXPORTING", "Exporting XLSX"),
                            (
                                "XLSX_IMPORTING_RECONCILIATION",
                                "Importing Reconciliation from XLSX",
                            ),
                            ("XLSX_EXPORT_ERROR", "Error while exporting XLSX"),
                            ("XLSX_IMPORT_ERROR", "Error while importing XLSX"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name="followupinstruction",
                    name="use_payment_gateway",
                    field=models.BooleanField(
                        default=False,
                        help_text="Send the payment lists through the payment gateway regardless of the FSP communication channel",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="closed_by",
                    field=models.ForeignKey(
                        blank=True,
                        help_text="User who closed the payment list",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="closed_payment_lists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="end_date",
                    field=models.DateTimeField(blank=True, help_text="Payment List end date", null=True),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="flat_amount_value",
                    field=models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Apply a fixed amount of entitlement for all payment records within a payment list",
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="plan_type",
                    field=models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("TOP_UP", "Top Up"),
                            ("FOLLOW_UP", "Follow Up"),
                            ("TOP_UP_AMENDMENT", "Top Up Amendment"),
                        ],
                        default="REGULAR",
                        help_text="Payment List type [sys]",
                        max_length=20,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="source_payment_list",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="source_payment_plan_id",
                        help_text="Source Payment List (applicable for follow-up and top-up Payment Lists)",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="child_plans",
                        to="payment.paymentlist",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="start_date",
                    field=models.DateTimeField(blank=True, help_text="Payment List start date", null=True),
                ),
                migrations.AlterField(
                    model_name="paymentlist",
                    name="status_date",
                    field=models.DateTimeField(help_text="Date and time of Payment List status [sys]"),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="background_action_status",
                    field=models.CharField(
                        blank=True,
                        choices=[
                            ("RECALCULATING", "Recalculating Payment List data"),
                            ("RECALCULATING_ERROR", "Payment List recalculation error"),
                            ("XLSX_EXPORTING", "Exporting XLSX file"),
                            ("XLSX_EXPORT_ERROR", "Export XLSX file Error"),
                            (
                                "XLSX_IMPORTING_RECONCILIATION",
                                "Importing Reconciliation XLSX file",
                            ),
                            (
                                "XLSX_IMPORTING_FSP_EXTRA_FIELDS",
                                "Importing FSP Extra Fields XLSX file",
                            ),
                            ("XLSX_IMPORT_ERROR", "Import XLSX file Error"),
                            ("REBUILDING", "Rebuilding"),
                            ("REBUILD_ERROR", "Rebuild Error"),
                        ],
                        default=None,
                        help_text="Background Action Status for asynchronous payment plan tasks [sys]",
                        max_length=50,
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="name",
                    field=models.CharField(default="Default Payment Plan", max_length=255),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="plan_type",
                    field=models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("TOP_UP", "Top Up"),
                            ("FOLLOW_UP", "Follow Up"),
                            ("TOP_UP_AMENDMENT", "Top Up Amendment"),
                        ],
                        default="REGULAR",
                        help_text="Type of the Payment Lists the payment plan runs; a Follow-Up / Top-Up / Amendment payment plan is linked [sys]",
                        max_length=20,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="source_payment_plan",
                    field=models.ForeignKey(
                        blank=True,
                        db_column="source_group_id",
                        help_text="The payment plan this Follow-Up / Top-Up / Amendment payment plan was created from [sys]",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="linked_payment_plans",
                        to="payment.paymentplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplan",
                    name="use_payment_gateway",
                    field=models.BooleanField(
                        default=False,
                        help_text="Send the payment lists through the payment gateway regardless of the FSP communication channel",
                    ),
                ),
            ],
        ),
        migrations.RunPython(forwards, backwards),
    ]
