
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


# Country specific rules

# untargetted hhs in congo
congo = BusinessArea.objects.get(name="Democratic Republic of Congo")
rdi_congo1 = RegistrationDataImport.objects.get(name="Importation IDP, Mbulula, Cash Multipurpose", business_area=congo)
program_congo1 = Program.objects.get(name="Cash-Nutrition Manono for partners", business_area=congo)
untargetted_hhs = Household.objects.filter(
    business_area=congo, registration_data_import=rdi_congo1, selections__isnull=True
).distinct()
assert program_congo1.id in untargetted_hhs.first().copied_to().values_list("program", flat=True)

# untargetted congo_withrdawal
rdi_congo2 = RegistrationDataImport.objects.get(name="1er cohorte DPS Kinshasa, 10/05/2022", business_area=congo)
untargetted_hhs_for_withdrawal = Household.objects.filter(
    business_area=congo, registration_data_import=rdi_congo2, selections__isnull=True
).distinct()
for hh_repr in Household.objects.filter(copied_from__in=untargetted_hhs_for_withdrawal):
    assert hh_repr.withdrawn

# rdi in sudan
sudan = BusinessArea.objects.get(name="Sudan")
rdi_sudan1 = RegistrationDataImport.objects.get(name="H&N GAVI Locality EPI officers", business_area=sudan)
program_sudan1 = Program.objects.get(name="Gavi Federal incentives", business_area=sudan)
for household in rdi_sudan1.households.all():
    assert program_sudan1.id in household.copied_to().values_list("program", flat=True)

# ignore in afghanistan
afghanistan = BusinessArea.objects.get(name="Afghanistan")
rdi_to_ignore = RegistrationDataImport.objects.get(name="APMU - MoE - Teacher Incentives - July Payroll - Group 8 - 20220314-4001-8000", business_area=afghanistan)
for household in rdi_to_ignore.households.all():
    assert household.copied_to().count() == 0

# unknown_unassigned
trinidad_and_tobago = BusinessArea.objects.get(name="Trinidad & Tobago")
assert not Program.all_objects.filter(name="Storage program - COLLECTION TYPE Unknown", business_area=trinidad_and_tobago).exists()  # this program is not created since the unassigned unknown are enrolled to TEEN program


# for hh that is a part of tp in closed program
chosen_hh =
program =
print(chosen_hh.individuals.all())
print(chosen_hh.representatives.all())
print(chosen_hh.copied_to.all())
household_repr = chosen_hh.copied_to.filter(program=program).first()
print(household_repr.individuals.all())
print(household_repr.individuals.values_list("program"))
print(household_repr.individuals.values_list("copied_from"))
print(household_repr.representives.all())
print(household_repr.representives.values_list("program"))
print(household_repr.representives.values_list("copied_from"))
# can also check documents, identities, bank_account_info


# for hh that is a part of tp in active program (best if not whole RDI is in this TP)
chosen_hh =
program =
print(chosen_hh.individuals.all())
print(chosen_hh.representatives.all())
print(chosen_hh.copied_to.all())
household_repr = chosen_hh.copied_to.filter(program=program).first()
print(household_repr.individuals.all())
print(household_repr.individuals.values_list("program"))
print(household_repr.individuals.values_list("copied_from"))
print(household_repr.representives.all())
print(household_repr.representives.values_list("program"))
print(household_repr.representives.values_list("copied_from"))
# can also check documents, identities, bank_account_info

all_households_from_this_rdi = chosen_hh.registration_data_import.households.all()
for household_from_rdi in all_households_from_this_rdi:
    assert program.id in household_from_rdi.copied_to().values_list("program", flat=True)


