from datetime import datetime
from unittest.mock import patch

from django.utils import timezone

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    ApprovalProcess,
    PaymentPlan,
)


def create_child_payment_plans(pp: PaymentPlan) -> None:
    PaymentPlanFactory(
        id="56aca38c-dc16-48a9-ace4-70d88b41d462",
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        start_date=timezone.datetime(2020, 9, 10, tzinfo=utc),
        end_date=timezone.datetime(2020, 11, 10, tzinfo=utc),
        is_follow_up=True,
        source_payment_plan=pp,
    )
    PaymentPlanFactory(
        id="5b04f7c3-579a-48dd-a232-424daaefffe7",
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        start_date=timezone.datetime(2020, 9, 10, tzinfo=utc),
        end_date=timezone.datetime(2020, 11, 10, tzinfo=utc),
        is_follow_up=True,
        source_payment_plan=pp,
    )


class TestPaymentPlanQueries(APITestCase):
    PAYMENT_PLAN_STATUS_CHOICES_QUERY = """
    query PaymentPlanStatusChoices{
        paymentPlanStatusChoices{
            name,
            value
        }
    }
    """

    ALL_PAYMENT_PLANS_QUERY = """
    query AllPaymentPlans($businessArea: String!) {
      allPaymentPlans(businessArea: $businessArea) {
        edges {
          node {
            status
            startDate
            dispersionStartDate
            dispersionEndDate
            endDate
            exchangeRate
            paymentsConflictsCount
            totalEntitledQuantity
            totalEntitledQuantityUsd
            totalEntitledQuantityRevised
            totalEntitledQuantityRevisedUsd
            totalDeliveredQuantity
            totalDeliveredQuantityUsd
            totalUndeliveredQuantity
            totalUndeliveredQuantityUsd
            unicefId
            femaleChildrenCount
            maleChildrenCount
            femaleAdultsCount
            maleAdultsCount
            totalHouseholdsCount
            totalIndividualsCount
            paymentItems{
              totalCount
            }
            approvalProcess{
              totalCount
              edges {
                node {
                  approvalNumberRequired
                  authorizationNumberRequired
                  financeReleaseNumberRequired
                }
              }
            }
            paymentsConflictsCount
          }
        }
      }
    }
    """

    ALL_PAYMENT_PLANS_FILTER_QUERY = """
    query AllPaymentPlans($businessArea: String!, $search: String, $status: [String], $totalEntitledQuantityFrom: Float, $totalEntitledQuantityTo: Float, $dispersionStartDate: Date, $dispersionEndDate: Date) {
        allPaymentPlans(businessArea: $businessArea, search: $search, status: $status, totalEntitledQuantityFrom: $totalEntitledQuantityFrom, totalEntitledQuantityTo: $totalEntitledQuantityTo, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate) {
        edges {
          node {
            status
            dispersionStartDate
            dispersionEndDate
            unicefId
            totalEntitledQuantity
          }
        }
      }
    }
    """

    ALL_PAYMENT_PLANS_FILTER_QUERY_2 = """
        query AllPaymentPlans($businessArea: String!, $isFollowUp: Boolean, $sourcePaymentPlanId: String) {
            allPaymentPlans(businessArea: $businessArea, isFollowUp: $isFollowUp, sourcePaymentPlanId: $sourcePaymentPlanId) {
            edges {
              node {
                unicefId
                dispersionStartDate
                dispersionEndDate
                isFollowUp
                sourcePaymentPlan {
                  unicefId
                }
                listOfPaymentPlans
              }
            }
          }
        }
        """

    ALL_PAYMENTS_QUERY = """
    query AllPayments($paymentPlanId: String!, $businessArea: String!) {
      allPayments(paymentPlanId: $paymentPlanId, businessArea: $businessArea) {
        edgeCount
        totalCount
        edges {
          node {
            unicefId
            entitlementQuantity
            entitlementQuantityUsd
            deliveredQuantity
            deliveredQuantityUsd
            parent {
              unicefId
            }
            paymentPlanHardConflicted
            paymentPlanSoftConflicted
            paymentPlanHardConflictedData {
              paymentPlanStatus
              paymentPlanStartDate
              paymentPlanEndDate
            }
            paymentPlanSoftConflictedData {
              paymentPlanStatus
              paymentPlanStartDate
              paymentPlanEndDate
            }
            conflicted
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PM_VIEW_LIST], BusinessArea.objects.get(slug="afghanistan")
        )

        with freeze_time("2020-10-10"):
            cls.pp = PaymentPlanFactory(
                dispersion_start_date=datetime(2020, 8, 10),
                dispersion_end_date=datetime(2020, 12, 10),
                start_date=timezone.datetime(2020, 9, 10, tzinfo=utc),
                end_date=timezone.datetime(2020, 11, 10, tzinfo=utc),
                is_follow_up=False,
            )
            cls.pp.unicef_id = "PP-01"
            cls.pp.save()

            hoh1 = IndividualFactory(household=None)
            hoh2 = IndividualFactory(household=None)
            hh1 = HouseholdFactory(head_of_household=hoh1)
            hh2 = HouseholdFactory(head_of_household=hoh2)
            PaymentFactory(
                parent=cls.pp,
                conflicted=False,
                household=hh1,
                head_of_household=hoh1,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
            )
            p2 = PaymentFactory(
                parent=cls.pp,
                conflicted=True,
                household=hh2,
                head_of_household=hoh2,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
            )

            # create hard conflicted payment
            cls.pp_conflicted = PaymentPlanFactory(
                start_date=cls.pp.start_date,
                end_date=cls.pp.end_date,
                status=PaymentPlan.Status.LOCKED,
                dispersion_start_date=cls.pp.dispersion_start_date + relativedelta(months=2),
                dispersion_end_date=cls.pp.dispersion_end_date - relativedelta(months=2),
            )
            cls.pp_conflicted.unicef_id = "PP-02"
            cls.pp_conflicted.save()

            PaymentFactory(
                parent=cls.pp_conflicted,
                household=p2.household,
                conflicted=False,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
            )
            PaymentFactory(
                parent=cls.pp_conflicted,
                conflicted=True,
                entitlement_quantity=00.00,
                entitlement_quantity_usd=00.00,
                delivered_quantity=00.00,
                delivered_quantity_usd=00.00,
            )

            IndividualFactory(household=hh1, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=5))
            IndividualFactory(household=hh1, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=5))
            IndividualFactory(household=hh2, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=20))
            IndividualFactory(household=hh2, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=20))

            AcceptanceProcessThreshold.objects.create(
                business_area=BusinessArea.objects.first(),
                approval_number_required=2,
                authorization_number_required=2,
                finance_release_number_required=3,
            )
            ApprovalProcess.objects.create(
                payment_plan=cls.pp,
                approval_number_required=cls.pp.approval_number_required,
                authorization_number_required=cls.pp.authorization_number_required,
                finance_release_number_required=cls.pp.finance_release_number_required,
            )

            with patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0):
                cls.pp.update_population_count_fields()
                cls.pp.update_money_fields()
                cls.pp_conflicted.update_population_count_fields()
                cls.pp_conflicted.update_money_fields()

    def test_fetch_payment_plan_status_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_STATUS_CHOICES_QUERY,
            context={"user": self.user},
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payment_plans(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
            },
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payment_plans_filters(self) -> None:
        for filter_data in [
            {"search": self.pp.unicef_id},
            {"status": self.pp.status},
            {
                "totalEntitledQuantityFrom": float(self.pp_conflicted.total_entitled_quantity - 10),
                "totalEntitledQuantityTo": float(self.pp_conflicted.total_entitled_quantity + 10),
            },
            {
                "dispersionStartDate": self.pp_conflicted.dispersion_start_date,
                "dispersionEndDate": self.pp_conflicted.dispersion_end_date,
            },
        ]:
            self.snapshot_graphql_request(
                request_string=self.ALL_PAYMENT_PLANS_FILTER_QUERY,
                context={"user": self.user},
                variables={"businessArea": "afghanistan", **filter_data},
            )

    @freeze_time("2020-10-10")
    def test_fetch_all_payments_for_open_payment_plan(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "paymentPlanId": encode_id_base64(self.pp.pk, "PaymentPlan")},
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payments_for_locked_payment_plan(self) -> None:
        """Conflicting payment are conflicted"""
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "paymentPlanId": encode_id_base64(self.pp_conflicted.pk, "PaymentPlan"),
            },
        )

    @freeze_time("2020-10-10")
    def test_filter_payment_plans_with_follow_up_flag(self) -> None:
        create_child_payment_plans(self.pp)

        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_FILTER_QUERY_2,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "isFollowUp": False,
            },
        )

    @freeze_time("2020-10-10")
    def test_filter_payment_plans_with_source_id(self) -> None:
        create_child_payment_plans(self.pp)

        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_FILTER_QUERY_2,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "sourcePaymentPlanId": encode_id_base64(self.pp.id, "PaymentPlan"),
            },
        )
