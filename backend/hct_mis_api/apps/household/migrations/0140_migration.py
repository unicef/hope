from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0139_migration'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='document',
            name='unique_if_not_removed_and_valid',
        ),
        migrations.AddField(
            model_name='documenttype',
            name='unique_for_individual',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL(
            """
            create or replace function check_unique_document_for_individual(uuid, boolean)
               returns boolean
               language plpgsql
               immutable
              as
            $$
            begin
                return(select exists(select 1 from household_documenttype where id = $1 and unique_for_individual = $2));
            end;
            $$
            """,
            migrations.RunSQL.noop,
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('is_removed', False), ('status', 'VALID'), django.db.models.expressions.Func(django.db.models.expressions.F('type_id'), django.db.models.expressions.Value(True), function='check_unique_document_for_individual', output_field=models.BooleanField()))), fields=('type', 'country'), name='unique_for_individual_if_not_removed_and_valid'),
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('is_removed', False), ('status', 'VALID'), django.db.models.expressions.Func(django.db.models.expressions.F('type_id'), django.db.models.expressions.Value(False), function='check_unique_document_for_individual', output_field=models.BooleanField()))), fields=('document_number', 'type', 'country'), name='unique_if_not_removed_and_valid'),
        ),
    ]
