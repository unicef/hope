import json
from datetime import datetime
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

from django import forms
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase, tag
from django.utils import timezone

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType, FileTemp
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    LOT_DIFFICULTY,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fields import DynamicChoiceArrayField, DynamicChoiceField
from hct_mis_api.apps.payment.fixtures import (
    AccountFactory,
    ApprovalFactory,
    ApprovalProcessFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    Account,
    AccountType,
    Approval,
    DeliveryMechanism,
    DeliveryMechanismConfig,
    FinancialInstitution,
    FinancialServiceProviderXlsxTemplate,
    FspNameMapping,
    Payment,
    PaymentPlan,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.program.fixtures import BeneficiaryGroupFactory, ProgramFactory
from hct_mis_api.apps.program.models import ProgramCycle
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
)

pytestmark = pytest.mark.django_db


class TestBasePaymentPlanModel:
    def test_get_last_approval_process_data_in_approval(self, afghanistan: BusinessAreaFactory) -> None:
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_APPROVAL)
        approval_user = UserFactory()
        approval_date = timezone.datetime(2000, 10, 10, tzinfo=timezone.utc)
        ApprovalProcessFactory(
            payment_plan=payment_plan,
            sent_for_approval_date=approval_date,
            sent_for_approval_by=approval_user,
        )
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_date
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_in_authorization(self, afghanistan: BusinessAreaFactory) -> None:
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_AUTHORIZATION)
        approval_user = UserFactory()
        approval_process = ApprovalProcessFactory(
            payment_plan=payment_plan,
        )
        ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
        approval_approval2 = ApprovalFactory(
            type=Approval.APPROVAL, approval_process=approval_process, created_by=approval_user
        )
        ApprovalFactory(type=Approval.AUTHORIZATION, approval_process=approval_process)
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_approval2.created_at
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_in_review(self, afghanistan: BusinessAreaFactory) -> None:
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_REVIEW)
        approval_user = UserFactory()
        approval_process = ApprovalProcessFactory(
            payment_plan=payment_plan,
        )
        ApprovalFactory(type=Approval.AUTHORIZATION, approval_process=approval_process)
        approval_authorization2 = ApprovalFactory(
            type=Approval.AUTHORIZATION, approval_process=approval_process, created_by=approval_user
        )
        ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_authorization2.created_at
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_no_approval_process(self, afghanistan: BusinessAreaFactory) -> None:
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_REVIEW)

        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == payment_plan.updated_at
        assert modified_data.modified_by is None

    @pytest.mark.parametrize(
        "status",
        [
            PaymentPlan.Status.FINISHED,
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.Status.DRAFT,
            PaymentPlan.Status.OPEN,
            PaymentPlan.Status.LOCKED,
            PaymentPlan.Status.LOCKED_FSP,
        ],
    )
    def test_get_last_approval_process_data_other_status(self, afghanistan: BusinessAreaFactory, status: str) -> None:
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=status)
        approval_user = UserFactory()
        approval_date = timezone.datetime(2000, 10, 10, tzinfo=timezone.utc)
        ApprovalProcessFactory(
            payment_plan=payment_plan,
            sent_for_approval_date=approval_date,
            sent_for_approval_by=approval_user,
        )
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == payment_plan.updated_at
        assert modified_data.modified_by is None


class TestPaymentPlanModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()

    def test_create(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        self.assertIsInstance(pp, PaymentPlan)

    def test_update_population_count_fields(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        PaymentFactory(parent=pp, household=hh1, head_of_household=hoh1, currency="PLN")
        PaymentFactory(parent=pp, household=hh2, head_of_household=hoh2, currency="PLN")

        IndividualFactory(
            household=hh1,
            sex="FEMALE",
            birth_date=datetime.now().date() - relativedelta(years=5),
        )
        IndividualFactory(
            household=hh1,
            sex="MALE",
            birth_date=datetime.now().date() - relativedelta(years=5),
        )
        IndividualFactory(
            household=hh2,
            sex="FEMALE",
            birth_date=datetime.now().date() - relativedelta(years=20),
        )
        IndividualFactory(
            household=hh2,
            sex="MALE",
            birth_date=datetime.now().date() - relativedelta(years=20),
        )

        pp.update_population_count_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.female_children_count, 1)
        self.assertEqual(pp.male_children_count, 1)
        self.assertEqual(pp.female_adults_count, 1)
        self.assertEqual(pp.male_adults_count, 1)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)

    @patch(
        "hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate",
        return_value=2.0,
    )
    def test_update_money_fields(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory()
        PaymentFactory(
            parent=pp,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
        )
        PaymentFactory(
            parent=pp,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
        )

        pp.update_money_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.exchange_rate, 2.0)
        self.assertEqual(pp.total_entitled_quantity, 200.00)
        self.assertEqual(pp.total_entitled_quantity_usd, 400.00)
        self.assertEqual(pp.total_delivered_quantity, 100.00)
        self.assertEqual(pp.total_delivered_quantity_usd, 200.00)
        self.assertEqual(pp.total_undelivered_quantity, 100.00)
        self.assertEqual(pp.total_undelivered_quantity_usd, 200.00)

    def test_not_excluded_payments(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        PaymentFactory(parent=pp, conflicted=False, currency="PLN")
        PaymentFactory(parent=pp, conflicted=True, currency="PLN")

        pp.refresh_from_db()
        self.assertEqual(pp.eligible_payments.count(), 1)

    def test_can_be_locked(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program_cycle=program_cycle, created_by=self.user)
        self.assertEqual(pp1.can_be_locked, False)

        # create hard conflicted payment
        pp1_conflicted = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED,
            program_cycle=program_cycle,
            created_by=self.user,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        PaymentFactory(
            parent=pp1_conflicted,
            household=p1.household,
            conflicted=False,
            currency="PLN",
        )
        self.assertEqual(pp1.payment_items.filter(payment_plan_hard_conflicted=True).count(), 1)
        self.assertEqual(pp1.can_be_locked, False)

        # create not conflicted payment
        PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        self.assertEqual(pp1.can_be_locked, True)

    def test_is_population_finalized(self) -> None:
        payment_plan = PaymentPlanFactory(created_by=self.user, status=PaymentPlan.Status.TP_PROCESSING)
        self.assertTrue(payment_plan.is_population_finalized())

    def test_get_exchange_rate_for_usdc_currency(self) -> None:
        pp = PaymentPlanFactory(currency=USDC, created_by=self.user)
        self.assertEqual(pp.get_exchange_rate(), 1.0)

    def test_is_reconciled(self) -> None:
        pp = PaymentPlanFactory(currency=USDC, created_by=self.user)
        self.assertEqual(pp.is_reconciled, False)

        PaymentFactory(parent=pp, currency="PLN", excluded=True)
        self.assertEqual(pp.is_reconciled, False)

        PaymentFactory(parent=pp, currency="PLN", conflicted=True)
        self.assertEqual(pp.is_reconciled, False)

        p1 = PaymentFactory(parent=pp, currency="PLN", status=Payment.STATUS_PENDING)
        self.assertEqual(pp.is_reconciled, False)

        p2 = PaymentFactory(parent=pp, currency="PLN", status=Payment.STATUS_SENT_TO_PG)
        self.assertEqual(pp.is_reconciled, False)

        p1.status = Payment.STATUS_SENT_TO_FSP
        p1.save()
        self.assertEqual(pp.is_reconciled, False)

        p1.status = Payment.STATUS_DISTRIBUTION_SUCCESS
        p1.save()
        self.assertEqual(pp.is_reconciled, False)

        p2.status = Payment.STATUS_SENT_TO_FSP
        p2.save()
        self.assertEqual(pp.is_reconciled, False)

        p2.status = Payment.STATUS_DISTRIBUTION_PARTIAL
        p2.save()
        self.assertEqual(pp.is_reconciled, True)

    def test_save_pp_steficon_rule_validation(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, version=11)
        rule_for_pp = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, version=22)

        self.assertIsNone(pp.steficon_rule_targeting_id)
        self.assertIsNone(pp.steficon_rule_id)

        with self.assertRaisesMessage(
            ValidationError, f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_PAYMENT_PLAN}."
        ):
            pp.steficon_rule = rule_for_tp
            pp.save()

        with self.assertRaisesMessage(
            ValidationError, f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_TARGETING}."
        ):
            pp.steficon_rule_targeting = rule_for_pp
            pp.save()

    def test_payment_plan_exclude_hh_property(self) -> None:
        ind = IndividualFactory(household=None)
        hh = HouseholdFactory(head_of_household=ind)
        pp: PaymentPlan = PaymentPlanFactory(created_by=self.user)
        pp.excluded_ids = f"{hh.unicef_id},{ind.unicef_id}"
        pp.save(update_fields=["excluded_ids"])
        pp.refresh_from_db()

        self.assertEqual(pp.excluded_household_ids_targeting_level, [hh.unicef_id])

    def test_payment_plan_has_empty_criteria_property(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(created_by=self.user)
        self.assertTrue(pp.has_empty_criteria)

    def test_payment_plan_has_empty_ids_criteria_property(self) -> None:
        targeting_criteria = TargetingCriteriaFactory()
        pp: PaymentPlan = PaymentPlanFactory(targeting_criteria=targeting_criteria, created_by=self.user)

        self.assertTrue(pp.has_empty_ids_criteria)

    def test_remove_export_file_entitlement(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user, status=PaymentPlan.Status.LOCKED)
        file_temp = FileTemp.objects.create(
            object_id=pp.pk,
            content_type=get_content_type_for_model(pp),
            created=timezone.now(),
            file=ContentFile(b"abc", "Test_123.xlsx"),
        )
        pp.export_file_entitlement = file_temp
        pp.save()
        pp.refresh_from_db()
        self.assertTrue(pp.has_export_file)
        self.assertEqual(pp.export_file_entitlement.pk, file_temp.pk)

        pp.remove_export_file_entitlement()
        pp.save()
        pp.refresh_from_db()
        self.assertFalse(pp.has_export_file)
        self.assertIsNone(pp.export_file_entitlement)

    def test_remove_imported_file(self) -> None:
        pp = PaymentPlanFactory(
            created_by=self.user, status=PaymentPlan.Status.LOCKED, imported_file_date=timezone.now()
        )
        file_temp = FileTemp.objects.create(
            object_id=pp.pk,
            content_type=get_content_type_for_model(pp),
            created=timezone.now(),
            file=ContentFile(b"abc", "Test_777.xlsx"),
        )
        pp.imported_file = file_temp
        pp.save()
        pp.refresh_from_db()
        self.assertEqual(pp.imported_file.pk, file_temp.pk)
        self.assertEqual(pp.imported_file_name, "Test_777.xlsx")

        pp.remove_imported_file()
        pp.save()
        pp.refresh_from_db()
        self.assertEqual(pp.imported_file_name, "")
        self.assertIsNone(pp.imported_file)
        self.assertIsNone(pp.imported_file_date)

    def test_has_empty_ids_criteria(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        TargetingCriteriaRuleFactory(
            targeting_criteria=pp.targeting_criteria,
            household_ids="HH-1, HH-2",
            individual_ids="IND-01, IND-02",
        )
        self.assertFalse(pp.has_empty_ids_criteria)


class TestPaymentModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(created_by=cls.user)

    def test_create(self) -> None:
        p1 = PaymentFactory()
        self.assertIsInstance(p1, Payment)

    def test_unique_together(self) -> None:
        pp = PaymentPlanFactory(created_by=self.user)
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1, currency="PLN")
        with self.assertRaises(IntegrityError):
            PaymentFactory(parent=pp, household=hh1, currency="PLN")

    def test_payment_status_property(self) -> None:
        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_PENDING)
        self.assertEqual(payment.payment_status, "Pending")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
        self.assertEqual(payment.payment_status, "Delivered Fully")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_SUCCESS)
        self.assertEqual(payment.payment_status, "Delivered Fully")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_DISTRIBUTION_PARTIAL)
        self.assertEqual(payment.payment_status, "Delivered Partially")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_NOT_DISTRIBUTED)
        self.assertEqual(payment.payment_status, "Not Delivered")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_ERROR)
        self.assertEqual(payment.payment_status, "Unsuccessful")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_FORCE_FAILED)
        self.assertEqual(payment.payment_status, "Force Failed")

        payment = PaymentFactory(parent=self.pp, status=Payment.STATUS_MANUALLY_CANCELLED)
        self.assertEqual(payment.payment_status, "-")

    def test_mark_as_failed(self) -> None:
        payment_invalid_status = PaymentFactory(parent=self.pp, status=Payment.STATUS_FORCE_FAILED)
        payment = PaymentFactory(
            parent=self.pp,
            entitlement_quantity=999,
            delivered_quantity=111,
            delivered_quantity_usd=22,
            status=Payment.STATUS_DISTRIBUTION_PARTIAL,
        )
        with self.assertRaises(ValidationError) as e:
            payment_invalid_status.mark_as_failed()
        self.assertIn("Status shouldn't be failed", e.exception)

        payment.mark_as_failed()
        payment.save()
        payment.refresh_from_db()
        self.assertEqual(payment.delivered_quantity, 0)
        self.assertEqual(payment.delivered_quantity_usd, 0)
        self.assertIsNone(payment.delivery_date)
        self.assertEqual(payment.status, Payment.STATUS_FORCE_FAILED)

    def test_revert_mark_as_failed(self) -> None:
        payment_entitlement_quantity_none = PaymentFactory(
            parent=self.pp,
            entitlement_quantity=None,
            entitlement_quantity_usd=None,
            delivered_quantity=None,
            delivered_quantity_usd=None,
            status=Payment.STATUS_FORCE_FAILED,
        )
        payment_invalid_status = PaymentFactory(parent=self.pp, entitlement_quantity=999, status=Payment.STATUS_PENDING)
        payment = PaymentFactory(
            parent=self.pp, entitlement_quantity=999, delivered_quantity=111, status=Payment.STATUS_FORCE_FAILED
        )
        date = timezone.now().date()

        with self.assertRaises(ValidationError) as e:
            payment_invalid_status.revert_mark_as_failed(999, date)
        self.assertIn("Only payment marked as force failed can be reverted", e.exception)

        with self.assertRaises(ValidationError) as e:
            payment_entitlement_quantity_none.revert_mark_as_failed(999, date)
        self.assertIn("Entitlement quantity need to be set in order to revert", e.exception)

        payment.revert_mark_as_failed(999, date)
        payment.save()
        payment.refresh_from_db()
        self.assertEqual(payment.delivered_quantity, 999)
        self.assertEqual(payment.delivery_date.date(), date)
        self.assertEqual(payment.status, Payment.STATUS_DISTRIBUTION_SUCCESS)

    def test_get_revert_mark_as_failed_status(self) -> None:
        payment = PaymentFactory(parent=self.pp, entitlement_quantity=999)
        delivered_quantity_with_status = (
            (0, Payment.STATUS_NOT_DISTRIBUTED),
            (100, Payment.STATUS_DISTRIBUTION_PARTIAL),
            (999, Payment.STATUS_DISTRIBUTION_SUCCESS),
        )
        for delivered_quantity, status in delivered_quantity_with_status:
            result_status = payment.get_revert_mark_as_failed_status(delivered_quantity)
            self.assertEqual(result_status, status)

        with self.assertRaises(ValidationError) as e:
            payment.get_revert_mark_as_failed_status(1000)
        self.assertIn("Wrong delivered quantity 1000 for entitlement quantity 999", e.exception)

    def test_manager_annotations_pp_conflicts(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program_cycle=program_cycle, created_by=self.user)

        # create hard conflicted payment
        pp2 = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED, program_cycle=program_cycle, created_by=self.user)
        # create soft conflicted payments
        pp3 = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, program_cycle=program_cycle, created_by=self.user)
        pp4 = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program_cycle=program_cycle,
            created_by=self.user,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        p2 = PaymentFactory(parent=pp2, household=p1.household, conflicted=False, currency="PLN")
        p3 = PaymentFactory(parent=pp3, household=p1.household, conflicted=False, currency="PLN")
        p4 = PaymentFactory(parent=pp4, household=p1.household, conflicted=False, currency="PLN")

        for obj in [pp1, pp2, pp3, pp4, p1, p2, p3, p4]:
            obj.refresh_from_db()  # update unicef_id from trigger

        p1_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(p1_data["payment_plan_hard_conflicted"], True)
        self.assertEqual(p1_data["payment_plan_soft_conflicted"], True)

        self.assertEqual(len(p1_data["payment_plan_hard_conflicted_data"]), 1)
        self.assertEqual(
            json.loads(p1_data["payment_plan_hard_conflicted_data"][0]),
            {
                "payment_id": str(p2.id),
                "payment_plan_id": str(pp2.id),
                "payment_plan_status": str(pp2.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                "payment_plan_unicef_id": str(pp2.unicef_id),
                "payment_unicef_id": str(p2.unicef_id),
            },
        )
        self.assertEqual(len(p1_data["payment_plan_soft_conflicted_data"]), 2)
        self.assertCountEqual(
            [json.loads(conflict_data) for conflict_data in p1_data["payment_plan_soft_conflicted_data"]],
            [
                {
                    "payment_id": str(p3.id),
                    "payment_plan_id": str(pp3.id),
                    "payment_plan_status": str(pp3.status),
                    "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp3.unicef_id),
                    "payment_unicef_id": str(p3.unicef_id),
                },
                {
                    "payment_id": str(p4.id),
                    "payment_plan_id": str(pp4.id),
                    "payment_plan_status": str(pp4.status),
                    "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp4.unicef_id),
                    "payment_unicef_id": str(p4.unicef_id),
                },
            ],
        )

        # the same conflicts when Cycle without end date
        program_cycle = program.cycles.first()
        ProgramCycle.objects.filter(pk=program_cycle.id).update(end_date=None)
        program_cycle.refresh_from_db()
        self.assertIsNone(program_cycle.end_date)

        payment_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(payment_data["payment_plan_hard_conflicted"], True)
        self.assertEqual(payment_data["payment_plan_soft_conflicted"], True)

        self.assertEqual(len(payment_data["payment_plan_hard_conflicted_data"]), 1)
        self.assertEqual(
            json.loads(payment_data["payment_plan_hard_conflicted_data"][0]),
            {
                "payment_id": str(p2.id),
                "payment_plan_id": str(pp2.id),
                "payment_plan_status": str(pp2.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": None,
                "payment_plan_unicef_id": str(pp2.unicef_id),
                "payment_unicef_id": str(p2.unicef_id),
            },
        )
        self.assertEqual(len(payment_data["payment_plan_soft_conflicted_data"]), 2)
        self.assertCountEqual(
            [json.loads(conflict_data) for conflict_data in payment_data["payment_plan_soft_conflicted_data"]],
            [
                {
                    "payment_id": str(p3.id),
                    "payment_plan_id": str(pp3.id),
                    "payment_plan_status": str(pp3.status),
                    "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": None,
                    "payment_plan_unicef_id": str(pp3.unicef_id),
                    "payment_unicef_id": str(p3.unicef_id),
                },
                {
                    "payment_id": str(p4.id),
                    "payment_plan_id": str(pp4.id),
                    "payment_plan_status": str(pp4.status),
                    "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": None,
                    "payment_plan_unicef_id": str(pp4.unicef_id),
                    "payment_unicef_id": str(p4.unicef_id),
                },
            ],
        )

    def test_manager_annotations_pp_no_conflicts_for_follow_up(self) -> None:
        rdi = RegistrationDataImportFactory(business_area=self.business_area)
        program = RealProgramFactory(business_area=self.business_area)
        program_cycle = program.cycles.first()
        pp1 = PaymentPlanFactory(
            program_cycle=program_cycle,
            business_area=self.business_area,
            status=PaymentPlan.Status.OPEN,
            created_by=self.user,
        )
        # create follow up pp
        pp2 = PaymentPlanFactory(
            business_area=self.business_area,
            status=PaymentPlan.Status.LOCKED,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
            created_by=self.user,
        )
        pp3 = PaymentPlanFactory(
            business_area=self.business_area,
            status=PaymentPlan.Status.OPEN,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
            created_by=self.user,
        )
        p1 = PaymentFactory(
            parent=pp1,
            conflicted=False,
            currency="PLN",
            household__registration_data_import=rdi,
            household__program=program,
        )
        p2 = PaymentFactory(
            parent=pp2,
            household=p1.household,
            conflicted=False,
            is_follow_up=True,
            source_payment=p1,
            currency="PLN",
        )
        p3 = PaymentFactory(
            parent=pp3,
            household=p1.household,
            conflicted=False,
            is_follow_up=True,
            source_payment=p1,
            currency="PLN",
        )

        for _ in [pp1, pp2, pp3, p1, p2, p3]:
            _.refresh_from_db()  # update unicef_id from trigger

        p2_data = Payment.objects.filter(id=p2.id).values()[0]
        self.assertEqual(p2_data["payment_plan_hard_conflicted"], False)
        self.assertEqual(p2_data["payment_plan_soft_conflicted"], True)
        p3_data = Payment.objects.filter(id=p3.id).values()[0]
        self.assertEqual(p3_data["payment_plan_hard_conflicted"], False)
        self.assertEqual(p3_data["payment_plan_soft_conflicted"], True)
        self.assertEqual(p2_data["payment_plan_hard_conflicted_data"], [])
        self.assertIsNotNone(p3_data["payment_plan_hard_conflicted_data"])


class TestPaymentPlanSplitModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")


class TestFinancialServiceProviderModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_fsp_template_get_column_from_core_field(self) -> None:
        household, individuals = create_household(
            {"size": 1, "business_area": self.business_area},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
                "phone_no": "+48577123654",
                "phone_no_alternative": "+48111222333",
                "wallet_name": "wallet_name_Ind_111",
                "blockchain_name": "blockchain_name_Ind_111",
                "wallet_address": "wallet_address_Ind_111",
            },
        )
        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)
        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
        area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)
        household.admin1 = area1
        household.admin2 = area2
        household.admin3 = area3
        household.country_origin = country
        household.save()

        payment = PaymentFactory(program=ProgramFactory(), household=household, collector=individuals[0])
        data_collecting_type = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
        beneficiary_group = BeneficiaryGroupFactory(name="People", master_detail=False)
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplate
        payment.parent.program.data_collecting_type = data_collecting_type
        payment.parent.program.beneficiary_group = beneficiary_group
        payment.parent.program.save()

        primary = IndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY).first().individual
        # update primary collector
        primary.household = household
        primary.phone_no = "+48577123654"
        primary.phone_no_alternative = "+48111222333"
        primary.wallet_name = "wallet_name_Ind_111"
        primary.blockchain_name = "blockchain_name_Ind_111"
        primary.wallet_address = "wallet_address_Ind_111"
        primary.save()

        document = DocumentFactory(
            individual=primary,
            type__key="national_id",
            document_number="id_doc_number_123",
        )
        generate_delivery_mechanisms()

        # get None if no snapshot
        none_resp = fsp_xlsx_template.get_column_from_core_field(payment, "given_name")
        self.assertIsNone(none_resp)

        create_payment_plan_snapshot_data(payment.parent)
        payment.refresh_from_db()

        # check invalid filed name
        result = fsp_xlsx_template.get_column_from_core_field(payment, "invalid_people_field_name")
        self.assertIsNone(result)

        # People program
        given_name = fsp_xlsx_template.get_column_from_core_field(payment, "given_name")
        self.assertEqual(given_name, primary.given_name)
        ind_unicef_id = fsp_xlsx_template.get_column_from_core_field(payment, "individual_unicef_id")
        self.assertEqual(ind_unicef_id, primary.unicef_id)

        # Standard program
        payment.parent.program.data_collecting_type.type = DataCollectingType.Type.STANDARD
        payment.parent.program.data_collecting_type.save()

        # check fields value
        size = fsp_xlsx_template.get_column_from_core_field(payment, "size")
        self.assertEqual(size, 1)
        admin1 = fsp_xlsx_template.get_column_from_core_field(payment, "admin1")
        self.assertEqual(admin1, f"{area1.p_code} - {area1.name}")
        admin2 = fsp_xlsx_template.get_column_from_core_field(payment, "admin2")
        self.assertEqual(admin2, f"{area2.p_code} - {area2.name}")
        admin3 = fsp_xlsx_template.get_column_from_core_field(payment, "admin3")
        self.assertEqual(admin3, f"{area3.p_code} - {area3.name}")
        given_name = fsp_xlsx_template.get_column_from_core_field(payment, "given_name")
        self.assertEqual(given_name, primary.given_name)
        ind_unicef_id = fsp_xlsx_template.get_column_from_core_field(payment, "individual_unicef_id")
        self.assertEqual(ind_unicef_id, primary.unicef_id)
        hh_unicef_id = fsp_xlsx_template.get_column_from_core_field(payment, "household_unicef_id")
        self.assertEqual(hh_unicef_id, household.unicef_id)
        phone_no = fsp_xlsx_template.get_column_from_core_field(payment, "phone_no")
        self.assertEqual(phone_no, primary.phone_no)
        phone_no_alternative = fsp_xlsx_template.get_column_from_core_field(payment, "phone_no_alternative")
        self.assertEqual(phone_no_alternative, primary.phone_no_alternative)
        national_id_no = fsp_xlsx_template.get_column_from_core_field(payment, "national_id_no")
        self.assertEqual(national_id_no, document.document_number)
        wallet_name = fsp_xlsx_template.get_column_from_core_field(payment, "wallet_name")
        self.assertEqual(wallet_name, primary.wallet_name)
        blockchain_name = fsp_xlsx_template.get_column_from_core_field(payment, "blockchain_name")
        self.assertEqual(blockchain_name, primary.blockchain_name)
        wallet_address = fsp_xlsx_template.get_column_from_core_field(payment, "wallet_address")
        self.assertEqual(wallet_address, primary.wallet_address)

        role = fsp_xlsx_template.get_column_from_core_field(payment, "role")
        self.assertEqual(role, "PRIMARY")

        primary_collector_id = fsp_xlsx_template.get_column_from_core_field(payment, "primary_collector_id")
        self.assertEqual(primary_collector_id, str(primary.pk))

        # country_origin
        country_origin = fsp_xlsx_template.get_column_from_core_field(payment, "country_origin")
        self.assertEqual(household.country_origin.iso_code3, country_origin)


