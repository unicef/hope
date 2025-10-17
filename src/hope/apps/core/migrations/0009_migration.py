from django.db import migrations


def add_sanction_list_to_program(apps, schema_editor):
    Program = apps.get_model("program", "Program")
    SanctionList = apps.get_model("sanction_list", "SanctionList")
    programs = Program.objects.filter(business_area__screen_beneficiary=True)
    un_sanction_lists = SanctionList.objects.first()
    for program in programs:
        program.sanction_lists.add(un_sanction_lists)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_migration"),
        ("program", "0005_migration"),
        ("sanction_list", "0003_migration"),
    ]

    operations = [
        migrations.RunPython(add_sanction_list_to_program, migrations.RunPython.noop),
    ]
