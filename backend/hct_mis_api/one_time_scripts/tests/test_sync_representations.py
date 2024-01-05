import logging
from unittest import skip

from django.core.files.base import ContentFile
from django.db.models import F, Q
from django.test import TestCase
from django.utils.timezone import now

from hct_mis_api.apps.accountability.models import Feedback, Message
from hct_mis_api.apps.geo.fixtures import AreaFactory, CountryFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketNote,
)
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_NONE,
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.one_time_scripts.migrate_data_for_sync import (
    migrate_data_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.migrate_grievance_for_sync import (
    migrate_grievance_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.sync_representations import (
    ONE_TO_ONE_GREVIANCE_MODELS,
    sync_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.tests.test_migrate_data_to_representations import (
    BaseMigrateDataTestCase,
)
from hct_mis_api.one_time_scripts.tests.test_migrate_grievance_to_representations import (
    BaseGrievanceTestCase,
)

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class TestSyncRepresentations(BaseMigrateDataTestCase, BaseGrievanceTestCase, TestCase):
    def setUp(self) -> None:
        super(TestSyncRepresentations, self).setUp()  # BaseMigrateDataTestCase setUp
        super(BaseMigrateDataTestCase, self).setUp()  # BaseGrievanceTestCase setUp

    def prepare_data(self) -> None:
        # remove all representations
        hh_reprs = Household.original_and_repr_objects.filter(is_original=False, copied_from__isnull=False)
        for hh_repr in hh_reprs:
            hh_repr.selections(manager="original_and_repr_objects").all().delete()
        hh_reprs.delete()
        Individual.original_and_repr_objects.filter(is_original=False, copied_from__isnull=False).delete()
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            is_original=False, copied_from__isnull=False
        ).delete()
        GrievanceTicket.default_for_migrations_fix.filter(is_original=False, copied_from__isnull=False).delete()
        Message.original_and_repr_objects.filter(is_original=False, copied_from__isnull=False).delete()
        Feedback.original_and_repr_objects.filter(is_original=False, copied_from__isnull=False).delete()

        # make originals again (managers...)
        Household.original_and_repr_objects.all().update(is_original=True, is_migration_handled=False)
        HouseholdSelection.original_and_repr_objects.all().update(is_original=True, is_migration_handled=False)
        Individual.original_and_repr_objects.all().update(is_original=True, is_migration_handled=False)
        IndividualRoleInHousehold.original_and_repr_objects.all().update(is_original=True, is_migration_handled=False)
        GrievanceTicket.default_for_migrations_fix.all().update(
            is_original=True, business_area=self.business_area, is_migration_handled=False
        )
        Message.original_and_repr_objects.all().update(
            is_original=True, business_area=self.business_area, is_migration_handled=False
        )
        Feedback.original_and_repr_objects.all().update(
            is_original=True, business_area=self.business_area, is_migration_handled=False
        )

        migrate_data_to_representations_per_business_area(business_area=self.business_area)
        migrate_grievance_to_representations_per_business_area(business_area=self.business_area)

        # representations count
        self.assertEqual(Household.objects.filter(business_area=self.business_area).count(), 28)
        self.assertEqual(Individual.objects.filter(business_area=self.business_area).count(), 43)
        self.assertEqual(
            IndividualRoleInHousehold.objects.filter(household__business_area=self.business_area).count(), 20
        )
        self.assertEqual(BankAccountInfo.objects.filter(individual__business_area=self.business_area).count(), 22)
        self.assertEqual(Document.objects.filter(individual__business_area=self.business_area).count(), 34)
        self.assertEqual(IndividualIdentity.objects.filter(individual__business_area=self.business_area).count(), 24)
        self.assertEqual(
            GrievanceTicket.default_for_migrations_fix.filter(
                is_original=False, business_area=self.business_area
            ).count(),
            55,
        )
        self.assertEqual(
            Message.original_and_repr_objects.filter(is_original=False, business_area=self.business_area).count(),
            5,
        )
        self.assertEqual(
            Feedback.original_and_repr_objects.filter(is_original=False, business_area=self.business_area).count(),
            14,
        )
        self.assertEqual(
            TicketNote.objects.filter(ticket__is_original=False, ticket__business_area=self.business_area).count(),
            14,
        )
        self.assertEqual(
            GrievanceDocument.objects.filter(
                grievance_ticket__is_original=False, grievance_ticket__business_area=self.business_area
            ).count(),
            14,
        )

    @skip("XXX")
    def test_remove_objects(self) -> None:
        self.prepare_data()

        # soft delete originals
        Household.original_and_repr_objects.filter(is_original=True, business_area=self.business_area).delete()

        sync_representations_per_business_area(self.business_area)

        # removed representations of removed originals
        self.assertEqual(
            Household.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                business_area=self.business_area,
                is_removed=True,
                is_original=False,
            )
            .distinct()
            .count(),
            116,
        )

        # soft delete originals
        Individual.original_and_repr_objects.filter(is_original=True, business_area=self.business_area).delete()
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            is_original=True, household__business_area=self.business_area
        ).delete()
        BankAccountInfo.original_and_repr_objects.filter(
            is_original=True, individual__business_area=self.business_area
        ).delete()
        Document.original_and_repr_objects.filter(
            is_original=True, individual__business_area=self.business_area
        ).delete()
        IndividualIdentity.original_and_repr_objects.filter(
            is_original=True, individual__business_area=self.business_area
        ).delete()

        # hard delete originals
        GrievanceTicket.default_for_migrations_fix.filter(is_original=True).delete()
        self.assertEqual(GrievanceTicket.default_for_migrations_fix.filter(is_original=True).count(), 0)
        self.assertEqual(
            GrievanceDocument.objects.filter(
                grievance_ticket__is_original=False, grievance_ticket__business_area=self.business_area
            ).count(),
            14,
        )

        sync_representations_per_business_area(self.business_area)

        self.assertEqual(
            Individual.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                business_area=self.business_area,
                is_removed=True,
                is_original=False,
            ).count(),
            237,
        )
        self.assertEqual(
            IndividualRoleInHousehold.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                household__business_area=self.business_area,
                is_removed=True,
                is_original=False,
            ).count(),
            20,
        )
        self.assertEqual(
            BankAccountInfo.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                individual__business_area=self.business_area,
                is_removed=True,
                is_original=False,
            ).count(),
            22,
        )
        self.assertEqual(
            Document.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                individual__business_area=self.business_area,
                is_removed=True,
                is_original=False,
            ).count(),
            34,
        )
        self.assertEqual(
            IndividualIdentity.all_objects.filter(
                Q(copied_from__isnull=True) | Q(copied_from__is_removed=True),
                individual__business_area=self.business_area,
                is_removed=True,
                is_original=False,
            ).count(),
            24,
        )

        # GRIEVANCE
        self.assertEqual(
            GrievanceTicket.objects.filter(
                business_area=self.business_area,
                is_original=False,
            ).count(),
            0,
        )

        for _model in ONE_TO_ONE_GREVIANCE_MODELS:
            self.assertEqual(
                _model.objects.filter(
                    ticket__business_area=self.business_area,
                    ticket__is_original=False,
                ).count(),
                0,
            )

    @skip("XXX")
    def test_create_new_objects(self) -> None:
        self.prepare_data()

        # new household, new rdi, 2 new target populations, 2 new programs
        new_program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area,
            data_collecting_type=self.full,
        )
        new_program2 = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area,
            data_collecting_type=self.full,
        )

        # From HouseHoldSelection to details
        new_rdi = RegistrationDataImportFactory(business_area=self.business_area)
        new_target_population = TargetPopulationFactory(
            program=new_program,
            status=TargetPopulation.STATUS_OPEN,
            business_area=self.business_area,
        )
        new_target_population_2 = TargetPopulationFactory(
            program=new_program2,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area,
        )
        new_head_of_household = IndividualFactory(business_area=self.business_area, household=None, is_original=True)
        new_document = DocumentFactory(individual=new_head_of_household, program=None, is_original=True)
        new_identity = IndividualIdentityFactory(individual=new_head_of_household, is_original=True)
        new_bank_account_info = BankAccountInfoFactory(individual=new_head_of_household, is_original=True)

        new_household = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=new_head_of_household,
            registration_data_import=new_rdi,
            collect_individual_data=COLLECT_TYPE_NONE,
            is_original=True,
        )
        new_head_of_household.household = new_household
        new_head_of_household.save()
        new_household.target_populations.set([new_target_population, new_target_population_2])
        new_household.selections(manager="original_and_repr_objects").all().update(is_original=True)

        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=False).count(),
            28,
        )
        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=True).count(),
            75,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=False).count(),
            43,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=True).count(),
            138,
        )

        sync_representations_per_business_area(self.business_area)

        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=False).count(),
            30,
        )
        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=True).count(),
            75,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=False).count(),
            45,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=True).count(),
            138,
        )
        self.assertEqual(
            new_head_of_household.copied_to.all().count(),
            2,
        )
        self.assertEqual(new_household.copied_to.all().count(), 2)

        for new_head_of_household_representation in new_head_of_household.copied_to.all():
            self.assertEqual(new_head_of_household_representation.documents.all().count(), 1)
            self.assertEqual(new_head_of_household_representation.identities.all().count(), 1)
            self.assertEqual(new_head_of_household_representation.bank_account_info.all().count(), 1)

        # From Individual to details
        new_individual = IndividualFactory(business_area=self.business_area, household=new_household, is_original=True)
        new_document = DocumentFactory(individual=new_individual, program=None, is_original=True)
        new_identity = IndividualIdentityFactory(individual=new_individual, is_original=True)
        new_bank_account_info = BankAccountInfoFactory(individual=new_individual, is_original=True)

        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=True).count(),
            139,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=False).count(),
            45,
        )

        sync_representations_per_business_area(self.business_area)

        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=False).count(),
            30,
        )
        self.assertEqual(
            Household.original_and_repr_objects.filter(is_original=True).count(),
            75,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=False).count(),
            47,
        )
        self.assertEqual(
            Individual.original_and_repr_objects.filter(is_original=True).count(),
            139,
        )
        self.assertEqual(
            new_head_of_household.copied_to(manager="original_and_repr_objects").all().count(),
            2,
        )
        self.assertEqual(new_household.copied_to.all().count(), 2)

        for new_individual_representation in new_individual.copied_to.all():
            self.assertEqual(new_individual_representation.documents.all().count(), 1)
            self.assertEqual(new_individual_representation.identities.all().count(), 1)
            self.assertEqual(new_individual_representation.bank_account_info.all().count(), 1)

        # New details only
        new_document = DocumentFactory(individual=new_individual, program=None, is_original=True)
        new_identity = IndividualIdentityFactory(individual=new_individual, is_original=True)
        new_bank_account_info = BankAccountInfoFactory(individual=new_individual, is_original=True)

        self.assertEqual(
            Document.original_and_repr_objects.filter(is_original=True).count(),
            12,
        )
        self.assertEqual(
            Document.original_and_repr_objects.filter(is_original=False).count(),
            20,
        )
        self.assertEqual(
            IndividualIdentity.original_and_repr_objects.filter(is_original=True).count(),
            6,
        )
        self.assertEqual(
            IndividualIdentity.original_and_repr_objects.filter(is_original=False).count(),
            10,
        )
        self.assertEqual(
            BankAccountInfo.original_and_repr_objects.filter(is_original=True).count(),
            5,
        )
        self.assertEqual(
            BankAccountInfo.original_and_repr_objects.filter(is_original=False).count(),
            8,
        )

        sync_representations_per_business_area(self.business_area)

        self.assertEqual(
            Document.original_and_repr_objects.filter(is_original=True).count(),
            12,
        )
        self.assertEqual(
            Document.original_and_repr_objects.filter(is_original=False).count(),
            22,
        )
        self.assertEqual(
            IndividualIdentity.original_and_repr_objects.filter(is_original=True).count(),
            6,
        )
        self.assertEqual(
            IndividualIdentity.original_and_repr_objects.filter(is_original=False).count(),
            12,
        )
        self.assertEqual(
            BankAccountInfo.original_and_repr_objects.filter(is_original=True).count(),
            5,
        )
        self.assertEqual(
            BankAccountInfo.original_and_repr_objects.filter(is_original=False).count(),
            10,
        )
        self.assertEqual(new_household.copied_to.all().count(), 2)

        for new_individual_representation in new_individual.copied_to.all():
            self.assertEqual(new_individual_representation.documents.all().count(), 2)
            self.assertEqual(new_individual_representation.identities.all().count(), 2)
            self.assertEqual(new_individual_representation.bank_account_info.all().count(), 2)

    @skip("XXX")
    def test_update_objects(self) -> None:
        self.prepare_data()
        # Household
        hh = Household.original_and_repr_objects.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            copied_to__is_removed=False,
        ).first()
        hh.migrated_at = now()
        hh_reprs = hh.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(hh_reprs.exists())
        # update head of household
        new_head_of_household = IndividualFactory(business_area=self.business_area, household=None, is_original=True)
        hh.head_of_household = new_head_of_household
        new_head_of_household.household = hh
        new_head_of_household.save()

        # update regular fields
        hh.size = 16
        hh.save()

        sync_representations_per_business_area(self.business_area)

        for hh_repr in hh.copied_to(manager="original_and_repr_objects").all():
            self.assertEqual(hh_repr.size, 16)
            self.assertIsNotNone(hh_repr.head_of_household)
            self.assertEqual(
                hh_repr.head_of_household,
                hh.head_of_household.copied_to(manager="original_and_repr_objects")
                .filter(program=hh_repr.program)
                .first(),
            )

        # Individual
        individual = Individual.original_and_repr_objects.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            copied_to__is_removed=False,
            household__isnull=False,
        ).first()
        individual.migrated_at = now()
        individual_reprs = individual.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(individual_reprs.exists())

        # update regular fields
        individual.full_name = "Marek Kowalski"
        individual.save()

        sync_representations_per_business_area(self.business_area)

        for ind_repr in individual.copied_to(manager="original_and_repr_objects").all():
            self.assertEqual(ind_repr.full_name, "Marek Kowalski")

        # IndividualRoleInHousehold
        individual_role_in_household = IndividualRoleInHousehold.original_and_repr_objects.filter(
            is_original=True,
            household__business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            copied_to__is_removed=False,
        ).first()
        individual_role_in_household.migrated_at = now()
        individual_role_in_household_reprs = individual_role_in_household.copied_to(
            manager="original_and_repr_objects"
        ).all()
        self.assertTrue(individual_role_in_household_reprs.exists())

        _original_role = individual_role_in_household.role

        # update regular fields
        if _original_role != "Primary collector":
            _new_role = "Primary collector"
        elif _original_role != "Alternate collector":
            _new_role = "Alternate collector"
        else:
            _new_role = "None"

        individual_role_in_household.role = _new_role

        # update individual
        new_individual = IndividualFactory(business_area=self.business_area, household=None, is_original=True)
        individual_role_in_household.individual = new_individual

        individual_role_in_household.save()

        sync_representations_per_business_area(self.business_area)

        for irh_repr in individual_role_in_household.copied_to(manager="original_and_repr_objects").all():
            self.assertEqual(irh_repr.role, _new_role)
            self.assertIsNotNone(irh_repr.individual)
            self.assertEqual(
                irh_repr.individual,
                individual_role_in_household.individual.copied_to(manager="original_and_repr_objects")
                .filter(program=irh_repr.household.program)
                .first(),
            )

        #  BankAccountInfo, Document, IndividualIdentity
        individual = Individual.original_and_repr_objects.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            copied_to__is_removed=False,
            household__isnull=False,
            bank_account_info__isnull=False,
            documents__isnull=False,
            identities__isnull=False,
        ).first()
        individual.migrated_at = now()
        individual.save()
        individual_reprs = individual.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(individual_reprs.exists())

        bank_account_infos = individual.bank_account_info(manager="original_and_repr_objects").filter(is_original=True)
        self.assertTrue(bank_account_infos.exists())
        for bank_account_info in bank_account_infos:
            bank_account_info.is_migration_handled = True
            bank_account_info.bank_name = "New Bank Name"
            bank_account_info.save()

        new_country = CountryFactory(
            name="New Country",
            short_name="Ne",
            iso_code2="N",
            iso_code3="NW",
            iso_num="669",
        )

        identities = individual.identities(manager="original_and_repr_objects").filter(is_original=True)
        self.assertTrue(identities.exists())
        for identity in identities:
            identity.is_migration_handled = True
            identity.number = "123"
            identity.country = new_country
            identity.save()

        documents = individual.documents(manager="original_and_repr_objects").filter(is_original=True)
        self.assertTrue(documents.exists())
        for document in documents:
            document.is_migration_handled = True
            document.photo = ContentFile(b"...", name="foo.png")
            document.document_number = "123"
            document.country = new_country
            document.save()

        sync_representations_per_business_area(self.business_area)

        for bank_account_info in bank_account_infos:
            representations = bank_account_info.copied_to(manager="original_and_repr_objects").all()
            self.assertTrue(representations.exists())
            for representation in representations:
                self.assertEqual(representation.bank_name, "New Bank Name")

        for identity in identities:
            representations = identity.copied_to(manager="original_and_repr_objects").all()
            self.assertTrue(representations.exists())
            for representation in representations:
                self.assertEqual(representation.number, "123")
                self.assertEqual(representation.country.name, "New Country")

        for document in documents:
            representations = document.copied_to(manager="original_and_repr_objects").all()
            self.assertTrue(representations.exists())
            for representation in representations:
                self.assertTrue("foo" in representation.photo.name)
                self.assertEqual(representation.document_number, "123")
                self.assertEqual(representation.country.name, "New Country")

        # GrievanceTicket
        gt = GrievanceTicket.default_for_migrations_fix.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            ticket_notes__isnull=False,
        ).first()
        gt.migrated_at = now()
        gt_reprs = gt.copied_to(manager="default_for_migrations_fix").all()
        self.assertTrue(gt_reprs.exists())

        new_area = AreaFactory()
        gt.description = "New description"
        gt.admin2 = new_area
        gt.save()

        ticket_notes = gt.ticket_notes.all()
        self.assertEqual(ticket_notes.count(), 1)
        for ticket_note in ticket_notes:
            ticket_note.description = "New description"
            ticket_note.save()

        sync_representations_per_business_area(self.business_area)

        representations = gt.copied_to(manager="default_for_migrations_fix").all()
        self.assertTrue(representations.exists())
        for representation in representations:
            self.assertEqual(representation.description, "New description")
            self.assertEqual(representation.admin2, new_area)
            ticket_notes = representation.ticket_notes.all()
            self.assertEqual(ticket_notes.count(), 1)
            for ticket_note in ticket_notes:
                self.assertEqual(ticket_note.description, "New description")

        # Message
        message = Message.original_and_repr_objects.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
        ).first()
        message.migrated_at = now()
        message_reprs = message.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(message_reprs.exists())
        message.title = "New title"
        message.save()

        sync_representations_per_business_area(self.business_area)

        representations = message.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(representations.exists())
        for representation in representations:
            self.assertEqual(representation.title, "New title")

        # Feedback, FeedbackMessage
        feedback = Feedback.original_and_repr_objects.filter(
            is_original=True,
            business_area=self.business_area,
            copied_to__isnull=False,
            is_migration_handled=True,
            feedback_messages__isnull=False,
        ).first()
        feedback.migrated_at = now()
        feedback_reprs = feedback.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(feedback_reprs.exists())
        feedback.description = "New description"
        # feedback.household_lookup = "New household lookup"
        # feedback.individual_lookup = "New individual lookup"
        feedback.save()

        feedback_messages = feedback.feedback_messages.all()
        self.assertEqual(feedback_messages.count(), 2)
        for feedback_message in feedback_messages:
            feedback_message.description = "New description"
            feedback_message.save()

        sync_representations_per_business_area(self.business_area)

        representations = feedback.copied_to(manager="original_and_repr_objects").all()
        self.assertTrue(representations.exists())
        for representation in representations:
            self.assertEqual(representation.description, "New description")
            feedback_messages = representation.feedback_messages.all()
            self.assertEqual(feedback_messages.count(), 2)
            for feedback_message in feedback_messages:
                self.assertEqual(feedback_message.description, "New description")
