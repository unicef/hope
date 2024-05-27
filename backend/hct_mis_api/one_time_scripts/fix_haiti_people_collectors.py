from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


def fix_haiti_people_collectors() -> None:
    rdi_1 = RegistrationDataImport.objects.get(id="bb8a178b-b4cc-4f6a-a19c-365249d9c3ac")
    rdi_2 = RegistrationDataImport.objects.get(id="fe57fe15-6d1d-42d7-a597-6b7d47899b08")

    assert rdi_1.households.count() == 74
    assert rdi_2.households.count() == 27

    roles_to_create = []
    for rdi in [rdi_1, rdi_2]:
        for household in rdi.households.all():
            collector = household.individuals.first()
            roles_to_create.append(
                IndividualRoleInHousehold(household=household, individual=collector, role=ROLE_PRIMARY)
            )

    IndividualRoleInHousehold.objects.bulk_create(roles_to_create)
