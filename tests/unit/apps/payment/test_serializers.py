from typing import Any
from unittest.mock import Mock

import pytest

from extras.test_utils.factories import (
    ApprovalFactory,
    ApprovalProcessFactory,
    AreaFactory,
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
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
from hope.models import Approval, FinancialServiceProvider, Payment, PaymentPlan, PaymentPlanSplit

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory()


@pytest.fixture
def user() -> Any:
    return UserFactory(first_name="Test", last_name="User")


@pytest.fixture
def pending_payment_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(created_by=user, business_area=business_area)
    program = payment_plan.program_cycle.program
    admin2 = AreaFactory(name="New admin22")
    hoh = IndividualFactory(household=None, business_area=business_area, program=program)
    household = HouseholdFactory(
        admin2=admin2,
        head_of_household=hoh,
        size=2,
        program=program,
        business_area=business_area,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=hoh,
        collector=hoh,
        vulnerability_score=123.012,
    )
    return {
        "payment": payment,
        "household": household,
    }


@pytest.fixture
def payment_list_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(created_by=user, business_area=business_area)
    program = payment_plan.program_cycle.program
    admin2 = AreaFactory(name="New admin22")
    hoh = IndividualFactory(household=None, business_area=business_area, program=program)
    household = HouseholdFactory(
        admin2=admin2,
        head_of_household=hoh,
        size=2,
        program=program,
        business_area=business_area,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=hoh,
        collector=hoh,
        vulnerability_score=123.012,
        entitlement_quantity=99,
        delivered_quantity=88,
        financial_service_provider=FinancialServiceProviderFactory(name="FSP 1"),
        fsp_auth_code="AUTH_123",
    )
    return {
        "payment": payment,
        "household": household,
        "user": user,
        "business_area": business_area,
    }


@pytest.fixture
def payment_plan_list_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        dispersion_start_date=None,
        dispersion_end_date=None,
    )
    return {"payment_plan": payment_plan, "user": user}


@pytest.fixture
def payment_plan_detail_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        dispersion_start_date=None,
        dispersion_end_date=None,
    )
    program = payment_plan.program_cycle.program
    admin2 = AreaFactory(name="New for PP details")
    hoh = IndividualFactory(household=None, business_area=business_area, program=program)
    household = HouseholdFactory(
        admin2=admin2,
        head_of_household=hoh,
        size=2,
        program=program,
        business_area=business_area,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=hoh,
        collector=hoh,
        vulnerability_score=999.012,
        entitlement_quantity=100,
        delivered_quantity=155,
        financial_service_provider=FinancialServiceProviderFactory(
            name="FSP ABC",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        ),
    )
    fsp_xlsx = payment.financial_service_provider
    fsp_api = FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123id",
    )
    payment_plan.financial_service_provider = fsp_xlsx
    payment_plan.delivery_mechanism = DeliveryMechanismFactory()
    payment_plan.save()
    return {
        "payment_plan": payment_plan,
        "fsp_xlsx": fsp_xlsx,
        "fsp_api": fsp_api,
        "user": user,
        "business_area": business_area,
    }


@pytest.fixture
def approval_process_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        dispersion_start_date=None,
        dispersion_end_date=None,
    )
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    ApprovalFactory(
        approval_process=approval_process,
        type=Approval.APPROVAL,
        created_by=None,
    )
    ApprovalFactory(
        approval_process=approval_process,
        type=Approval.REJECT,
        created_by=user,
    )
    return {"approval_process": approval_process, "user": user, "payment_plan": payment_plan}


@pytest.fixture
def volume_by_delivery_context(business_area: Any, user: Any) -> dict[str, Any]:
    payment_plan = PaymentPlanFactory(
        created_by=user,
        business_area=business_area,
        dispersion_start_date=None,
        dispersion_end_date=None,
        financial_service_provider=None,
        delivery_mechanism=DeliveryMechanismFactory(),
    )
    program = payment_plan.program_cycle.program
    hoh = IndividualFactory(household=None, business_area=business_area, program=program)
    household = HouseholdFactory(
        head_of_household=hoh,
        size=2,
        program=program,
        business_area=business_area,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=hoh,
        collector=hoh,
        status=Payment.STATUS_SUCCESS,
        entitlement_quantity=222,
        entitlement_quantity_usd=111,
        financial_service_provider=FinancialServiceProviderFactory(name="FSP_TEST_1"),
    )
    return {"payment_plan": payment_plan, "fsp": payment.financial_service_provider}


def test_pending_payment_serializer_all_data(pending_payment_context: dict[str, Any]) -> None:
    payment = pending_payment_context["payment"]
    household = pending_payment_context["household"]
    serializer = PendingPaymentSerializer(instance=payment)
    data = serializer.data

    assert data["id"] == str(payment.id)
    assert data["household_unicef_id"] == household.unicef_id
    assert data["head_of_household"] == {
        "id": str(payment.head_of_household.id),
        "full_name": f"{payment.head_of_household.full_name}",
        "unicef_id": payment.head_of_household.unicef_id,
    }
    assert data["household_size"] == 2
    assert data["household_admin2"] == "New admin22"
    assert data["vulnerability_score"] == "123.012"


