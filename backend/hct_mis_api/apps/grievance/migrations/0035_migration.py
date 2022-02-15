import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0093_migration'),
        ('grievance', '0034_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievanceticket',
            name='extras',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='ticketaddindividualdetails',
            name='individual_data',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='ticketdeleteindividualdetails',
            name='role_reassign_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='tickethouseholddataupdatedetails',
            name='household_data',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='ticketindividualdataupdatedetails',
            name='individual_data',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='ticketindividualdataupdatedetails',
            name='role_reassign_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='ticketneedsadjudicationdetails',
            name='extra_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='ticketneedsadjudicationdetails',
            name='role_reassign_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='ticketsystemflaggingdetails',
            name='role_reassign_data',
            field=models.JSONField(default=dict),
        migrations.CreateModel(
            name='TicketDeleteHouseholdDetails',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('role_reassign_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('approve_status', models.BooleanField(default=False)),
                ('household', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delete_household_ticket_details', to='household.Household')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delete_household_ticket_details', to='grievance.GrievanceTicket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
