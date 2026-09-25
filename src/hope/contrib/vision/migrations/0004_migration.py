from django.db import migrations, models

TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION funds_commitment_header_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    fc_header_id INT;
    office_id UUID;

BEGIN
    SELECT id INTO fc_header_id FROM vision_fundscommitmentheader
    WHERE funds_commitment_number = NEW.funds_commitment_number;

    IF fc_header_id IS NULL THEN
        INSERT INTO vision_fundscommitmentheader (
            funds_commitment_number,
            rec_serial_number,
            vendor_id,
            posting_date,
            document_reference,
            fc_status,
            currency
        )
        VALUES (
            NEW.funds_commitment_number,
            NEW.rec_serial_number,
            NEW.vendor_id,
            NEW.posting_date,
            NEW.document_reference,
            NEW.fc_status,
            NEW.currency_code
        )
        RETURNING id INTO fc_header_id;
    END IF;

    SELECT id INTO office_id FROM core_businessarea
    WHERE code = NEW.business_area
    LIMIT 1;

    INSERT INTO vision_fundscommitmentitem (
        funds_commitment_header_id,
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
        fc_header_id,
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
        office_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

TRIGGER_CREATION = """
DROP TRIGGER IF EXISTS funds_commitment_insert_trigger ON vision_fundscommitment;
CREATE TRIGGER funds_commitment_insert_trigger
AFTER INSERT ON vision_fundscommitment
FOR EACH ROW
EXECUTE FUNCTION funds_commitment_header_trigger_function();
"""

REVERSE_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION funds_commitment_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    fc_group_id INT;
    office_id UUID;

BEGIN
    SELECT id INTO fc_group_id FROM vision_fundscommitmentgroup
    WHERE funds_commitment_number = NEW.funds_commitment_number;

    IF fc_group_id IS NULL THEN
        INSERT INTO vision_fundscommitmentgroup (funds_commitment_number)
        VALUES (NEW.funds_commitment_number)
        RETURNING id INTO fc_group_id;
    END IF;

    SELECT id INTO office_id FROM core_businessarea
    WHERE code = NEW.business_area
    LIMIT 1;

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
        office_id
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

REVERSE_TRIGGER_CREATION = """
DROP TRIGGER IF EXISTS funds_commitment_insert_trigger ON vision_fundscommitment;
DROP FUNCTION IF EXISTS funds_commitment_header_trigger_function;
CREATE TRIGGER funds_commitment_insert_trigger
AFTER INSERT ON vision_fundscommitment
FOR EACH ROW
EXECUTE FUNCTION funds_commitment_trigger_function();
"""

BACKFILL_HEADER_FIELDS = """
UPDATE vision_fundscommitmentheader AS header
SET
    rec_serial_number = commitment.rec_serial_number,
    vendor_id = commitment.vendor_id,
    posting_date = commitment.posting_date,
    document_reference = commitment.document_reference,
    fc_status = commitment.fc_status,
    currency = commitment.currency_code
FROM (
    SELECT DISTINCT ON (funds_commitment_number)
        funds_commitment_number,
        rec_serial_number,
        vendor_id,
        posting_date,
        document_reference,
        fc_status,
        currency_code
    FROM vision_fundscommitment
    ORDER BY funds_commitment_number, rec_serial_number
) AS commitment
WHERE header.funds_commitment_number = commitment.funds_commitment_number;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("vision", "0003_migration"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="FundsCommitmentGroup",
            new_name="FundsCommitmentHeader",
        ),
        migrations.RenameField(
            model_name="fundscommitmentitem",
            old_name="funds_commitment_group",
            new_name="funds_commitment_header",
        ),
        migrations.AlterModelOptions(
            name="fundscommitmentheader",
            options={
                "verbose_name": "Funds Commitment Header",
                "verbose_name_plural": "Funds Commitment Headers",
            },
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="rec_serial_number",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="vendor_id",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="posting_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="document_reference",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="fc_status",
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name="fundscommitmentheader",
            name="currency",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.RunSQL(BACKFILL_HEADER_FIELDS, migrations.RunSQL.noop),
        migrations.RunSQL(
            TRIGGER_FUNCTION + TRIGGER_CREATION,
            REVERSE_TRIGGER_FUNCTION + REVERSE_TRIGGER_CREATION,
        ),
    ]
