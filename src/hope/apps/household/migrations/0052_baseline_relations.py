from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.comparison

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("household", "0001_migration"),
    ]

    dependencies = [
        ("account", "0037_baseline_relations"),
        ("core", "0041_baseline_models"),
        ("geo", "0010_baseline_models"),
        ("household", "0052_baseline_models"),
        ("program", "0023_baseline_models"),
        ("registration_data", "0020_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="program.program",
            ),
        ),
        migrations.CreateModel(
            name="PendingDocument",
            fields=[],
            options={
                "verbose_name": "Imported Document",
                "verbose_name_plural": "Imported Documents",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("household.document",),
        ),
        migrations.AddIndex(
            model_name="documenttype",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="household_documenttype_created_at_a5c65eca"
            ),
        ),
        migrations.AddIndex(
            model_name="documenttype",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="household_documenttype_updated_at_46741c9a"
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="household.documenttype",
            ),
        ),
        migrations.AddField(
            model_name="documentvalidator",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="validators",
                to="household.documenttype",
            ),
        ),
        migrations.AddField(
            model_name="facility",
            name="admin_area",
            field=models.ForeignKey(
                help_text="Admin area",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="facilities",
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="facility",
            name="business_area",
            field=models.ForeignKey(
                help_text="Business area",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="facilities",
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="admin1",
            field=models.ForeignKey(
                blank=True,
                help_text="Household administrative area level 1",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="admin2",
            field=models.ForeignKey(
                blank=True,
                help_text="Household administrative area level 2",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="admin3",
            field=models.ForeignKey(
                blank=True,
                help_text="Household administrative area level 3",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="admin4",
            field=models.ForeignKey(
                blank=True,
                help_text="Household administrative area level 4",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.area",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="business_area",
            field=models.ForeignKey(
                help_text="Household business area",
                on_delete=django.db.models.deletion.CASCADE,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this household was copied from another household, this field will contain the household it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="household.household",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="country",
            field=models.ForeignKey(
                blank=True,
                help_text="Household country",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.country",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="country_origin",
            field=models.ForeignKey(
                blank=True,
                help_text="Household country origin",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="geo.country",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                help_text="Household currency",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="households",
                to="core.currency",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="extra_rdis",
            field=models.ManyToManyField(
                blank=True,
                help_text="This relation is filed when collision of Household happens.",
                related_name="extra_hh_rdis",
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="facility",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="households",
                to="household.facility",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="program",
            field=models.ForeignKey(
                help_text="Household program",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="households",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="registration_data_import",
            field=models.ForeignKey(
                blank=True,
                help_text="Household registration data import",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="households",
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="storage_obj",
            field=models.ForeignKey(
                blank=True,
                help_text="Household storage object",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.storagefile",
            ),
        ),
        migrations.AddField(
            model_name="entitlementcard",
            name="household",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="entitlement_cards",
                to="household.household",
            ),
        ),
        migrations.CreateModel(
            name="PendingHousehold",
            fields=[],
            options={
                "verbose_name": "Imported Household",
                "verbose_name_plural": "Imported Households",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("household.household",),
        ),
        migrations.AddIndex(
            model_name="householdcollection",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="household_householdcollection_unicef_id_992af8db",
            ),
        ),
        migrations.AddIndex(
            model_name="householdcollection",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="household_householdcollection_unicef_id_992af8db_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="household_collection",
            field=models.ForeignKey(
                blank=True,
                help_text="Collection of household representations",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="households",
                to="household.householdcollection",
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="business_area",
            field=models.ForeignKey(
                help_text="Business area",
                on_delete=django.db.models.deletion.CASCADE,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this individual was copied from another individual, this field will contain the individual it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="household",
            field=models.ForeignKey(
                blank=True,
                help_text="This represents the household this person is a MEMBER,\n            and if null then relationship is NON_BENEFICIARY and that\n            simply means they are a representative of one or more households\n            and not a member of one.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="individuals",
                to="household.household",
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="program",
            field=models.ForeignKey(
                help_text="Program",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="individuals",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="registration_data_import",
            field=models.ForeignKey(
                help_text="RDI where Beneficiary was imported",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="individuals",
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="head_of_household",
            field=models.OneToOneField(
                blank=True,
                help_text="Household head of household",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="heading_household",
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="individual",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="household.individual",
            ),
        ),
        migrations.CreateModel(
            name="PendingIndividual",
            fields=[],
            options={
                "verbose_name": "Imported Individual",
                "verbose_name_plural": "Imported Individuals",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("household.individual",),
        ),
        migrations.AddIndex(
            model_name="individualcollection",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="household_individualcollection_unicef_id_9c88d31d",
            ),
        ),
        migrations.AddIndex(
            model_name="individualcollection",
            index=hope.models.utils.LongNameIndex(
                fields=["unicef_id"],
                name="household_individualcollection_unicef_id_9c88d31d_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="individual_collection",
            field=models.ForeignKey(
                help_text="Collection of individual representations",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="individuals",
                to="household.individualcollection",
            ),
        ),
        migrations.AddField(
            model_name="individualidentity",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this object was copied from another, this field will contain the object it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="household.individualidentity",
            ),
        ),
        migrations.AddField(
            model_name="individualidentity",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="geo.country",
            ),
        ),
        migrations.AddField(
            model_name="individualidentity",
            name="individual",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="identities",
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="individualidentity",
            name="partner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="individual_identities",
                to="account.partner",
            ),
        ),
        migrations.CreateModel(
            name="PendingIndividualIdentity",
            fields=[],
            options={
                "verbose_name": "Imported Individual Identity",
                "verbose_name_plural": "Imported Individual Identities",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("household.individualidentity",),
        ),
        migrations.AddField(
            model_name="individualroleinhousehold",
            name="copied_from",
            field=models.ForeignKey(
                blank=True,
                help_text="If this object was copied from another, this field will contain the object it was copied from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="copied_to",
                to="household.individualroleinhousehold",
            ),
        ),
        migrations.AddField(
            model_name="individualroleinhousehold",
            name="household",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="individuals_and_roles",
                to="household.household",
            ),
        ),
        migrations.AddField(
            model_name="individualroleinhousehold",
            name="individual",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="households_and_roles",
                to="household.individual",
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="representatives",
            field=models.ManyToManyField(
                help_text="This is only used to track collector (primary or secondary) of a household.\n                    They may still be a HOH of this household or any other household.\n                    Through model will contain the role (ROLE_CHOICE) they are connected with on.",
                related_name="represented_households",
                through="household.IndividualRoleInHousehold",
                to="household.individual",
            ),
        ),
        migrations.CreateModel(
            name="PendingIndividualRoleInHousehold",
            fields=[],
            options={
                "verbose_name": "Imported Individual Role In Household",
                "verbose_name_plural": "Imported Individual Roles In Household",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("household.individualroleinhousehold",),
        ),
        migrations.AddField(
            model_name="xlsxupdatefile",
            name="business_area",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="xlsxupdatefile",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="xlsxupdatefile",
            name="rdi",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="registration_data.registrationdataimport",
            ),
        ),
        migrations.AddField(
            model_name="xlsxupdatefile",
            name="uploaded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="documentvalidator",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="household_documentvalidator_created_at_114c7571",
            ),
        ),
        migrations.AddIndex(
            model_name="documentvalidator",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="household_documentvalidator_updated_at_e5956004",
            ),
        ),
        migrations.AddIndex(
            model_name="facility",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="household_facility_created_at_de99b22d"),
        ),
        migrations.AddIndex(
            model_name="facility",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="household_facility_updated_at_37444619"),
        ),
        migrations.AddConstraint(
            model_name="facility",
            constraint=models.UniqueConstraint(
                fields=("name", "business_area", "admin_area"),
                name="unique_for_ba_name_and_admin_area",
            ),
        ),
        migrations.AddIndex(
            model_name="entitlementcard",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="household_entitlementcard_created_at_97bf4a4a",
            ),
        ),
        migrations.AddIndex(
            model_name="entitlementcard",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="household_entitlementcard_updated_at_6438fd2a",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["type", "individual"], name="doc_type_individual_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=hope.models.utils.LongNameIndex(fields=["is_removed"], name="household_document_is_removed_ef7efe5b"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="household_document_created_at_3bc5e22a"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="household_document_updated_at_f16babb8"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=hope.models.utils.LongNameIndex(
                fields=["document_number"],
                name="household_document_document_number_43773c34",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=hope.models.utils.LongNameIndex(
                fields=["expiry_date"], name="household_document_expiry_date_623fe225"
            ),
        ),
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    models.Q(
                        ("is_removed", False),
                        ("status", "VALID"),
                        models.Func(
                            models.F("type_id"),
                            models.Value(True),
                            function="check_unique_document_for_individual",
                            output_field=models.BooleanField(),
                        ),
                    )
                ),
                fields=("individual", "type", "country", "program"),
                name="unique_for_individual_if_not_removed_and_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    models.Q(
                        ("is_removed", False),
                        ("status", "VALID"),
                        ("rdi_merge_status", "MERGED"),
                    )
                ),
                fields=("document_number", "type", "country", "program"),
                name="unique_if_not_removed_and_valid_for_representations",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["vector_column"], name="household_i_vector__4c5828_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "id"],
                name="hi_prog_id_active_merged_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "household"],
                name="hi_prog_hh_active_merged_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(
                    ("is_removed", False),
                    ("rdi_merge_status", "MERGED"),
                    ("sanction_list_possible_match", True),
                ),
                fields=["household"],
                name="hi_hh_sanction_possible_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(
                    ("is_removed", False),
                    ("rdi_merge_status", "MERGED"),
                    ("sanction_list_confirmed_match", True),
                ),
                fields=["household"],
                name="hi_hh_sanction_confirmed_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(
                    ("deduplication_golden_record_status", "DUPLICATE"),
                    ("is_removed", False),
                    ("rdi_merge_status", "MERGED"),
                ),
                fields=["household"],
                name="hi_hh_dup_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["household"],
                name="hi_hh_active_merged_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "unicef_id"],
                name="hi_prog_uni_act_merg_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "unicef_id"],
                include=("birth_date",),
                name="hi_prog_uni_act_merg_birth_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=models.Index(
                condition=models.Q(("is_removed", False)),
                fields=["program", "rdi_merge_status"],
                name="idx_hi_prog_rdi_status",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["is_removed"], name="household_individual_is_removed_d56b6e0f"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="household_individual_created_at_c3242865"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="household_individual_updated_at_45b7c40d"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["unicef_id"], name="household_individual_unicef_id_421e2ff2"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["full_name"], name="household_individual_full_name_8fa0162b"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["given_name"], name="household_individual_given_name_1ebbded2"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["middle_name"], name="household_individual_middle_name_1dfbf837"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["family_name"], name="household_individual_family_name_4d6db55f"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["full_name_latin"],
                name="household_individual_full_name_latin_b6e0eb4e",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["full_name_latin"],
                name="household_individual_full_name_latin_b6e0eb4e_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["given_name_latin"],
                name="household_individual_given_name_latin_e45772ab",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["given_name_latin"],
                name="household_individual_given_name_latin_e45772ab_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["middle_name_latin"],
                name="household_individual_middle_name_latin_8fd36185",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["middle_name_latin"],
                name="household_individual_middle_name_latin_8fd36185_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["family_name_latin"],
                name="household_individual_family_name_latin_e490d2fa",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["family_name_latin"],
                name="household_individual_family_name_latin_e490d2fa_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["sex"], name="household_individual_sex_7bf88507"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["sex"],
                name="household_individual_sex_7bf88507_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["birth_date"], name="household_individual_birth_date_91e492ed"
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["marital_status"],
                name="household_individual_marital_status_4f815fd6",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["marital_status"],
                name="household_individual_marital_status_4f815fd6_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["phone_no"], name="household_individual_phone_no_6323ce96"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["phone_no"],
                name="household_individual_phone_no_6323ce96_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["phone_no_alternative"],
                name="household_individual_phone_no_alternative_0c2ca589",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["phone_no_alternative"],
                name="household_individual_phone_no_alternative_0c2ca589_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["duplicate"], name="household_individual_duplicate_d00a5ad9"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(fields=["withdrawn"], name="household_individual_withdrawn_c679bc74"),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["phone_no_valid"],
                name="household_individual_phone_no_valid_60285604",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["phone_no_alternative_valid"],
                name="household_individual_phone_no_alternative_valid_2982c955",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["deduplication_golden_record_status"],
                name="household_individual_deduplication_golden_recor_f1abf0b2",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["deduplication_golden_record_status"],
                name="household_individual_deduplication_golden_rec_f1abf0b2_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["deduplication_batch_status"],
                name="household_individual_deduplication_batch_status_c60a6481",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["deduplication_batch_status"],
                name="household_individual_deduplication_batch_status_c60a6481_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["biometric_deduplication_golden_record_status"],
                name="household_individual_biometric_deduplication_go_b0296575",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["biometric_deduplication_golden_record_status"],
                name="household_individual_biometric_deduplication__b0296575_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["biometric_deduplication_batch_status"],
                name="household_individual_biometric_deduplication_ba_6e4e48dd",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["biometric_deduplication_batch_status"],
                name="household_individual_biometric_deduplication__6e4e48dd_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["sanction_list_possible_match"],
                name="household_individual_sanction_list_possible_match_d2ac3d70",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["sanction_list_confirmed_match"],
                name="household_individual_sanction_list_confirmed_match_62471337",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["country_workspace_id"],
                name="household_individual_country_workspace_id_37efac44",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["country_workspace_id"],
                name="household_individual_country_workspace_id_37efac44_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["program_registration_id"],
                name="household_individual_program_registration_id_598b7aa7",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["program_registration_id"],
                name="household_individual_program_registration_id_598b7aa7_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["identification_key"],
                name="household_individual_identification_key_3da15310",
            ),
        ),
        migrations.AddIndex(
            model_name="individual",
            index=hope.models.utils.LongNameIndex(
                fields=["identification_key"],
                name="household_individual_identification_key_3da15310_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False), ("duplicate", False)),
                fields=("unicef_id", "program"),
                name="unique_ind_unicef_id_in_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_removed", False),
                    ("identification_key__isnull", False),
                    ("rdi_merge_status", "MERGED"),
                ),
                fields=("identification_key", "program"),
                name="identification_key_ind_unique_constraint",
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False), ("originating_id__isnull", False)),
                fields=("originating_id",),
                name="originating_id_ind_unique_constraint",
            ),
        ),
        migrations.AddConstraint(
            model_name="individual",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_removed", False),
                    ("withdrawn", False),
                    ("country_workspace_id__isnull", False),
                ),
                fields=("business_area", "country_workspace_id"),
                name="country_workspace_id_ind_unique_constraint",
            ),
        ),
        migrations.AddIndex(
            model_name="individualidentity",
            index=hope.models.utils.LongNameIndex(
                fields=["is_removed"],
                name="household_individualidentity_is_removed_237a8b3b",
            ),
        ),
        migrations.AddIndex(
            model_name="individualroleinhousehold",
            index=hope.models.utils.LongNameIndex(
                fields=["is_removed"],
                name="household_individualroleinhousehold_is_removed_cee8311f",
            ),
        ),
        migrations.AddIndex(
            model_name="individualroleinhousehold",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="household_individualroleinhousehold_created_at_b1ebdac5",
            ),
        ),
        migrations.AddIndex(
            model_name="individualroleinhousehold",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="household_individualroleinhousehold_updated_at_3834d2ec",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="individualroleinhousehold",
            unique_together={("household", "individual"), ("role", "household")},
        ),
        migrations.AddIndex(
            model_name="household",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "created_at"],
                name="hh_prog_cre_active_merged",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "unicef_id"],
                name="hh_prog_unicef_act_merg_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=models.Index(fields=["size", "id"], name="hh_size_id_idx"),
        ),
        migrations.AddIndex(
            model_name="household",
            index=models.Index(
                condition=models.Q(("is_removed", False), ("rdi_merge_status", "MERGED")),
                fields=["program", "last_registration_date"],
                name="hi_prog_ltreg_act_merg_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=models.Index(
                condition=models.Q(("is_removed", False)),
                fields=["program", "rdi_merge_status"],
                name="idx_hh_prog_rdi_status",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["is_removed"], name="household_household_is_removed_252e0360"
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="household_household_created_at_c3191316"
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="household_household_updated_at_299c6681"
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(fields=["unicef_id"], name="household_household_unicef_id_6f025c4d"),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(fields=["size"], name="household_household_size_72609b19"),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(fields=["unhcr_id"], name="household_household_unhcr_id_71c2d7ae"),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["unhcr_id"],
                name="household_household_unhcr_id_71c2d7ae_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(fields=["withdrawn"], name="household_household_withdrawn_75f31056"),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["withdrawn_date"],
                name="household_household_withdrawn_date_45bc87bc",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["identification_key"],
                name="household_household_identification_key_0b623912",
            ),
        ),
        migrations.AddIndex(
            model_name="household",
            index=hope.models.utils.LongNameIndex(
                fields=["identification_key"],
                name="household_household_identification_key_0b623912_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddConstraint(
            model_name="household",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False)),
                fields=("unicef_id", "program"),
                name="unique_hh_unicef_id_in_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="household",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("is_removed", False),
                    ("identification_key__isnull", False),
                    ("rdi_merge_status", "MERGED"),
                ),
                fields=("identification_key", "program"),
                name="identification_key_unique_constraint",
            ),
        ),
        migrations.AddConstraint(
            model_name="household",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_removed", False), ("originating_id__isnull", False)),
                fields=("originating_id",),
                name="originating_id_hh_unique_constraint",
            ),
        ),
        migrations.AddIndex(
            model_name="xlsxupdatefile",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="household_xlsxupdatefile_created_at_185a6021",
            ),
        ),
        migrations.AddIndex(
            model_name="xlsxupdatefile",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="household_xlsxupdatefile_updated_at_018bdcb9",
            ),
        ),
        # household_household.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE household_household ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_hh_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            begin
                IF NEW.unicef_id IS NULL THEN
                    NEW.unicef_id := format('HH-%s-%s',TO_CHAR(NEW.first_registration_date, 'yy'), trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));
                END IF;
                return NEW;
            end
            $function$""",
                "CREATE TRIGGER create_hh_unicef_id BEFORE INSERT ON household_household FOR EACH ROW EXECUTE FUNCTION create_hh_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # household_householdcollection.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE household_householdcollection ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_hhc_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                begin
                    IF NEW.unicef_id IS NULL THEN
                        NEW.unicef_id := format('HHC-%s', trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));
                    END IF;
                    return NEW;
                end
                $function$""",
                "CREATE TRIGGER create_hhc_unicef_id BEFORE INSERT ON household_householdcollection FOR EACH ROW EXECUTE FUNCTION create_hhc_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # household_individual.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE household_individual ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_ii_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
            begin
                IF NEW.unicef_id IS NULL THEN
                    NEW.unicef_id := format('IND-%s-%s',TO_CHAR(NEW.first_registration_date, 'yy'), trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));
                END IF;
                return NEW;
            end
            $function$""",
                "CREATE TRIGGER create_ii_unicef_id BEFORE INSERT ON household_individual FOR EACH ROW EXECUTE FUNCTION create_ii_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # household_individualcollection.unicef_id comes from a serial column that is not on the model and a trigger that formats it.
        migrations.RunSQL(
            sql=[
                "ALTER TABLE household_individualcollection ADD unicef_id_index SERIAL",
                """CREATE OR REPLACE FUNCTION create_indc_unicef_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                begin
                    IF NEW.unicef_id IS NULL THEN
                        NEW.unicef_id := format('INDC-%s', trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));
                    END IF;
                    return NEW;
                end
                $function$""",
                "CREATE TRIGGER create_indc_unicef_id BEFORE INSERT ON household_individualcollection FOR EACH ROW EXECUTE FUNCTION create_indc_unicef_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Full-text search vector of an individual.
        migrations.RunSQL(
            sql=[
                "CREATE TRIGGER vector_column_trigger BEFORE INSERT OR UPDATE OF observed_disability, full_name, vector_column ON household_individual FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger('vector_column', 'pg_catalog.english', 'observed_disability', 'full_name')",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # program_registration_id gets a #<n> suffix that makes it unique.
        migrations.RunSQL(
            sql=[
                """CREATE OR REPLACE FUNCTION generate_unique_program_registration_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
                DECLARE
                    new_id TEXT;
                    count INT := 0;
                BEGIN
                    -- Check if program_registration_id is empty
                    IF NEW.program_registration_id IS NULL OR NEW.program_registration_id = '' THEN
                        NEW.program_registration_id := NULL;  -- Convert empty string to NULL
                        RETURN NEW;  -- Do not modify with increasing number
                    END IF;
                    new_id := NEW.program_registration_id || '#0';  -- Initial attempt with #0
                    LOOP
                        IF NOT EXISTS (SELECT 1 FROM household_household WHERE program_registration_id = new_id) THEN
                            EXIT;
                        END IF;
                        count := count + 1;
                        new_id := NEW.program_registration_id || '#' || count;
                    END LOOP;
                    NEW.program_registration_id := new_id;
                    RETURN NEW;
                END;
                $function$""",
                "CREATE TRIGGER unique_program_registration_id_trigger BEFORE INSERT OR UPDATE ON household_household FOR EACH ROW EXECUTE FUNCTION generate_unique_program_registration_id()",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Index that is not declared on the model.
        migrations.RunSQL(
            sql=[
                "CREATE INDEX IF NOT EXISTS household_household_default_page_index ON household_household USING btree (created_at, business_area_id, is_removed) WHERE (NOT is_removed)",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
