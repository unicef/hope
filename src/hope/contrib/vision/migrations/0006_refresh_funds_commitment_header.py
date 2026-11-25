from django.db import migrations

TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION funds_commitment_header_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    fc_header_id INT;
    office_id UUID;

BEGIN
    INSERT INTO vision_fundscommitmentheader (
        funds_commitment_number,
        vendor_id,
        posting_date,
        document_reference,
        fc_status,
        currency
    )
    VALUES (
        NEW.funds_commitment_number,
        NEW.vendor_id,
        NEW.posting_date,
        NEW.document_reference,
        NEW.fc_status,
        NEW.currency_code
    )
    ON CONFLICT (funds_commitment_number) DO UPDATE
        SET vendor_id = COALESCE(EXCLUDED.vendor_id, vision_fundscommitmentheader.vendor_id),
            posting_date = EXCLUDED.posting_date,
            document_reference = EXCLUDED.document_reference,
            fc_status = EXCLUDED.fc_status,
            currency = EXCLUDED.currency
    RETURNING id INTO fc_header_id;

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


REVERSE_TRIGGER_FUNCTION = """
CREATE OR REPLACE FUNCTION funds_commitment_header_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    fc_header_id INT;
    office_id UUID;

BEGIN
    INSERT INTO vision_fundscommitmentheader (
        funds_commitment_number,
        vendor_id,
        posting_date,
        document_reference,
        fc_status,
        currency
    )
    VALUES (
        NEW.funds_commitment_number,
        NEW.vendor_id,
        NEW.posting_date,
        NEW.document_reference,
        NEW.fc_status,
        NEW.currency_code
    )
    ON CONFLICT (funds_commitment_number) DO UPDATE
        SET funds_commitment_number = EXCLUDED.funds_commitment_number
    RETURNING id INTO fc_header_id;

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


class Migration(migrations.Migration):
    dependencies = [("vision", "0005_migration")]

    operations = [migrations.RunSQL(TRIGGER_FUNCTION, REVERSE_TRIGGER_FUNCTION)]
