from unittest.mock import Mock

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, RoleAssignment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64_required, to_choice_object
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.api.serializers import (
    ApprovalProcessSerializer,
    PaymentListSerializer,
    PaymentPlanDetailSerializer,
    PaymentPlanListSerializer,
    TPHouseholdListSerializer,
    VolumeByDeliveryMechanismSerializer,
)
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import (
    Approval,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.models.payment import (
    DeliveryMechanismPerPaymentPlan,
    Payment,
)


class TPHouseholdListSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(created_by=cls.user, business_area=cls.business_area)
        admin2 = AreaFactory(name="New admin22")
        cls.hoh = IndividualFactory(household=None)
        cls.hh1 = HouseholdFactory(admin2=admin2, head_of_household=cls.hoh, size=2)

        cls.payment = PaymentFactory(parent=cls.pp, household=cls.hh1, vulnerability_score=123.012)

    def test_serializer_all_data(self) -> None:
        serializer = TPHouseholdListSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(data["id"], encode_id_base64_required(str(self.payment.id), "Payment"))
        self.assertEqual(data["household_unicef_id"], self.hh1.unicef_id)
        self.assertEqual(data["hoh_full_name"], self.hoh.full_name)
        self.assertEqual(data["household_size"], 2)
        self.assertEqual(data["household_admin2"], "New admin22")
        self.assertEqual(data["vulnerability_score"], "123.012")

    def test_hoh_full_name_if_no_hoh(self) -> None:
        self.payment.head_of_household = None
        self.payment.save()
        serializer = TPHouseholdListSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(data["hoh_full_name"], "")


class PaymentListSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(created_by=cls.user, business_area=cls.business_area)
        cls.program = cls.pp.program_cycle.program
        admin2 = AreaFactory(name="New admin22")
        cls.hoh = IndividualFactory(household=None)
        cls.hh1 = HouseholdFactory(admin2=admin2, head_of_household=cls.hoh, size=2)
        cls.payment = PaymentFactory(
            parent=cls.pp,
            household=cls.hh1,
            vulnerability_score=123.012,
            entitlement_quantity=99,
            delivered_quantity=88,
            financial_service_provider__name="FSP 1",
            fsp_auth_code="AUTH_123",
        )

    def test_serializer_all_data(self) -> None:
        serializer = PaymentListSerializer(instance=self.payment, context={"request": Mock(user=self.user)})
        data = serializer.data

        self.assertEqual(data["id"], encode_id_base64_required(str(self.payment.id), "Payment"))
        self.assertEqual(data["unicef_id"], self.payment.unicef_id)
        self.assertEqual(data["household_unicef_id"], self.hh1.unicef_id)
        self.assertEqual(data["household_size"], 2)
        self.assertEqual(data["household_admin2"], "New admin22")
        self.assertEqual(data["entitlement_quantity"], "99.00")
        self.assertEqual(data["delivered_quantity"], "88.00")
        self.assertEqual(data["status"], self.payment.get_status_display())
        self.assertEqual(data["fsp_name"], "FSP 1")
        self.assertEqual(data["fsp_auth_code"], "")

    def test_get_auth_code(self) -> None:
        user_1 = UserFactory()
        role, created = Role.objects.update_or_create(
            name="Role with Permissions", defaults={"permissions": [Permissions.PM_VIEW_FSP_AUTH_CODE.value]}
        )
        user_role, _ = RoleAssignment.objects.get_or_create(user=user_1, role=role, business_area=self.business_area)
        serializer = PaymentListSerializer(instance=self.payment, context={"request": Mock(user=user_1)})
        data = serializer.data

        self.assertEqual(data["fsp_auth_code"], "AUTH_123")

    def test_get_snapshot_collector_full_name(self) -> None:
        household_data = {
            "primary_collector": {
                "full_name": "Name_from_Snapshot",
            },
            "alternate_collector": {},
        }
        PaymentHouseholdSnapshot.objects.create(
            payment=self.payment, snapshot_data=household_data, household_id=self.payment.household.id
        )
        serializer = PaymentListSerializer(instance=self.payment, context={"request": Mock(user=self.user)})
        data = serializer.data

        self.assertEqual(data["snapshot_collector_full_name"], "Name_from_Snapshot")


class PaymentPlanListSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(
            created_by=cls.user, business_area=cls.business_area, dispersion_start_date=None, dispersion_end_date=None
        )

    def test_created_by(self) -> None:
        serializer = PaymentPlanListSerializer(instance=self.pp)
        data = serializer.data
        self.assertEqual(data["created_by"], f"{self.user.first_name} {self.user.last_name}")


class PaymentPlanDetailSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(
            created_by=cls.user, business_area=cls.business_area, dispersion_start_date=None, dispersion_end_date=None
        )
        cls.program = cls.pp.program_cycle.program
        admin2 = AreaFactory(name="New for PP details")
        cls.hoh = IndividualFactory(household=None)
        cls.hh1 = HouseholdFactory(admin2=admin2, head_of_household=cls.hoh, size=2)
        cls.payment = PaymentFactory(
            parent=cls.pp,
            household=cls.hh1,
            vulnerability_score=999.012,
            entitlement_quantity=100,
            delivered_quantity=155,
            financial_service_provider__name="FSP ABC",
        )
        cls.fsp = cls.payment.financial_service_provider

    def test_serializer_all_data(self) -> None:
        self.pp.status = PaymentPlan.Status.ACCEPTED
        self.pp.save()
        DeliveryMechanismPerPaymentPlan.objects.create(
            payment_plan=self.pp,
            delivery_mechanism_order=1,
            financial_service_provider=self.fsp,
            delivery_mechanism=DeliveryMechanismFactory(),
        )

        serializer = PaymentPlanDetailSerializer(instance=self.pp, context={"request": Mock(user=self.user)})
        data = serializer.data

        self.assertEqual(data["id"], encode_id_base64_required(str(self.pp.id), "PaymentPlan"))
        self.assertEqual(data["reconciliation_summary"]["pending"], 1)
        self.assertEqual(data["reconciliation_summary"]["number_of_payments"], 1)
        self.assertEqual(data["excluded_households"], [])
        self.assertEqual(data["excluded_individuals"], [])
        self.assertEqual(data["fsp_communication_channel"], "XLSX")
        self.assertEqual(data["can_create_follow_up"], False)
        self.assertEqual(data["can_split"], True)
        self.assertEqual(data["can_export_xlsx"], False)
        self.assertEqual(data["can_download_xlsx"], False)
        self.assertEqual(data["can_send_xlsx_password"], False)
        self.assertEqual(data["split_choices"], to_choice_object(PaymentPlanSplit.SplitType.choices))
        self.assertIsNotNone(data.get("volume_by_delivery_mechanism"))


class ApprovalProcessSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(
            created_by=cls.user, business_area=cls.business_area, dispersion_start_date=None, dispersion_end_date=None
        )
        cls.approval_process = ApprovalProcessFactory(payment_plan=cls.pp)
        ApprovalFactory(approval_process=cls.approval_process, type=Approval.APPROVAL, created_by=None)
        ApprovalFactory(approval_process=cls.approval_process, type=Approval.REJECT, created_by=cls.user)

    def test_all_fields(self) -> None:
        user_name_str = f"{self.user.first_name} {self.user.last_name}"
        data = ApprovalProcessSerializer(instance=self.approval_process).data

        self.assertEqual(len(data["approvals"]), 2)
        reject = data["approvals"][0]
        approval = data["approvals"][1]
        self.assertEqual(reject["type"], Approval.REJECT)
        self.assertEqual(reject["created_by"], user_name_str)
        self.assertEqual(approval["type"], Approval.APPROVAL)
        self.assertEqual(approval["created_by"], "")
        # add user data
        self.approval_process.sent_for_approval_by = self.user
        self.approval_process.sent_for_authorization_by = self.user
        self.approval_process.sent_for_finance_release_by = self.user
        self.approval_process.save()
        data_with_users = ApprovalProcessSerializer(instance=self.approval_process).data
        self.assertEqual(data_with_users["sent_for_approval_by"], user_name_str)
        self.assertEqual(data_with_users["sent_for_authorization_by"], user_name_str)
        self.assertEqual(data_with_users["sent_for_finance_release_by"], user_name_str)


class VolumeByDeliveryMechanismSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.pp = PaymentPlanFactory(
            created_by=cls.user,
            business_area=cls.business_area,
            dispersion_start_date=None,
            dispersion_end_date=None,
            financial_service_provider=None,
        )
        cls.hoh = IndividualFactory(household=None)
        cls.hh1 = HouseholdFactory(head_of_household=cls.hoh, size=2)
        cls.payment = PaymentFactory(
            parent=cls.pp,
            household=cls.hh1,
            status=Payment.STATUS_SUCCESS,
            entitlement_quantity=222,
            entitlement_quantity_usd=111,
            financial_service_provider__name="FSP_TEST_1",
        )
        cls.fsp = cls.payment.financial_service_provider
        cls.dm_per_pp = DeliveryMechanismPerPaymentPlan.objects.create(
            payment_plan=cls.pp,
            delivery_mechanism_order=1,
            financial_service_provider=cls.fsp,
            delivery_mechanism=DeliveryMechanismFactory(),
        )

    def test_get_volume_fields(self) -> None:
        data = VolumeByDeliveryMechanismSerializer(instance=self.dm_per_pp).data

        self.assertEqual(data["volume"], None)
        self.assertEqual(data["volume_usd"], None)

        self.pp.financial_service_provider = self.fsp
        self.pp.save()
        data = VolumeByDeliveryMechanismSerializer(instance=self.dm_per_pp).data

        self.assertEqual(data["volume"], 222)
        self.assertEqual(data["volume_usd"], 111)
