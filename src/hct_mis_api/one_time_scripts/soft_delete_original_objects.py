from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)


def soft_delete_original_objects() -> None:
    Household.objects.filter(program__isnull=True).delete()
    Individual.objects.filter(program__isnull=True).delete()
    IndividualRoleInHousehold.objects.filter(household__program__isnull=True).delete()
    Document.objects.filter(individual__program__isnull=True).delete()
    IndividualIdentity.objects.filter(individual__program__isnull=True).delete()
    BankAccountInfo.objects.filter(individual__program__isnull=True).delete()
    # objects that cannot be deleted because they do not support soft-delete:
    # Feedback, Message, GrievanceTicket