def test_pending_payment_serializer_hoh_full_name_if_no_hoh(pending_payment_context: dict[str, Any]) -> None:
    payment = pending_payment_context["payment"]
    payment.head_of_household = None
    payment.save(update_fields=["head_of_household"])
    serializer = PendingPaymentSerializer(instance=payment)
    data = serializer.data

    assert data["head_of_household"] is None


def test_payment_list_serializer_all_data(payment_list_context: dict[str, Any]) -> None:
    payment = payment_list_context["payment"]
    household = payment_list_context["household"]
    user = payment_list_context["user"]

    serializer = PaymentListSerializer(instance=payment, context={"request": Mock(user=user)})
    data = serializer.data

    assert data["id"] == str(payment.id)
    assert data["unicef_id"] == payment.unicef_id
    assert data["household_unicef_id"] == household.unicef_id
    assert data["household_size"] == 2
    assert data["household_admin2"] == "New admin22"
    assert data["entitlement_quantity"] == "99.00"
    assert data["delivered_quantity"] == "88.00"
    assert data["status"] == payment.get_status_display()
    assert data["fsp_name"] == "FSP 1"
    assert data["fsp_auth_code"] == ""


def test_payment_list_serializer_get_auth_code(payment_list_context: dict[str, Any]) -> None:
    payment = payment_list_context["payment"]
    user = payment_list_context["user"]
    business_area = payment_list_context["business_area"]

    role = RoleFactory(
        name="Role with Permissions",
        permissions=[Permissions.PM_VIEW_FSP_AUTH_CODE.value],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)

    serializer = PaymentListSerializer(instance=payment, context={"request": Mock(user=user)})
    data = serializer.data

    assert data["fsp_auth_code"] == "AUTH_123"


def test_payment_list_serializer_snapshot_collector_full_name(payment_list_context: dict[str, Any]) -> None:
    payment = payment_list_context["payment"]
    household_data = {
        "primary_collector": {
            "full_name": "Name_from_Snapshot",
        },
        "alternate_collector": {},
    }
    PaymentHouseholdSnapshotFactory(
        payment=payment,
        snapshot_data=household_data,
        household_id=payment.household.id,
    )
    payment_qs = Payment.objects.filter(id=payment.id)
    serializer = PaymentListSerializer(
        payment_qs,
        many=True,
        context={"request": Mock(user=payment_list_context["user"])},
    )
    data = serializer.data[0]

    assert data["snapshot_collector_full_name"] == "Name_from_Snapshot"


def test_payment_list_serializer_snapshot_collector_data_none(payment_list_context: dict[str, Any]) -> None:
    payment = payment_list_context["payment"]
    household_data = {
        "primary_collector": None,
        "alternate_collector": None,
    }
    PaymentHouseholdSnapshotFactory(
        payment=payment,
        snapshot_data=household_data,
        household_id=payment.household.id,
    )
    payment = Payment.objects.get(id=payment.id)
    account_data = PaymentListSerializer.get_collector_field(payment, "account_data")
    assert account_data is None


def test_payment_list_serializer_snapshot_alt_collector_full_name_and_id(
    payment_list_context: dict[str, Any],
) -> None:
    payment = payment_list_context["payment"]
    household_data = {
        "primary_collector": {
            "full_name": "Name_Pr_Collector",
        },
        "alternate_collector": {"full_name": "Full_Name_Alt_Collector", "id": "uuid_1234"},
    }
    PaymentHouseholdSnapshotFactory(
        payment=payment,
        snapshot_data=household_data,
        household_id=payment.household.id,
    )
    payment_qs = Payment.objects.filter(id=payment.id)
    serializer = PaymentListSerializer(
        payment_qs,
        many=True,
        context={"request": Mock(user=payment_list_context["user"])},
    )
    data = serializer.data[0]

    assert data["snapshot_alternate_collector_full_name"] == "Full_Name_Alt_Collector"
    assert data["snapshot_alternate_collector_id"] == "uuid_1234"


def test_payment_plan_list_serializer_created_by(payment_plan_list_context: dict[str, Any]) -> None:
    payment_plan = payment_plan_list_context["payment_plan"]
    user = payment_plan_list_context["user"]

    serializer = PaymentPlanListSerializer(instance=payment_plan)
    data = serializer.data
    assert data["created_by"] == f"{user.first_name} {user.last_name}"


def test_payment_plan_detail_serializer_all_data(payment_plan_detail_context: dict[str, Any]) -> None:
    payment_plan = payment_plan_detail_context["payment_plan"]
    user = payment_plan_detail_context["user"]
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save(update_fields=["status"])

    serializer = PaymentPlanDetailSerializer(instance=payment_plan, context={"request": Mock(user=user)})
    data = serializer.data

    assert data["id"] == str(payment_plan.id)
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


