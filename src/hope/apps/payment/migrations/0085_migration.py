from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0084_migration"),
    ]

    operations = [
        migrations.RemoveField(model_name="paymentplan", name="currency"),
        migrations.RemoveField(model_name="paymentplan", name="financial_service_provider"),
        migrations.RemoveField(model_name="paymentplan", name="use_payment_gateway"),
        migrations.RemoveField(model_name="paymentplan", name="dispersion_start_date"),
        migrations.RemoveField(model_name="paymentplan", name="dispersion_end_date"),
        migrations.RemoveField(model_name="paymentplan", name="exchange_rate"),
        migrations.RemoveField(model_name="paymentplan", name="custom_exchange_rate"),
        migrations.RemoveField(model_name="paymentplan", name="custom_exchange_rate_set_by"),
        migrations.RemoveField(model_name="paymentplan", name="export_pdf_file_summary"),
        migrations.RemoveField(model_name="paymentplan", name="export_file_delivery"),
        migrations.RemoveIndex(model_name="paymentplan", name="payment_paymentplan_export_tag_ff34093c"),
        migrations.RemoveField(model_name="paymentplan", name="export_tag"),
        migrations.RemoveField(model_name="paymentplansupportingdocument", name="payment_plan"),
        migrations.AddConstraint(
            model_name="paymentplan",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("is_removed", True),
                    models.Q(("follow_up_instruction__isnull", True), ("payment_plan_group__isnull", False)),
                    models.Q(("follow_up_instruction__isnull", False), ("payment_plan_group__isnull", True)),
                    _connector="OR",
                ),
                name="payment_plan_in_group_or_instruction_unless_removed",
            ),
        ),
        migrations.AddConstraint(
            model_name="paymentplangroup",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("plan_type", "REGULAR"), ("source_group__isnull", True)),
                    models.Q(models.Q(("plan_type", "REGULAR"), _negated=True), ("source_group__isnull", False)),
                    _connector="OR",
                ),
                name="payment_plan_group_source_group_only_on_linked",
            ),
        ),
        migrations.AddConstraint(
            model_name="approvalprocess",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("follow_up_instruction__isnull", True),
                        ("payment_plan__isnull", False),
                        ("payment_plan_group__isnull", True),
                    ),
                    models.Q(
                        ("follow_up_instruction__isnull", True),
                        ("payment_plan__isnull", True),
                        ("payment_plan_group__isnull", False),
                    ),
                    models.Q(
                        ("follow_up_instruction__isnull", False),
                        ("payment_plan__isnull", True),
                        ("payment_plan_group__isnull", True),
                    ),
                    _connector="OR",
                ),
                name="approval_process_has_one_owner",
            ),
        ),
        migrations.AddConstraint(
            model_name="paymentplansupportingdocument",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("follow_up_instruction__isnull", True), ("payment_plan_group__isnull", False)),
                    models.Q(("follow_up_instruction__isnull", False), ("payment_plan_group__isnull", True)),
                    _connector="OR",
                ),
                name="supporting_document_has_one_owner",
            ),
        ),
    ]
