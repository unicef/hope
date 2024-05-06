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
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
)
from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    ApprovalProcess,
    PaymentHouseholdSnapshot,
    PaymentPlan,
)


def create_child_payment_plans(pp: PaymentPlan) -> None:
    fpp1 = PaymentPlanFactory(
        id="56aca38c-dc16-48a9-ace4-70d88b41d462",
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        start_date=timezone.datetime(2020, 9, 10, tzinfo=utc),
        end_date=timezone.datetime(2020, 11, 10, tzinfo=utc),
        is_follow_up=True,
        source_payment_plan=pp,
    )
    fpp1.unicef_id = "PP-0060-20-00000003"
    fpp1.save()

    fpp2 = PaymentPlanFactory(
        id="5b04f7c3-579a-48dd-a232-424daaefffe7",
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        start_date=timezone.datetime(2020, 9, 10, tzinfo=utc),
        end_date=timezone.datetime(2020, 11, 10, tzinfo=utc),
        is_follow_up=True,
        source_payment_plan=pp,
    )
    fpp2.unicef_id = "PP-0060-20-00000004"
    fpp2.save()


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
      allPaymentPlans(businessArea: $businessArea, orderBy: "unicef_id") {
        edges {
          node {
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
            canCreateFollowUp
            dispersionEndDate
            dispersionStartDate
            endDate
            exchangeRate
            femaleAdultsCount
            femaleChildrenCount
            maleAdultsCount
            maleChildrenCount
            paymentItems{
              totalCount
            }
            paymentsConflictsCount
            startDate
            status
            totalDeliveredQuantity
            totalDeliveredQuantityUsd
            totalEntitledQuantity
            totalEntitledQuantityRevised
            totalEntitledQuantityRevisedUsd
            totalEntitledQuantityUsd
            totalHouseholdsCount
            totalIndividualsCount
            totalUndeliveredQuantity
            totalUndeliveredQuantityUsd
            unicefId
          }
        }
      }
    }
    """

    ALL_PAYMENT_PLANS_FILTER_QUERY = """
    query AllPaymentPlans($businessArea: String!, $search: String, $status: [String], $totalEntitledQuantityFrom: Float, $totalEntitledQuantityTo: Float, $dispersionStartDate: Date, $dispersionEndDate: Date, $program: String) {
        allPaymentPlans(businessArea: $businessArea, search: $search, status: $status, totalEntitledQuantityFrom: $totalEntitledQuantityFrom, totalEntitledQuantityTo: $totalEntitledQuantityTo, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate, program: $program, orderBy: "unicef_id") {
        edges {
          node {
            dispersionEndDate
            dispersionStartDate
            status
            totalEntitledQuantity
            unicefId
          }
        }
      }
    }
    """

    ALL_PAYMENT_PLANS_FILTER_QUERY_2 = """
        query AllPaymentPlans($businessArea: String!, $isFollowUp: Boolean, $sourcePaymentPlanId: String) {
            allPaymentPlans(businessArea: $businessArea, isFollowUp: $isFollowUp, sourcePaymentPlanId: $sourcePaymentPlanId, orderBy: "unicef_id") {
            edges {
              node {
                unicefId
                dispersionStartDate
                dispersionEndDate
                isFollowUp
                sourcePaymentPlan {
                  unicefId
                }
                followUps {
                  totalCount
                  edges {
                      node {
                          unicefId
                      }
                  }
                }
              }
            }
          }
        }
        """

    ALL_PAYMENTS_QUERY = """
    query AllPayments($paymentPlanId: String!, $businessArea: String!) {
      allPayments(paymentPlanId: $paymentPlanId, businessArea: $businessArea, orderBy: "unicef_id") {
        edgeCount
        edges {
          node {
            conflicted
            deliveredQuantity
            deliveredQuantityUsd
            entitlementQuantity
            entitlementQuantityUsd
            parent {
              unicefId
            }
            paymentPlanHardConflicted
            paymentPlanHardConflictedData {
              paymentPlanStatus
              paymentPlanStartDate
              paymentPlanEndDate
            }
            paymentPlanSoftConflicted
            paymentPlanSoftConflictedData {
              paymentPlanStatus
              paymentPlanStartDate
              paymentPlanEndDate
            }
            unicefId
          }
        }
        totalCount
      }
    }
    """

    PAYMENT_NODE_SNAPSHOT_DATA = """
        query Payment($id: ID!) {
          payment(id: $id) {
            totalPersonsCovered
            snapshotCollectorFullName
            snapshotCollectorDeliveryPhoneNo
            snapshotCollectorBankName
            snapshotCollectorBankAccountNumber
            snapshotCollectorDebitCardNumber
            additionalCollectorName
            reasonForUnsuccessfulPayment
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.maxDiff = None
        create_afghanistan()
        cls.user = UserFactory.create(username="qazxsw321")
        cls.create_user_role_with_permissions(
            cls.user,
            [Permissions.PM_VIEW_LIST, Permissions.PM_VIEW_DETAILS],
            BusinessArea.objects.get(slug="afghanistan"),
        )

        with freeze_time("2020-10-10"):
            program = RealProgramFactory()
            program_cycle = program.cycles.first()
            cls.pp = PaymentPlanFactory(
                program=program,
                program_cycle=program_cycle,
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
                currency="PLN",
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
                currency="PLN",
            )

            # create hard conflicted payment
            cls.pp_conflicted = PaymentPlanFactory(
                program=program,
                program_cycle=program_cycle,
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
                financial_service_provider=FinancialServiceProviderFactory(name="xxx"),
                currency="PLN",
            )
            PaymentFactory(
                parent=cls.pp_conflicted,
                conflicted=True,
                entitlement_quantity=00.00,
                entitlement_quantity_usd=00.00,
                delivered_quantity=00.00,
                delivered_quantity_usd=00.00,
                financial_service_provider=FinancialServiceProviderFactory(name="yyy"),
                currency="PLN",
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
    def test_fetch_all_payments_for_open_payment_plan(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "paymentPlanId": encode_id_base64(self.pp.pk, "PaymentPlan")},
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
                variables={
                    "businessArea": "afghanistan",
                    "program": encode_id_base64(self.pp.program.pk, "Program"),
                    **filter_data,
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

        resp_data = self.graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_FILTER_QUERY_2,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "isFollowUp": False,
            },
        )["data"]

        pp_query = resp_data["allPaymentPlans"]["edges"]

        assert len(pp_query) == 2

        for parent_pp_id in ("PP-01", "PP-02"):
            parent_pp = [pp for pp in pp_query if pp["node"]["unicefId"] == parent_pp_id][0]["node"]
            assert parent_pp["isFollowUp"] is False
            assert parent_pp["sourcePaymentPlan"] is None

            # check followUps
            follow_ups = parent_pp["followUps"]

            if parent_pp_id == "PP-01":
                assert follow_ups["totalCount"] == 2
                for unicef_id in ("PP-0060-20-00000003", "PP-0060-20-00000004"):
                    assert len([i for i in follow_ups["edges"] if i["node"]["unicefId"] == unicef_id]) == 1

            if parent_pp_id == "PP-02":
                assert follow_ups["totalCount"] == 0

    def test_fetch_payment_plan_status_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_STATUS_CHOICES_QUERY,
            context={"user": self.user},
        )

    def test_payment_node_with_legacy_data(self) -> None:
        # test get snapshot data only
        program = RealProgramFactory()
        program_cycle = program.cycles.first()
        new_pp = PaymentPlanFactory(
            program=program,
            program_cycle=program_cycle,
            dispersion_start_date=datetime(2023, 8, 10),
            dispersion_end_date=datetime(2023, 12, 10),
            start_date=timezone.datetime(2023, 9, 10, tzinfo=utc),
            end_date=timezone.datetime(2023, 11, 10, tzinfo=utc),
            is_follow_up=False,
        )
        hoh_1 = IndividualFactory(household=None)
        hoh_2 = IndividualFactory(household=None)
        hoh_3 = IndividualFactory(household=None)
        household_1 = HouseholdFactory(head_of_household=hoh_1, size=5)
        household_2 = HouseholdFactory(head_of_household=hoh_2, size=10)
        household_3 = HouseholdFactory(head_of_household=hoh_3, size=15)
        payment_legacy = PaymentFactory(
            parent=new_pp,
            household=household_1,
            head_of_household=hoh_1,
            currency="PLN",
            reason_for_unsuccessful_payment="reason 123",
        )
        payment_new_1 = PaymentFactory(
            parent=new_pp,
            household=household_2,
            head_of_household=hoh_2,
            currency="PLN",
            additional_collector_name="AddCollectorName11",
            additional_document_number="AddDocNumber11",
            additional_document_type="AddDocType11",
            reason_for_unsuccessful_payment="reason 222",
        )
        payment_new_2 = PaymentFactory(
            parent=new_pp,
            household=household_3,
            head_of_household=hoh_3,
            currency="PLN",
            additional_collector_name="AddCollectorName22",
            additional_document_number="AddDocNumber22",
            additional_document_type="AddDocType22",
            reason_for_unsuccessful_payment="reason 333",
        )
        # create snapshot for payment
        snapshot_data_hh2 = {
            "size": 99,
            "primary_collector": {
                "full_name": "PrimaryCollectorFullName",
                "payment_delivery_phone_no": "1111111",
                "bank_account_info": {
                    "bank_name": "PrimaryCollBankName",
                    "bank_account_number": "PrimaryCollBankNumber",
                    "debit_card_number": "PrimaryCollDebitCardNumber",
                },
            },
        }
        snapshot_data_hh3 = {
            "size": 55,
            "alternate_collector": {
                "full_name": "AlternateCollectorFullName",
                "payment_delivery_phone_no": "222222222",
                "bank_account_info": {
                    "bank_name": "AlternateCollBankName",
                    "bank_account_number": "AlternateCollBankNumber",
                    "debit_card_number": "AlternateCollDebitCardNumber",
                },
            },
        }
        PaymentHouseholdSnapshot.objects.create(
            payment=payment_new_1, snapshot_data=snapshot_data_hh2, household_id=household_2.id
        )
        PaymentHouseholdSnapshot.objects.create(
            payment=payment_new_2, snapshot_data=snapshot_data_hh3, household_id=household_3.id
        )

        for payment_id in [payment_legacy.pk, payment_new_1.pk, payment_new_2.pk]:
            self.snapshot_graphql_request(
                request_string=self.PAYMENT_NODE_SNAPSHOT_DATA,
                context={"user": self.user},
                variables={"id": encode_id_base64(payment_id, "Payment")},
            )
