from django.db import migrations, connection

TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION funds_commitment_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    fc_group_id INT;
BEGIN
    -- Check if FundsCommitmentGroup exists, if not create it
    SELECT id INTO fc_group_id FROM vision_fundscommitmentgroup 
    WHERE funds_commitment_number = NEW.funds_commitment_number;

    IF fc_group_id IS NULL THEN
        INSERT INTO vision_fundscommitmentgroup (funds_commitment_number)
        VALUES (NEW.funds_commitment_number)
        RETURNING id INTO fc_group_id;
    END IF;

    -- Insert into FundsCommitmentItem
    INSERT INTO vision_fundscommitmentitem (
        funds_commitment_group_id,
        funds_commitment_item,
        rec_serial_number,
        vendor_id,
        business_area,
        posting_date,
        vision_approval,
        document_reference,
        fc_status,
        wbs_element,
        grant_number,
        document_type,
        document_text,
        currency_code,
        gl_account,
        commitment_amount_local,
        commitment_amount_usd,
        total_open_amount_local,
        total_open_amount_usd,
        sponsor,
        sponsor_name,
        fund,
        funds_center,
        percentage,
        create_date,
        created_by,
        update_date,
        updated_by,
        office_id
    )
    VALUES (
        fc_group_id,
        NEW.funds_commitment_item,
        NEW.rec_serial_number,
        NEW.vendor_id,
        NEW.business_area,
        NEW.posting_date,
        NEW.vision_approval,
        NEW.document_reference,
        NEW.fc_status,
        NEW.wbs_element,
        NEW.grant_number,
        NEW.document_type,
        NEW.document_text,
        NEW.currency_code,
        NEW.gl_account,
        NEW.commitment_amount_local,
        NEW.commitment_amount_usd,
        NEW.total_open_amount_local,
        NEW.total_open_amount_usd,
        NEW.sponsor,
        NEW.sponsor_name,
        NEW.fund,
        NEW.funds_center,
        NEW.percentage,
        NEW.create_date,
        NEW.created_by,
        NEW.update_date,
        NEW.updated_by,
        NEW.office_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

TRIGGER_CREATION = """
CREATE TRIGGER funds_commitment_insert_trigger
AFTER INSERT ON vision_fundscommitment
FOR EACH ROW
EXECUTE FUNCTION funds_commitment_trigger_function();
"""

TRIGGER_DELETION = """
DROP TRIGGER IF EXISTS funds_commitment_insert_trigger ON vision_fundscommitment;
DROP FUNCTION IF EXISTS funds_commitment_trigger_function;
"""

def create_trigger(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(TRIGGER_FUNCTION)
        cursor.execute(TRIGGER_CREATION)

def drop_trigger(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(TRIGGER_DELETION)

class Migration(migrations.Migration):

    dependencies = [
        ("vision", "0002_migration"),
    ]

    operations = [
        migrations.RunPython(create_trigger, reverse_code=drop_trigger),
    ]
