import json
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

from django import forms
from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.payment.fields import DynamicChoiceArrayField, DynamicChoiceField
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismDataFactory,
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    Approval,
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import ProgramCycle

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
            PaymentPlan.Status.PREPARING,
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
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self) -> None:
        pp = PaymentPlanFactory()
        self.assertIsInstance(pp, PaymentPlan)

    def test_update_population_count_fields(self) -> None:
        pp = PaymentPlanFactory()
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
        pp = PaymentPlanFactory()
        PaymentFactory(parent=pp, conflicted=False, currency="PLN")
        PaymentFactory(parent=pp, conflicted=True, currency="PLN")

        pp.refresh_from_db()
        self.assertEqual(pp.eligible_payments.count(), 1)

    def test_can_be_locked(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program=program, program_cycle=program_cycle)
        self.assertEqual(pp1.can_be_locked, False)

        # create hard conflicted payment
        pp1_conflicted = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED,
            program=program,
            program_cycle=program_cycle,
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

    def test_get_exchange_rate_for_usdc_currency(self) -> None:
        pp = PaymentPlanFactory(currency=USDC)
        self.assertEqual(pp.get_exchange_rate(), 1.0)

    def test_is_reconciled(self) -> None:
        pp = PaymentPlanFactory(currency=USDC)
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


class TestPaymentModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self) -> None:
        p1 = PaymentFactory()
        self.assertIsInstance(p1, Payment)

    def test_unique_together(self) -> None:
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1, currency="PLN")
        with self.assertRaises(IntegrityError):
            PaymentFactory(parent=pp, household=hh1, currency="PLN")

    def test_manager_annotations_pp_conflicts(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program=program, program_cycle=program_cycle)

        # create hard conflicted payment
        pp2 = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED,
            program=program,
            program_cycle=program_cycle,
        )
        # create soft conflicted payments
        pp3 = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program=program,
            program_cycle=program_cycle,
        )
        pp4 = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            program=program,
            program_cycle=program_cycle,
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
        program_cycle = RealProgramFactory().cycles.first()
        pp1 = PaymentPlanFactory(program_cycle=program_cycle)
        # create follow up pp
        pp2 = PaymentPlanFactory(
            status=PaymentPlan.Status.LOCKED,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
        )
        pp3 = PaymentPlanFactory(
            status=PaymentPlan.Status.OPEN,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
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
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_properties(self) -> None:
        pp = PaymentPlanFactory()
        dm = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=pp,
            chosen_configuration="key1",
        )
        p1 = PaymentFactory(parent=pp, currency="PLN")
        p2 = PaymentFactory(parent=pp, currency="PLN")
        pp_split1 = PaymentPlanSplitFactory(
            payment_plan=pp,
            split_type=PaymentPlanSplit.SplitType.BY_RECORDS,
            chunks_no=2,
            order=0,
        )
        pp_split1.payments.set([p1, p2])
        self.assertEqual(pp_split1.financial_service_provider, dm.financial_service_provider)
        self.assertEqual(pp_split1.chosen_configuration, dm.chosen_configuration)
        self.assertEqual(pp_split1.delivery_mechanism, dm.delivery_mechanism)


class TestFinancialServiceProviderModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_properties(self) -> None:
        fsp1 = FinancialServiceProviderFactory(
            data_transfer_configuration=[
                {"key": "key1", "label": "label1", "id": 1, "random_key": "random"},
                {"key": "key2", "label": "label2", "id": 2, "random_key": "random"},
            ],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id=123,
        )
        fsp2 = FinancialServiceProviderFactory(
            data_transfer_configuration=[
                {"key": "key1", "label": "label1", "id": 1, "random_key": "random"},
                {"key": "key2", "label": "label2", "id": 2, "random_key": "random"},
            ],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )

        self.assertEqual(fsp1.configurations, [])
        self.assertEqual(fsp2.configurations, [])

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
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplate
        payment.parent.program.data_collecting_type = data_collecting_type
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
        dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        dmd = DeliveryMechanismDataFactory(
            individual=primary,
            delivery_mechanism=dm_atm_card,
            data={
                "card_number__atm_card": "333111222",
                "card_expiry_date__atm_card": "2025-11-11",
                "name_of_cardholder__atm_card": "Just Random Test Name",
            },
        )

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
        self.assertEqual(admin1, f"{area1.p_code}")
        admin2 = fsp_xlsx_template.get_column_from_core_field(payment, "admin2")
        self.assertEqual(admin2, f"{area2.p_code}")
        admin3 = fsp_xlsx_template.get_column_from_core_field(payment, "admin3")
        self.assertEqual(admin3, f"{area3.p_code}")
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

        # get delivery_mechanisms_data field
        dmd_resp = fsp_xlsx_template.get_column_from_core_field(payment, "name_of_cardholder__atm_card", dmd)
        self.assertEqual(dmd_resp, "Just Random Test Name")

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