class TestDynamicChoiceArrayField(TestCase):
    def setUp(self) -> None:
        self.mock_choices = [("field1", "Field 1"), ("field2", "Field 2")]
        self.mock_choices_callable = MagicMock(return_value=self.mock_choices)

    def test_choices(self) -> None:
        field = DynamicChoiceArrayField(
            base_field=models.CharField(max_length=255),
            choices_callable=self.mock_choices_callable,
        )
        form_field = field.formfield()

        # Check if the choices_callable is passed to the form field
        self.assertEqual(list(form_field.choices), self.mock_choices)
        self.mock_choices_callable.assert_called_once()

        # Check the form field class and choices
        self.assertIsInstance(form_field, DynamicChoiceField)


class TestFinancialServiceProviderXlsxTemplate(TestCase):
    class FinancialServiceProviderXlsxTemplateForm(forms.ModelForm):
        class Meta:
            model = FinancialServiceProviderXlsxTemplate
            fields = ["core_fields"]

    def test_model_form_integration(self) -> None:
        form = self.FinancialServiceProviderXlsxTemplateForm(
            data={"core_fields": ["age", "residence_status"]}
        )  # real existing core fields
        self.assertTrue(form.is_valid())
        template = form.save()
        self.assertEqual(template.core_fields, ["age", "residence_status"])

        form = self.FinancialServiceProviderXlsxTemplateForm(data={"core_fields": ["field1"]})  # fake core fields
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {"core_fields": ["Select a valid choice. field1 is not one of the available choices."]},
        )


class TestAccountModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program1 = ProgramFactory()
        cls.user = UserFactory.create()
        cls.ind = IndividualFactory(household=None, program=cls.program1)
        cls.ind2 = IndividualFactory(household=None, program=cls.program1)
        cls.hh = HouseholdFactory(head_of_household=cls.ind)
        cls.ind.household = cls.hh
        cls.ind.save()
        cls.ind2.household = cls.hh
        cls.ind2.save()

        cls.fsp = FinancialServiceProviderFactory()
        generate_delivery_mechanisms()
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        cls.financial_institution = FinancialInstitution.objects.create(
            code="ABC", type=FinancialInstitution.FinancialInstitutionType.BANK
        )

    def test_str(self) -> None:
        dmd = AccountFactory(individual=self.ind)
        self.assertEqual(str(dmd), f"{dmd.individual} - {dmd.account_type}")

    def test_get_associated_object(self) -> None:
        dmd = AccountFactory(data={"test": "test"}, individual=self.ind)
        self.assertEqual(dmd.get_associated_object(FspNameMapping.SourceModel.ACCOUNT.value), dmd.data)
        self.assertEqual(
            dmd.get_associated_object(FspNameMapping.SourceModel.HOUSEHOLD.value), dmd.individual.household
        )
        self.assertEqual(dmd.get_associated_object(FspNameMapping.SourceModel.INDIVIDUAL.value), dmd.individual)

    def test_delivery_data(self) -> None:
        dmd = AccountFactory(
            data={
                "expiry_date": "12.12.2024",
                "name_of_cardholder": "Marek",
            },
            individual=self.ind,
            account_type=AccountType.objects.get(key="bank"),
            number="test",
            financial_institution=self.financial_institution,
        )

        fsp2 = FinancialServiceProviderFactory()  # no dm config
        self.assertEqual(
            dmd.delivery_data(fsp2, self.dm_atm_card),
            {},
        )

        dm_config = DeliveryMechanismConfig.objects.get(fsp=self.fsp, delivery_mechanism=self.dm_atm_card)
        dm_config.required_fields.extend(["custom_ind_name", "custom_hh_address", "address"])
        dm_config.save()

        FspNameMapping.objects.create(
            external_name="number", hope_name="number", source=FspNameMapping.SourceModel.ACCOUNT, fsp=self.fsp
        )
        FspNameMapping.objects.create(
            external_name="expiry_date",
            hope_name="expiry_date",
            source=FspNameMapping.SourceModel.ACCOUNT,
            fsp=self.fsp,
        )
        FspNameMapping.objects.create(
            external_name="custom_ind_name",
            hope_name="my_custom_ind_name",
            source=FspNameMapping.SourceModel.INDIVIDUAL,
            fsp=self.fsp,
        )
        FspNameMapping.objects.create(
            external_name="custom_hh_address",
            hope_name="my_custom_hh_address",
            source=FspNameMapping.SourceModel.HOUSEHOLD,
            fsp=self.fsp,
        )
        FspNameMapping.objects.create(
            external_name="address", hope_name="address", source=FspNameMapping.SourceModel.HOUSEHOLD, fsp=self.fsp
        )

        def my_custom_ind_name(self: Any) -> str:
            return f"{self.full_name} Custom"

        dmd.individual.__class__.my_custom_ind_name = property(my_custom_ind_name)

        def my_custom_hh_address(self: Any) -> str:
            return f"{self.address} Custom"

        self.hh.__class__.my_custom_hh_address = property(my_custom_hh_address)

        self.assertEqual(
            dmd.delivery_data(self.fsp, self.dm_atm_card),
            {
                "number": "test",
                "expiry_date": "12.12.2024",
                "name_of_cardholder": "Marek",
                "custom_ind_name": f"{dmd.individual.full_name} Custom",
                "custom_hh_address": f"{self.hh.address} Custom",
                "address": self.hh.address,
                "financial_institution": "ABC",
            },
        )

    def test_validate(self) -> None:
        dmd = AccountFactory(
            data={
                "number": "test",
                "expiry_date": "12.12.2024",
                "name_of_cardholder": "Marek",
            },
            individual=self.ind,
            account_type=AccountType.objects.get(key="bank"),
        )
        self.assertEqual(dmd.validate(self.fsp, self.dm_atm_card), True)

        dm_config = DeliveryMechanismConfig.objects.get(fsp=self.fsp, delivery_mechanism=self.dm_atm_card)
        dm_config.required_fields.extend(["address"])
        dm_config.save()

        FspNameMapping.objects.create(
            external_name="address", hope_name="address", source=FspNameMapping.SourceModel.HOUSEHOLD, fsp=self.fsp
        )
        self.assertEqual(dmd.validate(self.fsp, self.dm_atm_card), True)

        dm_config.required_fields.extend(["missing_field"])
        dm_config.save()

        FspNameMapping.objects.create(
            external_name="missing_field",
            hope_name="missing_field",
            source=FspNameMapping.SourceModel.INDIVIDUAL,
            fsp=self.fsp,
        )
        self.assertEqual(dmd.validate(self.fsp, self.dm_atm_card), False)

    def test_validate_uniqueness(self) -> None:
        AccountFactory(data={"name_of_cardholder": "test"}, individual=self.ind)
        Account.update_unique_field = mock.Mock()  # type: ignore
        Account.validate_uniqueness(Account.objects.all())
        Account.update_unique_field.assert_called_once()


