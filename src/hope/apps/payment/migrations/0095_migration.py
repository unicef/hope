from django.db import migrations, models

import hope.models.utils


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0094_migration"),
    ]

    operations = [
        # db_index=True already created these indexes under the same names, so the state just takes them over.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="paymentplangroup",
                    name="plan_type",
                    field=models.CharField(
                        choices=[
                            ("REGULAR", "Regular"),
                            ("TOP_UP", "Top Up"),
                            ("FOLLOW_UP", "Follow Up"),
                            ("TOP_UP_AMENDMENT", "Top Up Amendment"),
                        ],
                        default="REGULAR",
                        help_text=(
                            "Type of the Payment Plans the group runs; a Follow-Up / Top-Up / Amendment group is linked"
                            " [sys]"
                        ),
                        max_length=20,
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentplangroup",
                    name="status",
                    field=models.CharField(
                        choices=[
                            ("OPEN", "Open"),
                            ("LOCKED", "Locked"),
                            ("IN_APPROVAL", "In Approval"),
                            ("IN_AUTHORIZATION", "In Authorization"),
                            ("IN_REVIEW", "In Review"),
                            ("ACCEPTED", "Accepted"),
                            ("ABORTED", "Aborted"),
                            ("FINISHED", "Finished"),
                            ("READY_FOR_CLOSURE", "Ready for Closure"),
                            ("CLOSED", "Closed"),
                        ],
                        default="OPEN",
                        max_length=50,
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymentplangroup",
                    index=hope.models.utils.LongNameIndex(
                        fields=["status"], name="payment_paymentplangroup_status_c68e4ae6"
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymentplangroup",
                    index=hope.models.utils.LongNameIndex(
                        fields=["status"],
                        name="payment_paymentplangroup_status_c68e4ae6_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymentplangroup",
                    index=hope.models.utils.LongNameIndex(
                        fields=["plan_type"], name="payment_paymentplangroup_plan_type_1e21f341"
                    ),
                ),
                migrations.AddIndex(
                    model_name="paymentplangroup",
                    index=hope.models.utils.LongNameIndex(
                        fields=["plan_type"],
                        name="payment_paymentplangroup_plan_type_1e21f341_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ),
            ],
        ),
    ]
