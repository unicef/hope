from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("accountability", "0001_migration"),
    ]

    dependencies = [
        ("accountability", "0013_baseline_models"),
        ("core", "0044_baseline_models"),
        ("geo", "0010_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("grievance", "0022_baseline_models"),
        ("household", "0056_baseline_models"),
        ("payment", "0084_baseline_models"),
        ("program", "0027_baseline_models"),
        ("registration_data", "0022_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="admin2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="feedback",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this object was copied from another, this field will contain the object it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="accountability.feedback",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="feedbacks",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="household_lookup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="feedbacks",
                to="household.household",
                verbose_name="Household lookup",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="individual_lookup",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="feedbacks",
                to="household.individual",
                verbose_name="Individual lookup",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="linked_grievance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="feedback",
                to="grievance.grievanceticket",
                verbose_name="Linked grievance",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="feedbackmessage",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="feedback_messages",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="feedbackmessage",
            name="feedback",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="feedback_messages",
                to="accountability.feedback",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="message",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this object was copied from another, this field will contain the object it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="accountability.message",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="households",
            field=models.ManyToManyField(blank=True, related_name="messages", to="household.household"),
        ),
        migrations.AddField(
            model_name="message",
            name="payment_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="messages",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="registration_data_import",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="survey",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="surveys",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created by",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="payment_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="surveys",
                to="payment.paymentplan",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="surveys",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="recipients",
            field=models.ManyToManyField(blank=True, related_name="surveys", to="household.household"),
        ),
        migrations.AddIndex(
            model_name="feedback",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="accountability_feedback_created_at_70179f13",
            ),
        ),
        migrations.AddIndex(
            model_name="feedback",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="accountability_feedback_updated_at_14c6d99e",
            ),
        ),
        migrations.AddIndex(
            model_name="feedback",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"], name="accountability_feedback_unicef_id_37792878"
            ),
        ),
        migrations.AddIndex(
            model_name="feedback",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="accountability_feedback_unicef_id_37792878_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="feedbackmessage",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="accountability_feedbackmessage_created_at_c0d52383",
            ),
        ),
        migrations.AddIndex(
            model_name="feedbackmessage",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="accountability_feedbackmessage_updated_at_3e2b51d8",
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="accountability_message_created_at_6189007a"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="accountability_message_updated_at_0c461641"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"], name="accountability_message_unicef_id_e1aefe5a"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="accountability_message_unicef_id_e1aefe5a_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="survey",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="accountability_survey_created_at_818ed9ba"
            ),
        ),
        migrations.AddIndex(
            model_name="survey",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="accountability_survey_updated_at_504609e0"
            ),
        ),
        migrations.AddIndex(
            model_name="survey",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"], name="accountability_survey_unicef_id_09eaa181"
            ),
        ),
        migrations.AddIndex(
            model_name="survey",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="accountability_survey_unicef_id_09eaa181_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
    ]
