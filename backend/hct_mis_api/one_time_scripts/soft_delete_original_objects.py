from hct_mis_api.apps.household.models import Household, Individual, IndividualRoleInHousehold, IndividualIdentity, \
    Document, BankAccountInfo

Household.objects.delete()
Individual.objects.delete()
IndividualRoleInHousehold.objects.delete()
Document.objects.delete()
IndividualIdentity.objects.delete()
BankAccountInfo.objects.delete()
# objects that cannot be deleted because they do not support soft-delete:
# Feedback, Message, GrievanceTicket, HouseholdSelection