def test_payment_plan_detail_can_export_xlsx(payment_plan_detail_context: dict[str, Any]) -> None:
    payment_plan = payment_plan_detail_context["payment_plan"]
    user = payment_plan_detail_context["user"]
    business_area = payment_plan_detail_context["business_area"]
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.financial_service_provider = payment_plan_detail_context["fsp_api"]
    payment_plan.save(update_fields=["status", "financial_service_provider"])

    role = RoleFactory(
        name="Role with Permissions in BA",
        permissions=[Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)

    data = PaymentPlanDetailSerializer(instance=payment_plan, context={"request": Mock(user=user)}).data
    assert data["fsp_communication_channel"] == "API"
    assert data["can_export_xlsx"] is False


def test_payment_plan_detail_can_download_xlsx(payment_plan_detail_context: dict[str, Any]) -> None:
    payment_plan = payment_plan_detail_context["payment_plan"]
    user = payment_plan_detail_context["user"]
    business_area = payment_plan_detail_context["business_area"]
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.financial_service_provider = payment_plan_detail_context["fsp_api"]
    payment_plan.save(update_fields=["status", "financial_service_provider"])

    role = RoleFactory(
        name="Role with Permissions in BA",
        permissions=[Permissions.PM_DOWNLOAD_FSP_AUTH_CODE.value],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)

    data = PaymentPlanDetailSerializer(instance=payment_plan, context={"request": Mock(user=user)}).data
    assert data["fsp_communication_channel"] == "API"
    assert data["can_download_xlsx"] is False


def test_payment_plan_detail_can_send_xlsx_password(payment_plan_detail_context: dict[str, Any]) -> None:
    payment_plan = payment_plan_detail_context["payment_plan"]
    user = payment_plan_detail_context["user"]
    business_area = payment_plan_detail_context["business_area"]
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.financial_service_provider = payment_plan_detail_context["fsp_api"]
    payment_plan.save(update_fields=["status", "financial_service_provider"])

    role = RoleFactory(
        name="Role with Permissions in BA",
        permissions=[Permissions.PM_SEND_XLSX_PASSWORD.value],
    )
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)

    data = PaymentPlanDetailSerializer(instance=payment_plan, context={"request": Mock(user=user)}).data
    assert data["fsp_communication_channel"] == "API"
    assert data["can_send_xlsx_password"] is False


def test_approval_process_serializer_all_fields(approval_process_context: dict[str, Any]) -> None:
    approval_process = approval_process_context["approval_process"]
    user = approval_process_context["user"]
    user_name_str = f"{user.first_name} {user.last_name}"
    data = ApprovalProcessSerializer(instance=approval_process).data
    assert len(data["actions"]) == 4
    reject = data["actions"]["reject"][0]
    approval = data["actions"]["approval"][0]
    assert reject["type"] == Approval.REJECT
    assert reject["info"] == f"Rejected by {user_name_str}"
    assert approval["type"] == Approval.APPROVAL
    assert approval["info"] == "Approved"

    approval_process.sent_for_approval_by = user
    approval_process.sent_for_authorization_by = user
    approval_process.sent_for_finance_release_by = user
    approval_process.save(
        update_fields=[
            "sent_for_approval_by",
            "sent_for_authorization_by",
            "sent_for_finance_release_by",
        ]
    )
    data_with_users = ApprovalProcessSerializer(instance=approval_process).data
    assert data_with_users["sent_for_approval_by"] == user_name_str
    assert data_with_users["sent_for_authorization_by"] == user_name_str
    assert data_with_users["sent_for_finance_release_by"] == user_name_str


def test_approval_process_serializer_rejected_on(approval_process_context: dict[str, Any]) -> None:
    approval_process = approval_process_context["approval_process"]
    user = approval_process_context["user"]
    payment_plan = approval_process_context["payment_plan"]

    approval_process = ApprovalProcessFactory(payment_plan=payment_plan, sent_for_approval_date="2025-11-12")
    ApprovalFactory(
        approval_process=approval_process,
        type=Approval.REJECT,
        created_by=user,
    )
    data = ApprovalProcessSerializer(instance=approval_process).data
    assert data["rejected_on"] == "IN_APPROVAL"

    approval_process.sent_for_authorization_date = approval_process.sent_for_approval_date
    approval_process.save(update_fields=["sent_for_authorization_date"])
    data = ApprovalProcessSerializer(instance=approval_process).data
    assert data["rejected_on"] == "IN_AUTHORIZATION"

    approval_process.sent_for_finance_release_date = approval_process.sent_for_approval_date
    approval_process.save(update_fields=["sent_for_finance_release_date"])
    data = ApprovalProcessSerializer(instance=approval_process).data
    assert data["rejected_on"] == "IN_REVIEW"


def test_volume_by_delivery_mechanism_serializer_get_volume_fields(volume_by_delivery_context: dict[str, Any]) -> None:
    payment_plan = volume_by_delivery_context["payment_plan"]
    data = VolumeByDeliveryMechanismSerializer(instance=payment_plan).data

    assert data["volume"] is None
    assert data["volume_usd"] is None

    payment_plan.financial_service_provider = volume_by_delivery_context["fsp"]
    payment_plan.save(update_fields=["financial_service_provider"])
    data = VolumeByDeliveryMechanismSerializer(instance=payment_plan).data

    assert data["volume"] == 222
    assert data["volume_usd"] == 111
