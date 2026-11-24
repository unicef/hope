from django.db import migrations, models
import django.db.models.deletion

from hope.apps.core.migration_operations import RunSQLAfterDeferred
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("vision", "0001_migration"),
        ("vision", "0002_migration"),
        ("vision", "0003_migration"),
        ("vision", "0004_migration"),
        ("vision", "0005_migration"),
    ]

    dependencies = [
        ("core", "0041_baseline_models"),
        ("payment", "0081_baseline_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="DownPayment",
            fields=[
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("business_area", models.CharField(max_length=4)),
                ("down_payment_reference", models.CharField(max_length=20)),
                ("document_type", models.CharField(max_length=10)),
                ("consumed_fc_number", models.CharField(max_length=10)),
                (
                    "consumed_fc_item_number",
                    models.CharField(blank=True, max_length=3, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                ("doc_year", models.IntegerField(blank=True, null=True)),
                ("doc_number", models.CharField(blank=True, max_length=10, null=True)),
                ("doc_item_number", models.CharField(max_length=3, null=True)),
                (
                    "total_down_payment_amount_local",
                    models.DecimalField(decimal_places=2, max_digits=15),
                ),
                (
                    "total_down_payment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FundsCommitmentHeader",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "funds_commitment_number",
                    models.CharField(max_length=10, unique=True),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "document_reference",
                    models.CharField(blank=True, max_length=16, null=True),
                ),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                ("currency", models.CharField(blank=True, max_length=5, null=True)),
                (
                    "payment_plans",
                    models.ManyToManyField(
                        blank=True,
                        related_name="funds_commitment_headers",
                        to="payment.paymentplan",
                    ),
                ),
            ],
            options={
                "verbose_name": "Funds Commitment Header",
                "verbose_name_plural": "Funds Commitment Headers",
            },
        ),
        migrations.CreateModel(
            name="FundsCommitment",
            fields=[
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                (
                    "funds_commitment_number",
                    models.CharField(blank=True, max_length=10, null=True),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "business_area",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "vision_approval",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
                ("document_reference", models.CharField(max_length=16, null=True)),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "funds_commitment_item",
                    models.CharField(blank=True, default="", max_length=3, null=True),
                ),
                (
                    "wbs_element",
                    models.CharField(blank=True, default="", max_length=24, null=True),
                ),
                (
                    "grant_number",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "document_type",
                    models.CharField(blank=True, max_length=2, null=True),
                ),
                (
                    "document_text",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("gl_account", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "commitment_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "commitment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "sponsor",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "sponsor_name",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "fund",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "funds_center",
                    models.CharField(blank=True, default="", max_length=16, null=True),
                ),
                (
                    "percentage",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
            options={
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_number"],
                        name="vision_fundscommitment_funds_commitment_number_7eeae3be",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_number"],
                        name="vision_fundscommitment_funds_commitment_number_7eeae3be_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="FundsCommitmentItem",
            fields=[
                ("funds_commitment_item", models.CharField(max_length=3)),
                (
                    "rec_serial_number",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("vendor_id", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "business_area",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                ("posting_date", models.DateField(blank=True, null=True)),
                (
                    "vision_approval",
                    models.CharField(blank=True, max_length=1, null=True),
                ),
                ("document_reference", models.CharField(max_length=16, null=True)),
                ("fc_status", models.CharField(blank=True, max_length=1, null=True)),
                (
                    "wbs_element",
                    models.CharField(blank=True, default="", max_length=24, null=True),
                ),
                (
                    "grant_number",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "document_type",
                    models.CharField(blank=True, max_length=2, null=True),
                ),
                (
                    "document_text",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "currency_code",
                    models.CharField(blank=True, max_length=5, null=True),
                ),
                ("gl_account", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "commitment_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "commitment_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_local",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "total_open_amount_usd",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
                ),
                (
                    "sponsor",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "sponsor_name",
                    models.CharField(blank=True, default="", max_length=100, null=True),
                ),
                (
                    "fund",
                    models.CharField(blank=True, default="", max_length=10, null=True),
                ),
                (
                    "funds_center",
                    models.CharField(blank=True, default="", max_length=16, null=True),
                ),
                (
                    "percentage",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "created_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                ("update_date", models.DateTimeField(blank=True, null=True)),
                (
                    "updated_by",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "funds_commitment_header",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="funds_commitment_items",
                        to="vision.fundscommitmentheader",
                    ),
                ),
                (
                    "office",
                    models.ForeignKey(
                        blank=True,
                        help_text="This can be a business office or a business area",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="core.businessarea",
                    ),
                ),
            ],
            options={
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_item"],
                        name="vision_fundscommitmentitem_funds_commitment_item_ab1d46fb",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["funds_commitment_item"],
                        name="vision_fundscommitmentitem_funds_commitment_item_ab1d46fb_like",
                        opclasses=["varchar_pattern_ops"],
                    ),
                ],
            },
        ),
        # Every inserted funds commitment row is split into a header and an item.
        # funds_commitment_trigger_function is the previous version: no trigger uses it, but every existing
        # database still has it.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION funds_commitment_trigger_function()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    fc_group_id INT;
    office_id UUID;

BEGIN
    -- Check if FundsCommitmentGroup exists, if not create it
    SELECT id INTO fc_group_id FROM vision_fundscommitmentgroup
    WHERE funds_commitment_number = NEW.funds_commitment_number;

    IF fc_group_id IS NULL THEN
        INSERT INTO vision_fundscommitmentgroup (funds_commitment_number)
        VALUES (NEW.funds_commitment_number)
        RETURNING id INTO fc_group_id;
    END IF;

    -- Try to get BusinessArea.id using the business_area code
    SELECT id INTO office_id FROM core_businessarea
    WHERE code = NEW.business_area
    LIMIT 1;

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
        office_id
    );

    RETURN NEW;
END;
$function$""",
                """CREATE OR REPLACE FUNCTION funds_commitment_header_trigger_function()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
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
$function$""",
                "CREATE TRIGGER funds_commitment_insert_trigger AFTER INSERT ON vision_fundscommitment FOR EACH ROW EXECUTE FUNCTION funds_commitment_header_trigger_function()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Names that RenameModel and RenameField left behind in the replaced history. Every existing database
        # has them, so a new one gets them too. Renaming the index of a primary key or unique constraint
        # renames the constraint with it.
        RunSQLAfterDeferred(
            sql=[
                "ALTER INDEX IF EXISTS vision_fundscommitmentheader_funds_commitment_number_key RENAME TO vision_fundscommitmenthe_funds_commitment_number_cb571cb3_uniq",
                "ALTER INDEX IF EXISTS vision_fundscommitmentheader_pkey RENAME TO vision_fundscommitmentgroup_pkey",
                "ALTER INDEX IF EXISTS vision_fundscommitmentitem_funds_commitment_header_id_b22857ee RENAME TO vision_fundscommitmentitem_funds_commitment_group_id_a20597ad",
                "ALTER SEQUENCE IF EXISTS vision_fundscommitmentheader_id_seq RENAME TO vision_fundscommitmentgroup_id_seq",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