@tag("isolated")
class TestAccountModelUniqueField(TransactionTestCase):
    def test_update_unique_fields(self) -> None:
        create_afghanistan()
        self.program1 = ProgramFactory()
        self.user = UserFactory.create()
        self.ind = IndividualFactory(household=None, program=self.program1)
        self.ind2 = IndividualFactory(household=None, program=self.program1)
        self.hh = HouseholdFactory(head_of_household=self.ind)
        self.ind.household = self.hh
        self.ind.save()
        self.ind2.household = self.hh
        self.ind2.save()

        account_type_bank, _ = AccountType.objects.update_or_create(
            key="bank",
            label="Bank",
            defaults=dict(
                unique_fields=[
                    "number",
                    "seeing_disability",
                    "name_of_cardholder__atm_card",
                ],
                payment_gateway_id="123",
            ),
        )

        dmd_1 = AccountFactory(
            data={"name_of_cardholder__atm_card": "test"},
            individual=self.ind,
            account_type=account_type_bank,
            number="123",
        )
        dmd_1.individual.seeing_disability = LOT_DIFFICULTY
        dmd_1.individual.save()
        self.assertIsNone(dmd_1.unique_key)
        self.assertEqual(dmd_1.is_unique, True)

        dmd_2 = AccountFactory(
            data={"name_of_cardholder__atm_card": "test2"},
            individual=self.ind2,
            account_type=account_type_bank,
            number="123",
        )
        dmd_2.individual.seeing_disability = LOT_DIFFICULTY
        dmd_2.individual.save()
        self.assertIsNone(dmd_2.unique_key)
        self.assertEqual(dmd_2.is_unique, True)

        with transaction.atomic():
            dmd_1.update_unique_field()
        dmd_1.refresh_from_db()
        self.assertIsNotNone(dmd_1.unique_key)
        self.assertEqual(dmd_1.is_unique, True)

        dmd_2.data = {**dmd_2.data, "name_of_cardholder__atm_card": "test"}
        dmd_2.save()
        with transaction.atomic():
            dmd_2.update_unique_field()
        dmd_2.refresh_from_db()
        self.assertIsNotNone(dmd_2.unique_key)
        self.assertEqual(dmd_2.is_unique, False)


class TestAccountTypeModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.fsp = FinancialServiceProviderFactory()
        generate_delivery_mechanisms()

    def test_get_targeting_field_names(self) -> None:
        self.assertEqual(AccountType.get_targeting_field_names(), ["bank__number", "mobile__number"])
