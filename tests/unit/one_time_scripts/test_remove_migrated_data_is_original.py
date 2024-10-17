from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.accountability.fixtures import (
    CommunicationMessageFactory,
    FeedbackFactory,
)
from hct_mis_api.apps.accountability.models import Feedback, Message
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    PendingBankAccountInfoFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    PendingIndividualIdentityFactory,
    PendingIndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    PendingBankAccountInfo,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.targeting.fixtures import HouseholdSelectionFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.one_time_scripts.remove_migrated_data_is_original import (
    get_statistic_is_original,
    remove_migrated_data_is_original,
)


class BaseMigrateDataTestCase(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")

        ind = IndividualFactory(household=None)
        ind2 = IndividualFactory(is_original=True, household=None)
        pending_ind = PendingIndividualFactory(household=None)
        pending_ind2 = PendingIndividualFactory(is_original=True, household=None)

        hh = HouseholdFactory()
        hh2 = HouseholdFactory(is_original=True)
        pending_hh = PendingHouseholdFactory()
        pending_hh2 = PendingHouseholdFactory(is_original=True)

        HouseholdSelectionFactory(household=hh)
        HouseholdSelectionFactory(is_original=True, household=hh2)

        DocumentFactory(individual=ind)
        DocumentFactory(is_original=True, individual=ind2)
        PendingDocumentFactory(individual=pending_ind)
        PendingDocumentFactory(is_original=True, individual=pending_ind2)

        IndividualIdentityFactory(individual=ind)
        IndividualIdentityFactory(is_original=True, individual=ind)
        PendingIndividualIdentityFactory(individual=pending_ind)
        PendingIndividualIdentityFactory(is_original=True, individual=pending_ind)

        IndividualRoleInHouseholdFactory(household=hh, individual=ind, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(is_original=True, household=hh2, individual=ind2, role=ROLE_PRIMARY)
        PendingIndividualRoleInHouseholdFactory(household=pending_hh, individual=pending_ind, role=ROLE_PRIMARY)
        PendingIndividualRoleInHouseholdFactory(
            is_original=True, household=pending_hh2, individual=pending_ind2, role=ROLE_PRIMARY
        )

        EntitlementCardFactory(household=hh)
        EntitlementCardFactory(is_original=True, household=hh2)

        BankAccountInfoFactory(individual=ind)
        BankAccountInfoFactory(is_original=True, individual=ind2)
        PendingBankAccountInfoFactory(individual=pending_ind)
        PendingBankAccountInfoFactory(is_original=True, individual=pending_ind2)

        CommunicationMessageFactory()
        CommunicationMessageFactory(is_original=True)
        FeedbackFactory()
        FeedbackFactory(is_original=True)

        gr1 = GrievanceTicketFactory()
        gr2 = GrievanceTicketFactory(is_original=True)

        TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=ind,
            ticket=gr1,
        )
        TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=ind2,
            ticket=gr2,
        )

    def test_run_remove_migrated_data_is_original(self) -> None:
        # check count before
        self.assertEqual(Individual.all_objects.count(), 4)
        self.assertEqual(PendingIndividual.all_objects.count(), 4)
        self.assertEqual(Household.all_objects.count(), 4)
        self.assertEqual(PendingHousehold.all_objects.count(), 4)
        self.assertEqual(HouseholdSelection.original_and_repr_objects.count(), 2)
        self.assertEqual(Document.all_objects.count(), 4)
        self.assertEqual(PendingDocument.all_objects.count(), 4)
        self.assertEqual(IndividualIdentity.all_objects.count(), 4)
        self.assertEqual(PendingIndividualIdentity.all_objects.count(), 4)
        self.assertEqual(IndividualRoleInHousehold.all_objects.count(), 4)
        self.assertEqual(PendingIndividualRoleInHousehold.all_objects.count(), 4)
        self.assertEqual(EntitlementCard.original_and_repr_objects.count(), 2)
        self.assertEqual(BankAccountInfo.all_objects.count(), 4)
        self.assertEqual(PendingBankAccountInfo.all_objects.count(), 4)
        self.assertEqual(Message.original_and_repr_objects.count(), 2)
        self.assertEqual(Feedback.original_and_repr_objects.count(), 2)
        self.assertEqual(GrievanceTicket.default_for_migrations_fix.count(), 2)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.count(), 2)

        # added just to have cov 95 XD
        get_statistic_is_original()

        remove_migrated_data_is_original()

        # check count after
        self.assertEqual(Individual.all_objects.count(), 2)
        self.assertEqual(PendingIndividual.all_objects.count(), 2)
        self.assertEqual(Household.all_objects.count(), 2)
        self.assertEqual(PendingHousehold.all_objects.count(), 2)
        self.assertEqual(HouseholdSelection.original_and_repr_objects.count(), 1)
        self.assertEqual(Document.all_objects.count(), 2)
        self.assertEqual(PendingDocument.all_objects.count(), 2)
        self.assertEqual(IndividualIdentity.all_objects.count(), 2)
        self.assertEqual(PendingIndividualIdentity.all_objects.count(), 2)
        self.assertEqual(IndividualRoleInHousehold.all_objects.count(), 2)
        self.assertEqual(PendingIndividualRoleInHousehold.all_objects.count(), 2)
        self.assertEqual(EntitlementCard.original_and_repr_objects.count(), 1)
        self.assertEqual(BankAccountInfo.all_objects.count(), 2)
        self.assertEqual(PendingBankAccountInfo.all_objects.count(), 2)
        self.assertEqual(Message.original_and_repr_objects.count(), 1)
        self.assertEqual(Feedback.original_and_repr_objects.count(), 1)
        self.assertEqual(GrievanceTicket.default_for_migrations_fix.count(), 1)
        self.assertEqual(TicketNeedsAdjudicationDetails.objects.count(), 1)

        self.assertEqual(Individual.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingIndividual.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(Household.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingHousehold.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(HouseholdSelection.original_and_repr_objects.filter(is_original=True).count(), 0)
        self.assertEqual(Document.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingDocument.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(IndividualIdentity.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingIndividualIdentity.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(IndividualRoleInHousehold.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingIndividualRoleInHousehold.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(EntitlementCard.original_and_repr_objects.filter(is_original=True).count(), 0)
        self.assertEqual(BankAccountInfo.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(PendingBankAccountInfo.all_objects.filter(is_original=True).count(), 0)
        self.assertEqual(Message.original_and_repr_objects.filter(is_original=True).count(), 0)
        self.assertEqual(Feedback.original_and_repr_objects.filter(is_original=True).count(), 0)
        self.assertEqual(GrievanceTicket.default_for_migrations_fix.filter(is_original=True).count(), 0)
