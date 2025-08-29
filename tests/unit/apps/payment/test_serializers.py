from typing import Any, List
from unittest.mock import Mock

from django.test import TestCase

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.apps.payment.api.serializers import (
    ApprovalProcessSerializer,
    PaymentListSerializer,
    PaymentPlanDetailSerializer,
    PaymentPlanListSerializer,
    PendingPaymentSerializer,
    VolumeByDeliveryMechanismSerializer,
)
from hope.models.approval import Approval
from hope.models.business_area import BusinessArea
from hope.models.delivery_mechanism_per_payment_plan import DeliveryMechanismPerPaymentPlan
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.payment import Payment
from hope.models.payment_household_snapshot import PaymentHouseholdSnapshot
from hope.models.payment_plan import PaymentPlan
from hope.models.payment_plan_split import PaymentPlanSplit
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment
from hope.models.user import User


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
        serializer = PendingPaymentSerializer(instance=self.payment)
        data = serializer.data

        assert data["id"] == str(self.payment.id)
        assert data["household_unicef_id"] == self.hh1.unicef_id
        assert data["head_of_household"] == {
            "id": str(self.payment.head_of_household.id),
            "full_name": f"{self.payment.head_of_household.full_name}",
            "unicef_id": self.payment.head_of_household.unicef_id,
        }
        assert data["household_size"] == 2
        assert data["household_admin2"] == "New admin22"
        assert data["vulnerability_score"] == "123.012"

    def test_hoh_full_name_if_no_hoh(self) -> None:
        self.payment.head_of_household = None
        self.payment.save()
        serializer = PendingPaymentSerializer(instance=self.payment)
        data = serializer.data

        assert data["head_of_household"] is None


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

        assert data["id"] == str(self.payment.id)
        assert data["unicef_id"] == self.payment.unicef_id
        assert data["household_unicef_id"] == self.hh1.unicef_id
        assert data["household_size"] == 2
        assert data["household_admin2"] == "New admin22"
        assert data["entitlement_quantity"] == "99.00"
        assert data["delivered_quantity"] == "88.00"
        assert data["status"] == self.payment.get_status_display()
        assert data["fsp_name"] == "FSP 1"
        assert data["fsp_auth_code"] == ""

    def test_get_auth_code(self) -> None:
        user_1 = UserFactory()
        role, created = Role.objects.update_or_create(
            name="Role with Permissions",
            defaults={"permissions": [Permissions.PM_VIEW_FSP_AUTH_CODE.value]},
        )
        request = Mock()
        request.user = user_1
        user_role, _ = RoleAssignment.objects.get_or_create(user=user_1, role=role, business_area=self.business_area)
        serializer = PaymentListSerializer(instance=self.payment, context={"request": request})
        data = serializer.data

        assert data["fsp_auth_code"] == "AUTH_123"

    def test_get_snapshot_collector_full_name(self) -> None:
        household_data = {
            "primary_collector": {
                "full_name": "Name_from_Snapshot",
            },
            "alternate_collector": {},
        }
        PaymentHouseholdSnapshot.objects.create(
            payment=self.payment,
            snapshot_data=household_data,
            household_id=self.payment.household.id,
        )
        payment_qs = Payment.objects.filter(id=self.payment.id)
        serializer = PaymentListSerializer(payment_qs, many=True, context={"request": Mock(user=self.user)})
        data = serializer.data[0]

        assert data["snapshot_collector_full_name"] == "Name_from_Snapshot"


class PaymentPlanListSerializerTest(TestCase):
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
        )

    def test_created_by(self) -> None:
        serializer = PaymentPlanListSerializer(instance=self.pp)
        data = serializer.data
        assert data["created_by"] == f"{self.user.first_name} {self.user.last_name}"


