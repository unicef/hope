import json
from unittest.mock import patch
from datetime import datetime
from dateutil.relativedelta import relativedelta

from freezegun import freeze_time
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentFactory
from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory
from hct_mis_api.apps.payment.models import PaymentPlan, ApprovalProcess


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
            payments{
              totalCount
            }
            approvalProcess{
              totalCount
            }
            approvalNumberRequired
            authorizationNumberRequired
            financeReviewNumberRequired
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

    ALL_PAYMENTS_QUERY = """
    query AllPayments($paymentPlanId: String!, $businessArea: String!) {
      allPayments(paymentPlanId: $paymentPlanId, businessArea: $businessArea) {
        edgeCount
        totalCount
        edges {
          node {
            entitlementQuantity
            entitlementQuantityUsd
            deliveredQuantity
            deliveredQuantityUsd
            paymentPlan {
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
            excluded
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PAYMENT_MODULE_VIEW_LIST], BusinessArea.objects.get(slug="afghanistan")
        )

        with freeze_time("2020-10-10"):
            cls.pp = PaymentPlanFactory(
                dispersion_start_date=datetime(2020, 8, 10),
                dispersion_end_date=datetime(2020, 12, 10),
                start_date=datetime(2020, 9, 10),
                end_date=datetime(2020, 11, 10),
                unicef_id="PP-01",
            )
            hoh1 = IndividualFactory(household=None)
            hoh2 = IndividualFactory(household=None)
            hh1 = HouseholdFactory(head_of_household=hoh1)
            hh2 = HouseholdFactory(head_of_household=hoh2)
            p1 = PaymentFactory(
                payment_plan=cls.pp,
                excluded=False,
                household=hh1,
                head_of_household=hoh1,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
            )
            p2 = PaymentFactory(
                payment_plan=cls.pp,
                excluded=True,
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
                unicef_id="PP-02",
            )
            p_conflicted = PaymentFactory(
                payment_plan=cls.pp_conflicted,
                household=p2.household,
                excluded=False,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
            )
            p_not_conflicted = PaymentFactory(
                payment_plan=cls.pp_conflicted,
                excluded=True,
                entitlement_quantity=00.00,
                entitlement_quantity_usd=00.00,
                delivered_quantity=00.00,
                delivered_quantity_usd=00.00,
            )

            female_child = IndividualFactory(
                household=hh1, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=5)
            )
            male_child = IndividualFactory(
                household=hh1, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=5)
            )
            female_adult = IndividualFactory(
                household=hh2, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=20)
            )
            male_adult = IndividualFactory(
                household=hh2, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=20)
            )

            ApprovalProcess.objects.create(payment_plan=cls.pp)

            with patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0):
                cls.pp.update_population_count_fields()
                cls.pp.update_money_fields()
                cls.pp_conflicted.update_population_count_fields()
                cls.pp_conflicted.update_money_fields()

    def test_fetch_payment_plan_status_choices(self):
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_STATUS_CHOICES_QUERY,
            context={"user": self.user},
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payment_plans(self):
        self.maxDiff = None
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
            },
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payment_plans_filters(self):
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
    def test_fetch_all_payments_for_open_payment_plan(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "paymentPlanId": encode_id_base64(self.pp.pk, "PaymentPlan")},
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payments_for_locked_payment_plan(self):
        """Conflicting payment are excluded"""
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "paymentPlanId": encode_id_base64(self.pp_conflicted.pk, "PaymentPlan"),
            },
        )
