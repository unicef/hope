from hct_mis_api.apps.household.models import Household, Individual, IndividualRoleInHousehold, IndividualIdentity, \
    Document, BankAccountInfo

Household.objects(program__isnull=True).delete()
Individual(program__isnull=True).objects.delete()
IndividualRoleInHousehold.objects(household__program__isnull=True).delete()
Document.objects(individual__program__isnull=True).delete()
IndividualIdentity(individual__program__isnull=True).objects.delete()
BankAccountInfo(individual__program__isnull=True).objects.delete()
# objects that cannot be deleted because they do not support soft-delete:
# Feedback, Message, GrievanceTicket, HouseholdSelection

