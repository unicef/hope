"""Tests for pending changes: managers, proxy models, soft delete, and merge status transitions."""

import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.models import (
    BusinessArea,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PendingIndividualRoleInHousehold,
    Program,
    RegistrationDataImport,
)
from hope.models.account import Account, PendingAccount
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="TestBA", slug="test-ba")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(program: Program, business_area: BusinessArea) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program,
        business_area=business_area,
        status=RegistrationDataImport.IN_REVIEW,
    )


# ---------------------------------------------------------------------------
# 1. PendingManager / SoftDeletablePendingManager filtering
# ---------------------------------------------------------------------------


class TestPendingManagerFiltering:
    def test_pending_household_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )

        assert pending in PendingHousehold.objects.all()
        assert merged not in PendingHousehold.objects.all()

    def test_pending_individual_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )

        assert pending in PendingIndividual.objects.all()
        assert merged not in PendingIndividual.objects.all()

    def test_pending_document_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pending_doc = PendingDocumentFactory(individual=pending_ind, program=rdi.program)
        merged_doc = DocumentFactory(individual=merged_ind, program=rdi.program)

        assert pending_doc in PendingDocument.objects.all()
        assert merged_doc not in PendingDocument.objects.all()

    def test_pending_household_excludes_soft_deleted(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        hh.delete(soft=True)

        assert hh not in PendingHousehold.objects.all()
        assert hh in PendingHousehold.all_objects.filter(is_removed=True)

    def test_all_objects_includes_both_pending_and_merged(self, rdi: RegistrationDataImport) -> None:
        pending = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )

        assert pending in Household.all_objects.all()
        assert merged in Household.all_objects.all()


# ---------------------------------------------------------------------------
# 2. SoftDeletableMergeStatusModel.delete() on pending objects
# ---------------------------------------------------------------------------


