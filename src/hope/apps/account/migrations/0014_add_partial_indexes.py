from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0013_migration"),
    ]

    operations = [
        # Add partial index for role assignments where expiry_date is NULL (never expires)
        migrations.RunSQL(
            sql="CREATE INDEX idx_ra_user_no_expiry ON account_roleassignment(user_id) WHERE expiry_date IS NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_ra_user_no_expiry;",
        ),
        # Add partial index for partner + business_area where expiry_date is NULL
        migrations.RunSQL(
            sql="CREATE INDEX idx_ra_partner_ba_no_exp ON account_roleassignment(partner_id, business_area_id) WHERE expiry_date IS NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_ra_partner_ba_no_exp;",
        ),
        # Add partial index for business_area where expiry_date is NULL
        migrations.RunSQL(
            sql="CREATE INDEX idx_ra_ba_no_expiry ON account_roleassignment(business_area_id) WHERE expiry_date IS NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_ra_ba_no_expiry;",
        ),
    ]
