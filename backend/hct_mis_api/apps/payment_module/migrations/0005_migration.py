from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment_module", "0004_migration"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE payment_module_paymentcycle ADD unicef_id_index SERIAL",
            "ALTER TABLE payment_module_paymentcycle DROP unicef_id_index",
        ),
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION create_pc_unicef_id() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
            begin
                NEW.unicef_id := format('PC-%s', trim(to_char(NEW.unicef_id_index,'000000')));
                return NEW;
            end
            $$;
            
            CREATE TRIGGER create_pc_unicef_id
                BEFORE INSERT
                ON payment_module_paymentcycle
                FOR EACH ROW
            EXECUTE PROCEDURE create_pc_unicef_id();
            """,
            """
            DROP TRIGGER IF EXISTS create_pc_unicef_id ON payment_module_paymentcycle
            """,
        ),
        migrations.RunSQL(
            """
            UPDATE payment_module_paymentcycle
            SET unicef_id = format('PC-%s', trim(to_char(unicef_id_index,'000000')));
            """,
            "",  # Needed to rollback migration
        ),
    ]