class TestSoftDeleteOnPendingObjects:
    def test_soft_delete_pending_household_sets_flags(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )

        result = hh.delete(soft=True)

        hh.refresh_from_db()
        assert hh.is_removed is True
        assert hh.removed_date is not None
        assert result == (1, {hh._meta.label: 1})

    def test_soft_delete_pending_individual_sets_flags(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )

        result = ind.delete(soft=True)

        ind.refresh_from_db()
        assert ind.is_removed is True
        assert ind.removed_date is not None
        assert result == (1, {ind._meta.label: 1})

    def test_hard_delete_pending_household_removes_row(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        hh_id = hh.id

        hh.delete(soft=False)

        assert not Household.all_objects.filter(id=hh_id).exists()

    def test_hard_delete_pending_individual_removes_row(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind_id = ind.id

        ind.delete(soft=False)

        assert not Individual.all_objects.filter(id=ind_id).exists()

    def test_soft_deleted_pending_object_hidden_from_pending_manager(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        hh.delete(soft=True)

        assert PendingHousehold.objects.filter(id=hh.id).count() == 0
        assert PendingHousehold.all_objects.filter(id=hh.id, is_removed=True).count() == 1

    def test_soft_deleted_pending_individual_hidden_from_pending_manager(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind.delete(soft=True)

        assert PendingIndividual.objects.filter(id=ind.id).count() == 0
        assert PendingIndividual.all_objects.filter(id=ind.id, is_removed=True).count() == 1


# ---------------------------------------------------------------------------
# 3. PendingHousehold individuals / individuals_and_roles with data
# ---------------------------------------------------------------------------


class TestPendingHouseholdDataAccessors:
    def test_individuals_returns_only_pending_members(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        merged_hh = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_ind = IndividualFactory(
            household=merged_hh,
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )

        result = pending_hh.individuals

        assert pending_ind in result
        assert merged_ind not in result

    def test_individuals_and_roles_returns_only_pending_roles(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        pending_role = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=pending_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        merged_hh = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_ind = IndividualFactory(
            household=merged_hh,
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_role = IndividualRoleInHouseholdFactory(
            household=merged_hh,
            individual=merged_ind,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        result = pending_hh.individuals_and_roles

        assert pending_role in result
        assert merged_role not in result

    def test_pending_representatives_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=pending_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        result = pending_hh.pending_representatives

        assert pending_ind in result


# ---------------------------------------------------------------------------
# 4. PendingHousehold primary_collector / alternate_collector
# ---------------------------------------------------------------------------


class TestPendingHouseholdCollectors:
    def test_primary_collector_returns_correct_individual(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            create_role=False,
        )
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        assert hh.primary_collector == ind

    def test_primary_collector_none_when_no_primary_role(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            create_role=False,
        )

        with pytest.raises(Individual.DoesNotExist):
            _ = hh.primary_collector

    def test_alternate_collector_returns_correct_individual(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            create_role=False,
        )
        alt = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=alt,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        assert hh.alternate_collector == alt

    def test_alternate_collector_none_when_no_alternate_role(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            create_role=False,
        )

        assert hh.alternate_collector is None


# ---------------------------------------------------------------------------
# 5. Proxy model isolation
# ---------------------------------------------------------------------------


class TestPendingDocumentProxyModel:
    def test_pending_document_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pd = PendingDocumentFactory(individual=pending_ind, program=rdi.program)
        md = DocumentFactory(individual=merged_ind, program=rdi.program)

        assert PendingDocument.objects.count() >= 1
        assert pd in PendingDocument.objects.all()
        assert md not in PendingDocument.objects.all()

    def test_pending_document_has_pending_merge_status(self, rdi: RegistrationDataImport) -> None:
        pd = PendingDocumentFactory(program=rdi.program)
        assert pd.rdi_merge_status == MergeStatusModel.PENDING

    def test_document_manager_includes_all_statuses(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pd = PendingDocumentFactory(individual=ind, program=rdi.program)

        assert pd in Document.all_objects.all()


class TestPendingIndividualIdentityProxyModel:
    def test_pending_identity_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pi = IndividualIdentity.objects.create(
            individual=pending_ind,
            number="PID-001",
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        mi = IndividualIdentity.objects.create(
            individual=merged_ind,
            number="MID-001",
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        assert pi in PendingIndividualIdentity.objects.all()
        assert mi not in PendingIndividualIdentity.objects.all()

    def test_pending_identity_in_all_objects(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pi = IndividualIdentity.objects.create(
            individual=ind,
            number="PID-002",
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        assert pi in IndividualIdentity.all_objects.all()


class TestPendingIndividualRoleInHouseholdProxyModel:
    def test_pending_role_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        merged_hh = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_ind = IndividualFactory(
            household=merged_hh,
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pr = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=pending_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        mr = IndividualRoleInHouseholdFactory(
            household=merged_hh,
            individual=merged_ind,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        assert pr in PendingIndividualRoleInHousehold.objects.all()
        assert mr not in PendingIndividualRoleInHousehold.objects.all()

    def test_pending_role_in_all_objects(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        pr = IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        assert pr in IndividualRoleInHousehold.all_objects.all()


class TestPendingAccountProxyModel:
    def test_pending_account_manager_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        acct_type = AccountTypeFactory()
        pa = AccountFactory(
            individual=pending_ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        ma = AccountFactory(
            individual=merged_ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        assert pa in PendingAccount.objects.all()
        assert ma not in PendingAccount.objects.all()

    def test_pending_account_in_all_objects(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        acct_type = AccountTypeFactory()
        pa = AccountFactory(
            individual=ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        assert pa in Account.all_objects.all()


# ---------------------------------------------------------------------------
# 5b. Soft delete on additional proxy model types
# ---------------------------------------------------------------------------


class TestSoftDeleteOnAdditionalPendingObjects:
    def test_soft_delete_pending_document_sets_flags(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        doc = PendingDocumentFactory(individual=ind, program=rdi.program)

        result = doc.delete(soft=True)

        doc.refresh_from_db()
        assert doc.is_removed is True
        assert doc.removed_date is not None
        assert result == (1, {doc._meta.label: 1})

    def test_hard_delete_pending_document_removes_row(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        doc = PendingDocumentFactory(individual=ind, program=rdi.program)
        doc_id = doc.id

        doc.delete(soft=False)

        assert not Document.all_objects.filter(id=doc_id).exists()

    def test_soft_delete_pending_account_sets_flags(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        acct_type = AccountTypeFactory()
        acct = AccountFactory(
            individual=ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        result = acct.delete(soft=True)

        acct.refresh_from_db()
        assert acct.is_removed is True
        assert acct.removed_date is not None
        assert result == (1, {acct._meta.label: 1})

    def test_hard_delete_pending_account_removes_row(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        acct_type = AccountTypeFactory()
        acct = AccountFactory(
            individual=ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        acct_id = acct.id

        acct.delete(soft=False)

        assert not Account.all_objects.filter(id=acct_id).exists()

    def test_soft_delete_pending_identity_sets_flags(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        identity = IndividualIdentity.objects.create(
            individual=ind,
            number="PID-DEL",
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        result = identity.delete(soft=True)

        identity.refresh_from_db()
        assert identity.is_removed is True
        assert identity.removed_date is not None
        assert result == (1, {identity._meta.label: 1})

    def test_hard_delete_pending_identity_removes_row(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        identity = IndividualIdentity.objects.create(
            individual=ind,
            number="PID-HARD",
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        identity_id = identity.id

        identity.delete(soft=False)

        assert not IndividualIdentity.all_objects.filter(id=identity_id).exists()

    def test_soft_delete_pending_role_sets_flags(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        role = IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        result = role.delete(soft=True)

        role.refresh_from_db()
        assert role.is_removed is True
        assert role.removed_date is not None
        assert result == (1, {role._meta.label: 1})

    def test_hard_delete_pending_role_removes_row(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        role = IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        role_id = role.id

        role.delete(soft=False)

        assert not IndividualRoleInHousehold.all_objects.filter(id=role_id).exists()

    def test_soft_deleted_pending_document_hidden_from_manager(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        doc = PendingDocumentFactory(individual=ind, program=rdi.program)
        doc.delete(soft=True)

        assert PendingDocument.objects.filter(id=doc.id).count() == 0
        assert PendingDocument.all_objects.filter(id=doc.id, is_removed=True).count() == 1

    def test_soft_deleted_pending_account_hidden_from_manager(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        acct_type = AccountTypeFactory()
        acct = AccountFactory(
            individual=ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        acct.delete(soft=True)

        assert PendingAccount.objects.filter(id=acct.id).count() == 0
        assert PendingAccount.all_objects.filter(id=acct.id, is_removed=True).count() == 1

    def test_soft_deleted_pending_identity_hidden_from_manager(self, rdi: RegistrationDataImport) -> None:
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        identity = IndividualIdentity.objects.create(
            individual=ind,
            number="PID-HIDDEN",
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        identity.delete(soft=True)

        assert PendingIndividualIdentity.objects.filter(id=identity.id).count() == 0
        assert PendingIndividualIdentity.all_objects.filter(id=identity.id, is_removed=True).count() == 1

    def test_soft_deleted_pending_role_hidden_from_manager(self, rdi: RegistrationDataImport) -> None:
        hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh,
        )
        role = IndividualRoleInHousehold.objects.create(
            household=hh,
            individual=ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        role.delete(soft=True)

        assert PendingIndividualRoleInHousehold.objects.filter(id=role.id).count() == 0
        assert PendingIndividualRoleInHousehold.all_objects.filter(id=role.id, is_removed=True).count() == 1


# ---------------------------------------------------------------------------
# 5c. available_objects and all_merge_status_objects managers
# ---------------------------------------------------------------------------


class TestManagerVariants:
    def test_available_objects_returns_merged_not_removed(self, rdi: RegistrationDataImport) -> None:
        merged = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pending = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        deleted = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        deleted.delete(soft=True)

        qs = Household.available_objects.all()
        assert merged in qs
        assert pending not in qs
        assert deleted not in qs

    def test_all_merge_status_objects_returns_pending_and_merged(self, rdi: RegistrationDataImport) -> None:
        merged = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        pending = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        deleted = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        deleted.delete(soft=True)

        qs = Household.all_merge_status_objects.all()
        assert merged in qs
        assert pending in qs
        assert deleted not in qs


# ---------------------------------------------------------------------------
# 5d. PendingIndividual property accessors
# ---------------------------------------------------------------------------


class TestPendingIndividualProperties:
    def test_households_and_roles_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        pending_role = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=pending_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        merged_hh = HouseholdFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_ind = IndividualFactory(
            household=merged_hh,
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_role = IndividualRoleInHouseholdFactory(
            household=merged_hh,
            individual=merged_ind,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        result = pending_ind.households_and_roles
        assert pending_role in result
        assert merged_role not in result

    def test_documents_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_doc = PendingDocumentFactory(individual=pending_ind, program=rdi.program)
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_doc = DocumentFactory(individual=merged_ind, program=rdi.program)

        result = pending_ind.documents
        assert pending_doc in result
        assert merged_doc not in result

    def test_identities_returns_only_pending(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_id = IndividualIdentity.objects.create(
            individual=pending_ind,
            number="PID-PROP",
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        merged_ind = IndividualFactory(
            business_area=rdi.business_area,
            program=rdi.program,
            registration_data_import=rdi,
        )
        merged_id = IndividualIdentity.objects.create(
            individual=merged_ind,
            number="MID-PROP",
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        result = pending_ind.identities
        assert pending_id in result
        assert merged_id not in result

    def test_pending_household_returns_pending_proxy(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )

        result = pending_ind.pending_household
        assert isinstance(result, PendingHousehold)
        assert result.pk == pending_hh.pk

    def test_setters_are_noop(self, rdi: RegistrationDataImport) -> None:
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind.households_and_roles = "ignored"
        pending_ind.documents = "ignored"
        pending_ind.identities = "ignored"


# ---------------------------------------------------------------------------
# 6. _update_merge_statuses for all pending model types
# ---------------------------------------------------------------------------


class TestUpdateMergeStatuses:
    def test_updates_accounts_to_merged(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        acct_type = AccountTypeFactory()
        account = AccountFactory(
            individual=pending_ind,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [pending_ind.id])

        account.refresh_from_db()
        assert account.rdi_merge_status == MergeStatusModel.MERGED

    def test_updates_roles_to_merged(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        role = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=pending_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [pending_ind.id])

        role.refresh_from_db()
        assert role.rdi_merge_status == MergeStatusModel.MERGED

    def test_updates_documents_to_merged(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        doc = PendingDocumentFactory(individual=pending_ind, program=rdi.program)

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [pending_ind.id])

        doc.refresh_from_db()
        assert doc.rdi_merge_status == MergeStatusModel.MERGED

    def test_updates_households_to_merged_with_timestamp(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [pending_ind.id])

        pending_hh.refresh_from_db()
        assert pending_hh.rdi_merge_status == MergeStatusModel.MERGED
        assert pending_hh.updated_at is not None

    def test_updates_individuals_to_merged_with_timestamp(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        pending_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [pending_ind.id])

        pending_ind.refresh_from_db()
        assert pending_ind.rdi_merge_status == MergeStatusModel.MERGED
        assert pending_ind.updated_at is not None

    def test_updates_all_role_types_to_merged(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        primary_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        alternate_ind = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        primary_role = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=primary_ind,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        alternate_role = IndividualRoleInHousehold.objects.create(
            household=pending_hh,
            individual=alternate_ind,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [primary_ind.id, alternate_ind.id])

        primary_role.refresh_from_db()
        alternate_role.refresh_from_db()
        assert primary_role.rdi_merge_status == MergeStatusModel.MERGED
        assert alternate_role.rdi_merge_status == MergeStatusModel.MERGED

    def test_updates_households_excludes_unlisted_ids(self, rdi: RegistrationDataImport) -> None:
        hh_a = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        hh_b = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind_a = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh_a,
        )
        ind_b = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=hh_b,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([hh_a.id], [ind_a.id])

        hh_a.refresh_from_db()
        hh_b.refresh_from_db()
        ind_a.refresh_from_db()
        ind_b.refresh_from_db()
        assert hh_a.rdi_merge_status == MergeStatusModel.MERGED
        assert hh_b.rdi_merge_status == MergeStatusModel.PENDING
        assert ind_a.rdi_merge_status == MergeStatusModel.MERGED
        assert ind_b.rdi_merge_status == MergeStatusModel.PENDING

    def test_updates_documents_across_multiple_individuals(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind1 = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        ind2 = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        doc1 = PendingDocumentFactory(individual=ind1, program=rdi.program)
        doc2 = PendingDocumentFactory(individual=ind2, program=rdi.program)

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [ind1.id, ind2.id])

        doc1.refresh_from_db()
        doc2.refresh_from_db()
        assert doc1.rdi_merge_status == MergeStatusModel.MERGED
        assert doc2.rdi_merge_status == MergeStatusModel.MERGED

    def test_updates_accounts_across_multiple_individuals(self, rdi: RegistrationDataImport) -> None:
        pending_hh = PendingHouseholdFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
        )
        ind1 = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        ind2 = PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=rdi.business_area,
            household=pending_hh,
        )
        acct_type = AccountTypeFactory()
        acct1 = AccountFactory(
            individual=ind1,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )
        acct2 = AccountFactory(
            individual=ind2,
            account_type=acct_type,
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        task = RdiMergeTask()
        task._update_merge_statuses([pending_hh.id], [ind1.id, ind2.id])

        acct1.refresh_from_db()
        acct2.refresh_from_db()
        assert acct1.rdi_merge_status == MergeStatusModel.MERGED
        assert acct2.rdi_merge_status == MergeStatusModel.MERGED
