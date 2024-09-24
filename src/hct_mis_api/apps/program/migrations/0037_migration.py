# Generated by Django 3.2.18 on 2023-04-17 11:41

import concurrency.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid

def populate_program_cycles(apps, schema_editor):
    Program = apps.get_model("program", "Program")
    ProgramCycle = apps.get_model("program", "ProgramCycle")
    program_cycles = []
    for program in Program.objects.all():
        program_cycles.append(
            ProgramCycle(
                program=program,
                start_date=program.start_date,
                end_date=program.end_date,
                status="ACTIVE", # ProgramCycle.ACTIVE
            )
        )

    ProgramCycle.objects.bulk_create(program_cycles)


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0036_migration'),
        ('payment', '0078_migration_squashed_0096_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCycle',
            fields=[
                ('is_removed', models.BooleanField(default=False)),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('version', concurrency.fields.IntegerVersionField(default=0, help_text='record revision number')),
                ('iteration', models.PositiveIntegerField(db_index=True, default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')], db_index=True, max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycles', to='program.program')),
            ],
            options={
                'verbose_name': 'ProgrammeCycles',
                'unique_together': {('iteration', 'program')},
            },
        ),
        migrations.RunPython(populate_program_cycles, migrations.RunPython.noop)
    ]