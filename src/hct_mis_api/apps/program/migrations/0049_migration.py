# Generated by Django 3.2.25 on 2024-07-16 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0048_migration'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION program_cycle_fill_unicef_id_per_business_area_seq() RETURNS trigger
                    LANGUAGE plpgsql
                    AS $$
                    DECLARE
                        businessAreaID varchar;
                        businessAreaCode varchar;
                    BEGIN
                        SELECT INTO businessAreaID p.business_area_id FROM program_program p WHERE p.id = NEW.program_id;
                        SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id = businessAreaID::uuid;
                        NEW.unicef_id := format('PC-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('program_cycle_business_area_seq_' || translate(businessAreaID::text, '-','_')),'000000'),',','.')));
                        RETURN NEW;
                    END;
                    $$;
                """,
        ),
        migrations.RunSQL(
            sql="CREATE TRIGGER program_cycle_fill_unicef_id_per_business_area_seq BEFORE INSERT ON program_programcycle FOR EACH ROW EXECUTE PROCEDURE program_cycle_fill_unicef_id_per_business_area_seq();",
        ),
    ]
