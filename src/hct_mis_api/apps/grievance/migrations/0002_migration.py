# Generated by Django 3.2.25 on 2024-11-07 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('grievance', '0001_migration'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sanction_list', '0001_migration'),
        ('household', '0002_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketsystemflaggingdetails',
            name='golden_records_individual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='household.individual'),
        ),
        migrations.AddField(
            model_name='ticketsystemflaggingdetails',
            name='sanction_list_individual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='sanction_list.sanctionlistindividual'),
        ),
        migrations.AddField(
            model_name='ticketsystemflaggingdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='system_flagging_ticket_details', to='grievance.grievanceticket'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensitive_ticket_details', to='household.household'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensitive_ticket_details', to='household.individual'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='payment_content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sensitive_ticket_details', to='grievance.grievanceticket'),
        ),
        migrations.AddField(
            model_name='ticketreferraldetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referral_ticket_details', to='household.household'),
        ),
        migrations.AddField(
            model_name='ticketreferraldetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referral_ticket_details', to='household.individual'),
        ),
        migrations.AddField(
            model_name='ticketreferraldetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='referral_ticket_details', to='grievance.grievanceticket'),
        ),
        migrations.AddField(
            model_name='ticketpositivefeedbackdetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='household.household'),
        ),
        migrations.AddField(
            model_name='ticketpositivefeedbackdetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='household.individual'),
        ),
        migrations.AddField(
            model_name='ticketpositivefeedbackdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='grievance.grievanceticket'),
        ),
    ]