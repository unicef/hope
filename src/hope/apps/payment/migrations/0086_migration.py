from django.db import migrations

DEFAULT_ACTIONS = ("add", "change", "delete", "view")


def _rename_codenames(apps, model_name, old_suffix, new_suffix, new_verbose_name):
    content_type_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    content_type = content_type_model.objects.filter(app_label="payment", model=model_name).first()
    if content_type is None:
        return
    for action in DEFAULT_ACTIONS:
        permission_model.objects.filter(content_type=content_type, codename=f"{action}_{old_suffix}").update(
            codename=f"{action}_{new_suffix}", name=f"Can {action} {new_verbose_name}"
        )


def rename_permission_codenames(apps, schema_editor):
    _rename_codenames(apps, "paymentlist", "paymentplan", "paymentlist", "Payment List")
    _rename_codenames(apps, "paymentplan", "paymentplangroup", "paymentplan", "Payment Plan")


def restore_permission_codenames(apps, schema_editor):
    _rename_codenames(apps, "paymentplan", "paymentplan", "paymentplangroup", "Payment Plan Group")
    _rename_codenames(apps, "paymentlist", "paymentlist", "paymentplan", "Payment Plan")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("accountability", "0011_migration"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("payment", "0085_migration"),
        ("targeting", "0013_migration"),
        ("vision", "0006_migration"),
    ]

    operations = [
        migrations.DeleteModel(name="TargetPopulation"),
        migrations.AlterModelTable(name="paymentplan", table="payment_paymentplan"),
        migrations.AlterModelTable(name="paymentplangroup", table="payment_paymentplangroup"),
        migrations.RenameModel(old_name="PaymentPlan", new_name="PaymentList"),
        migrations.RenameModel(old_name="PaymentPlanGroup", new_name="PaymentPlan"),
        migrations.CreateModel(
            name="TargetPopulation",
            fields=[],
            options={
                "verbose_name": "Target Population",
                "verbose_name_plural": "Target Populations",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("payment.paymentlist",),
        ),
        migrations.AlterModelOptions(
            name="paymentplan",
            options={"ordering": ["created_at"], "verbose_name": "Payment Plan"},
        ),
        migrations.AlterModelOptions(
            name="paymentlist",
            options={
                "ordering": ["created_at"],
                "permissions": (
                    ("recalculate_exchange_rate", "Can recalculate USD values based on exchange rate"),
                    ("restart_preparing_payment_plan", "Can restart Preparing Payment Plans"),
                    ("restart_exporting_template_for_entitlement", "Can restart Exporting Template for Entitlements"),
                    ("restart_exporting_payment_plan_list", "Can restart Exporting Payment Plans"),
                    ("restart_importing_reconciliation_xlsx_file", "Can restart Importing Reconciliation XLSX File"),
                    ("pm_sync_payment_plan_with_pg", "Can sync payment plan with payment gateway"),
                    ("pm_manage_vision_workflow", "Can manage Payment Plan Vision workflow"),
                    ("download_payment_instruction", "Can download payment instruction from payment gateway"),
                ),
                "verbose_name": "Payment List",
            },
        ),
        migrations.RunPython(rename_permission_codenames, restore_permission_codenames),
    ]