class PaymentPlanDetailSerializerTest(TestCase):
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
            financial_service_provider__communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )
        cls.fsp_xlsx = cls.payment.financial_service_provider
        cls.fsp_api = FinancialServiceProviderFactory(
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123id",
        )

    @staticmethod
    def _create_user_with_permissions_in_ba(user: User, ba: BusinessArea, perms: List[Any]) -> None:
        role, created = Role.objects.update_or_create(
            name=f"Role with Permissions in {ba.name}", defaults={"permissions": perms}
        )
        user_role, _ = RoleAssignment.objects.get_or_create(user=user, role=role, business_area=ba)

    def test_serializer_all_data(self) -> None:
        self.pp.status = PaymentPlan.Status.ACCEPTED
        self.pp.save()
        DeliveryMechanismPerPaymentPlan.objects.create(
            payment_plan=self.pp,
            delivery_mechanism_order=1,
            financial_service_provider=self.fsp_xlsx,
            delivery_mechanism=DeliveryMechanismFactory(),
        )

        serializer = PaymentPlanDetailSerializer(instance=self.pp, context={"request": Mock(user=self.user)})
        data = serializer.data

        assert data["id"] == str(self.pp.id)
        assert data["reconciliation_summary"]["pending"] == 1
        assert data["reconciliation_summary"]["number_of_payments"] == 1
        assert data["excluded_households"] == []
        assert data["excluded_individuals"] == []
        assert data["fsp_communication_channel"] == "XLSX"
        assert data["can_create_follow_up"] is False
        assert data["can_split"] is True
        assert data["can_export_xlsx"] is False
        assert data["can_download_xlsx"] is False
        assert data["can_send_xlsx_password"] is False
        assert data["split_choices"] == to_choice_object(PaymentPlanSplit.SplitType.choices)
        assert data.get("volume_by_delivery_mechanism") is not None

    def test_can_export_xlsx(self) -> None:
        self._create_user_with_permissions_in_ba(
            self.user, self.business_area, [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value]
        )
        self.pp.status = PaymentPlan.Status.ACCEPTED
        self.pp.financial_service_provider = self.fsp_api
        self.pp.save()

        data = PaymentPlanDetailSerializer(instance=self.pp, context={"request": Mock(user=self.user)}).data
        assert data["fsp_communication_channel"] == "API"
        assert data["can_export_xlsx"] is False

    def test_can_download_xlsx(self) -> None:
        self._create_user_with_permissions_in_ba(
            self.user, self.business_area, [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value]
        )
        self.pp.status = PaymentPlan.Status.ACCEPTED
        self.pp.financial_service_provider = self.fsp_api
        self.pp.save()

        data = PaymentPlanDetailSerializer(instance=self.pp, context={"request": Mock(user=self.user)}).data
        assert data["fsp_communication_channel"] == "API"
        assert data["can_download_xlsx"] is False

    def test_can_send_xlsx_password(self) -> None:
        self._create_user_with_permissions_in_ba(
            self.user, self.business_area, [Permissions.PM_SEND_XLSX_PASSWORD.value]
        )
        self.pp.status = PaymentPlan.Status.ACCEPTED
        self.pp.financial_service_provider = self.fsp_api
        self.pp.save()

        data = PaymentPlanDetailSerializer(instance=self.pp, context={"request": Mock(user=self.user)}).data
        assert data["fsp_communication_channel"] == "API"
        assert data["can_send_xlsx_password"] is False


class ApprovalProcessSerializerTest(TestCase):
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
        )
        cls.approval_process = ApprovalProcessFactory(payment_plan=cls.pp)
        ApprovalFactory(
            approval_process=cls.approval_process,
            type=Approval.APPROVAL,
            created_by=None,
        )
        ApprovalFactory(
            approval_process=cls.approval_process,
            type=Approval.REJECT,
            created_by=cls.user,
        )

    def test_all_fields(self) -> None:
        user_name_str = f"{self.user.first_name} {self.user.last_name}"
        data = ApprovalProcessSerializer(instance=self.approval_process).data
        assert len(data["actions"]) == 4
        reject = data["actions"]["reject"][0]
        approval = data["actions"]["approval"][0]
        assert reject["type"] == Approval.REJECT
        assert reject["info"] == f"Rejected by {user_name_str}"
        assert approval["type"] == Approval.APPROVAL
        assert approval["info"] == "Approved"
        # add user data
        self.approval_process.sent_for_approval_by = self.user
        self.approval_process.sent_for_authorization_by = self.user
        self.approval_process.sent_for_finance_release_by = self.user
        self.approval_process.save()
        data_with_users = ApprovalProcessSerializer(instance=self.approval_process).data
        assert data_with_users["sent_for_approval_by"] == user_name_str
        assert data_with_users["sent_for_authorization_by"] == user_name_str
        assert data_with_users["sent_for_finance_release_by"] == user_name_str

    def test_rejected_on(self) -> None:
        approval_process = ApprovalProcessFactory(payment_plan=self.pp, sent_for_approval_date="2025-11-12")
        ApprovalFactory(
            approval_process=approval_process,
            type=Approval.REJECT,
            created_by=self.user,
        )
        data = ApprovalProcessSerializer(instance=approval_process).data
        assert data["rejected_on"] == "IN_APPROVAL"

        approval_process.sent_for_authorization_date = approval_process.sent_for_approval_date
        approval_process.save()
        data = ApprovalProcessSerializer(instance=approval_process).data
        assert data["rejected_on"] == "IN_AUTHORIZATION"

        approval_process.sent_for_finance_release_date = approval_process.sent_for_approval_date
        approval_process.save()
        data = ApprovalProcessSerializer(instance=approval_process).data
        assert data["rejected_on"] == "IN_REVIEW"


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

        assert data["volume"] is None
        assert data["volume_usd"] is None

        self.pp.financial_service_provider = self.fsp
        self.pp.save()
        data = VolumeByDeliveryMechanismSerializer(instance=self.dm_per_pp).data

        assert data["volume"] == 222
        assert data["volume_usd"] == 111
