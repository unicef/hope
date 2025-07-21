from datetime import datetime
from io import BytesIO
from typing import Any, List
from unittest.mock import patch

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from parameterized import parameterized
from pytz import utc

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.utils import create_diff
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64
from tests.extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from tests.extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    RealProgramFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    ApprovalProcess,
    DeliveryMechanism,
    FinancialServiceProvider,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSupportingDocument,
    PaymentVerificationPlan,
)
from tests.extras.test_utils.factories.program import ProgramCycleFactory
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaRuleFactory
from hct_mis_api.contrib.vision.fixtures import FundsCommitmentFactory
from hct_mis_api.contrib.vision.models import FundsCommitmentItem


def create_child_payment_plans(pp: PaymentPlan, created_by: User) -> None:
    fpp1 = PaymentPlanFactory(
        name="PaymentPlan FollowUp 01",
        id="56aca38c-dc16-48a9-ace4-70d88b41d462",
        is_follow_up=True,
        source_payment_plan=pp,
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        created_by=created_by,
    )
    fpp1.unicef_id = "PP-0060-20-00000003"
    fpp1.save()

    fpp2 = PaymentPlanFactory(
        name="PaymentPlan FollowUp 02",
        id="5b04f7c3-579a-48dd-a232-424daaefffe7",
        is_follow_up=True,
        source_payment_plan=pp,
        dispersion_start_date=datetime(2020, 8, 10),
        dispersion_end_date=datetime(2020, 12, 10),
        created_by=created_by,
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
            canSplit
            canSendToPaymentGateway
            canCreateXlsxWithFspAuthCode
            fspCommunicationChannel
            canExportXlsx
            canDownloadXlsx
            canSendXlsxPassword
            unsuccessfulPaymentsCount
            hasFspDeliveryMechanismXlsxTemplate
            availablePaymentRecordsCount
            importedFileName
            hasPaymentListExportFile
            currencyName
            verificationPlans{
                totalCount
            }
            program{
              name
            }
            splitChoices{
              name
              value
            }
            dispersionEndDate
            dispersionStartDate
            exchangeRate
            femaleAdultsCount
            femaleChildrenCount
            maleAdultsCount
            maleChildrenCount
            paymentItems{
              totalCount
            }
            programCycle{
                startDate
                endDate
            }
            paymentsConflictsCount
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
            supportingDocuments{
              title
            }
            excludedHouseholds{
              id
            }
            excludedIndividuals{
              id
            }
          }
        }
      }
    }
    """

    ALL_PAYMENT_PLANS_FILTER_QUERY = """
    query AllPaymentPlans($businessArea: String!, $search: String, $status: [String], $totalEntitledQuantityFrom: Float, $totalEntitledQuantityTo: Float, $dispersionStartDate: Date, $dispersionEndDate: Date, $program: String, $programCycle: String, $verificationStatus: [String], $serviceProvider: String, $deliveryTypes: [String]) {
        allPaymentPlans(businessArea: $businessArea, search: $search, status: $status, totalEntitledQuantityFrom: $totalEntitledQuantityFrom, totalEntitledQuantityTo: $totalEntitledQuantityTo, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate, program: $program, orderBy: "unicef_id", programCycle: $programCycle, verificationStatus: $verificationStatus, serviceProvider: $serviceProvider, deliveryTypes: $deliveryTypes) {
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
    query AllPayments($paymentPlanId: String, $businessArea: String!, $householdId: String) {
      allPayments(paymentPlanId: $paymentPlanId, businessArea: $businessArea, orderBy: "unicef_id", householdId: $householdId) {
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
            fspAuthCode
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
            fullName
            snapshotCollectorAccountData
            additionalCollectorName
            reasonForUnsuccessfulPayment
            verification {
              status
            }
          }
        }
        """

    PAYMENT_PLANS_FILTER_QUERY = """
        query AllPaymentPlans($businessArea: String!, $search: String, $status: [String], $totalEntitledQuantityFrom: Float, $totalEntitledQuantityTo: Float, $dispersionStartDate: Date, $dispersionEndDate: Date, $program: String, $programCycle: String, $isPaymentPlan: Boolean, $isTargetPopulation: Boolean, $name: String, $totalHouseholdsCountMin: Int, $totalHouseholdsCountMax: Int, $totalHouseholdsCountWithValidPhoneNoMax: Int, $totalHouseholdsCountWithValidPhoneNoMin: Int, $statusNot: String) {
            allPaymentPlans(businessArea: $businessArea, search: $search, status: $status, totalEntitledQuantityFrom: $totalEntitledQuantityFrom, totalEntitledQuantityTo: $totalEntitledQuantityTo, dispersionStartDate: $dispersionStartDate, dispersionEndDate: $dispersionEndDate, program: $program, orderBy: "status", programCycle: $programCycle, isPaymentPlan: $isPaymentPlan, isTargetPopulation: $isTargetPopulation, name: $name, totalHouseholdsCountMin: $totalHouseholdsCountMin, totalHouseholdsCountMax: $totalHouseholdsCountMax, totalHouseholdsCountWithValidPhoneNoMax: $totalHouseholdsCountWithValidPhoneNoMax, totalHouseholdsCountWithValidPhoneNoMin: $totalHouseholdsCountWithValidPhoneNoMin, statusNot: $statusNot) {
            edges {
              node {
                name
                status
                totalHouseholdsCountWithValidPhoneNo
              }
            }
          }
        }
        """
    PAYMENT_PLAN_QUERY = """
      query PaymentPlan($id: ID!) {
        paymentPlan(id: $id) {
          name
          status
          canSendToPaymentGateway
          canCreateXlsxWithFspAuthCode
          fspCommunicationChannel
          canExportXlsx
          canDownloadXlsx
          canSendXlsxPassword
        }
      }
    """

    PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY = """
      query PaymentPlan($id: ID!) {
        paymentPlan(id: $id) {
          status
          availableFundsCommitments {
              fundsCommitmentNumber
              fundsCommitmentItems {
                  paymentPlan {
                      name
                  }
                  fundsCommitmentItem
                  recSerialNumber
              }
          }
          fundsCommitments {
              fundsCommitmentNumber
              insufficientAmount
          }
        }
      }
    """

    PAYMENT_PLAN_QUERY_WITH_TARGETING_CRITERIA = """
    query PaymentPlan($id: ID!) {
      paymentPlan(id: $id) {
        name
        status
        householdIds
        individualIds
        flagExcludeIfOnSanctionList
        flagExcludeIfActiveAdjudicationTicket
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create(username="qazxsw321")
        cls.create_user_role_with_permissions(
            cls.user,
            [Permissions.PM_VIEW_LIST, Permissions.PM_VIEW_DETAILS, Permissions.ACTIVITY_LOG_VIEW],
            cls.business_area,
        )

        with freeze_time("2020-10-10"):
            cls.cash_dm = DeliveryMechanism.objects.get(code="cash")
            program = RealProgramFactory(
                name="Test All PP QS",
                cycle__start_date=timezone.datetime(2020, 9, 10, tzinfo=utc).date(),
                cycle__end_date=timezone.datetime(2020, 11, 10, tzinfo=utc).date(),
            )
            cls.program_cycle = program.cycles.first()
            cls.financial_service_provider = FinancialServiceProviderFactory(
                communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
                payment_gateway_id="test123",
            )
            cls.pp = PaymentPlanFactory(
                name="Main Payment Plan",
                program_cycle=cls.program_cycle,
                dispersion_start_date=datetime(2020, 8, 10),
                dispersion_end_date=datetime(2020, 12, 10),
                is_follow_up=False,
                created_by=cls.user,
                currency="PLN",
                delivery_mechanism=cls.cash_dm,
                financial_service_provider=cls.financial_service_provider,
                exchange_rate=2.0,
            )
            cls.pp.unicef_id = "PP-01"
            cls.pp.save()
            referral_dm = DeliveryMechanism.objects.get(code="referral")
            PaymentVerificationSummaryFactory(payment_plan=cls.pp, status="ACTIVE")

            hoh1 = IndividualFactory(household=None)
            hoh2 = IndividualFactory(household=None)
            hh1 = HouseholdFactory(head_of_household=hoh1)
            hh2 = HouseholdFactory(head_of_household=hoh2)
            cls.p1 = PaymentFactory(
                parent=cls.pp,
                conflicted=False,
                household=hh1,
                head_of_household=hoh1,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                currency="PLN",
                fsp_auth_code="123",
            )
            cls.p2 = PaymentFactory(
                parent=cls.pp,
                conflicted=True,
                household=hh2,
                head_of_household=hoh2,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                currency="PLN",
                fsp_auth_code=None,
            )
            # create hard conflicted payment
            cls.pp_conflicted = PaymentPlanFactory(
                name="PaymentPlan with conflicts",
                program_cycle=cls.program_cycle,
                status=PaymentPlan.Status.LOCKED,
                dispersion_start_date=cls.pp.dispersion_start_date + relativedelta(months=2),
                dispersion_end_date=cls.pp.dispersion_end_date - relativedelta(months=2),
                created_by=cls.user,
                currency="UAH",
                delivery_mechanism=referral_dm,
                financial_service_provider=cls.financial_service_provider,
                exchange_rate=2.0,
            )
            cls.pp_conflicted.unicef_id = "PP-02"
            cls.pp_conflicted.save()

            PaymentFactory(
                parent=cls.pp_conflicted,
                household=cls.p2.household,
                conflicted=False,
                entitlement_quantity=100.00,
                entitlement_quantity_usd=200.00,
                delivered_quantity=50.00,
                delivered_quantity_usd=100.00,
                financial_service_provider=FinancialServiceProviderFactory(name="xxx"),
                currency="PLN",
                fsp_auth_code="789",
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
                fsp_auth_code="987",
            )

            IndividualFactory(household=hh1, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=5))
            IndividualFactory(household=hh1, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=5))
            IndividualFactory(household=hh2, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=20))
            IndividualFactory(household=hh2, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=20))

            AcceptanceProcessThreshold.objects.create(
                business_area=cls.business_area,
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

            PaymentPlanSupportingDocument.objects.create(
                payment_plan=cls.pp,
                title="Test File 123",
                file=InMemoryUploadedFile(
                    name="Test123.jpg",
                    file=BytesIO(b"abc"),
                    charset=None,
                    field_name="0",
                    size=10,
                    content_type="image/jpeg",
                ),
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
        from hct_mis_api.apps.account.models import UserRole

        role = UserRole.objects.get(user=self.user).role
        role.permissions.append("PM_VIEW_FSP_AUTH_CODE")
        role.save()

        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "paymentPlanId": encode_id_base64(self.pp.pk, "PaymentPlan")},
        )

    @freeze_time("2020-10-10")
    def test_fetch_all_payment_plans_filters(self) -> None:
        just_random_program_cycle = ProgramCycleFactory(program=self.pp.program)
        for filter_data in [
            {
                "totalEntitledQuantityFrom": float(self.pp_conflicted.total_entitled_quantity - 10),
                "totalEntitledQuantityTo": float(self.pp_conflicted.total_entitled_quantity + 10),
            },
            {
                "dispersionStartDate": self.pp_conflicted.dispersion_start_date,
                "dispersionEndDate": self.pp_conflicted.dispersion_end_date,
            },
            {"programCycle": encode_id_base64(self.pp.program_cycle.pk, "ProgramCycleNode")},
            {"programCycle": encode_id_base64(just_random_program_cycle.pk, "ProgramCycleNode")},
            {"search": self.pp.unicef_id},
            {"status": self.pp.status},
            {"serviceProvider": "test"},
            {"verificationStatus": ["ACTIVE", "FINISHED"]},
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
    def test_all_payment_plans_filter_by_delivery_types(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "program": encode_id_base64(self.pp.program.pk, "Program"),
                **{"deliveryTypes": ["cash", "referral"]},
            },
        )

    @freeze_time("2020-10-10")
    def test_filter_payment_plans_with_source_id(self) -> None:
        create_child_payment_plans(self.pp, self.user)

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
        create_child_payment_plans(self.pp, self.user)

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
        program = RealProgramFactory(
            cycle__start_date=timezone.datetime(2023, 9, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2023, 11, 10, tzinfo=utc).date(),
        )
        new_pp = PaymentPlanFactory(
            name="PaymentPlan with legacy data",
            program_cycle=program.cycles.first(),
            dispersion_start_date=datetime(2023, 8, 10),
            dispersion_end_date=datetime(2023, 12, 10),
            is_follow_up=False,
            created_by=self.user,
        )
        hoh_1 = IndividualFactory(household=None, given_name="First1", middle_name="Mid1", family_name="Last1")
        hoh_2 = IndividualFactory(household=None, given_name="First2", middle_name="Mid2", family_name="Last3")
        hoh_3 = IndividualFactory(household=None, given_name="First3", middle_name="Mid3", family_name="Last3")
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
            },
        }
        snapshot_data_hh3 = {
            "size": 55,
            "alternate_collector": {
                "full_name": "AlternateCollectorFullName",
                "payment_delivery_phone_no": "222222222",
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

    def test_all_payment_verification_log_entries(self) -> None:
        query = """
        query allPaymentVerificationLogEntries($objectId: UUID, $businessArea: String!) {
          allPaymentVerificationLogEntries(objectId: $objectId, businessArea: $businessArea) {
            totalCount
            edges {
              node {
                isUserGenerated
                action
              }
            }
          }
        }
        """
        payment_plan_id = str(self.pp.id)
        PaymentVerificationSummaryFactory(payment_plan=self.pp_conflicted)
        pvp = PaymentVerificationPlanFactory(payment_plan=self.pp)
        pvp2 = PaymentVerificationPlanFactory(payment_plan=self.pp_conflicted)
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=pvp,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(pvp),
            changes=create_diff(None, pvp, PaymentVerificationPlan.ACTIVITY_LOG_MAPPING),
        )
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=pvp2,
            user=self.user,
            business_area=self.business_area,
            object_repr=str(pvp2),
            changes=create_diff(None, pvp2, PaymentVerificationPlan.ACTIVITY_LOG_MAPPING),
        )

        self.snapshot_graphql_request(
            request_string=query,
            context={"user": self.user},
            variables={"objectId": payment_plan_id, "businessArea": "afghanistan"},
        )

    def test_payment_plan_filter_is_payment_plan(self) -> None:
        PaymentPlanFactory(
            name="Payment Plan within FINISHED status",
            status=PaymentPlan.Status.FINISHED,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=self.user,
        )
        PaymentPlanFactory(
            name="Payment Plan within TP_LOCK status",
            status=PaymentPlan.Status.TP_LOCKED,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=self.user,
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "isPaymentPlan": True},
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "isPaymentPlan": False},
        )

    def test_payment_plan_filter_is_target_population(self) -> None:
        PaymentPlanFactory(
            name="Payment Plan within TP_LOCK status",
            status=PaymentPlan.Status.TP_LOCKED,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=self.user,
        )
        PaymentPlanFactory(
            name="Payment Plan within DRAFT status",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=self.user,
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "isTargetPopulation": True},
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "isTargetPopulation": False},
        )

    def test_payment_plan_filter_name(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "name": "PaymentPlan with"},
        )

    def test_payment_plan_filter_total_households_count_max(self) -> None:
        pp_1 = PaymentPlanFactory(
            name="Payment Plan with 2 payments",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentFactory.create_batch(2, parent=pp_1)
        pp_2 = PaymentPlanFactory(
            name="Payment Plan with 5 payments",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentFactory.create_batch(5, parent=pp_2)
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "totalHouseholdsCountMax": 3},
        )

    def test_payment_plan_filter_total_households_count_min(self) -> None:
        pp_1 = PaymentPlanFactory(
            name="Payment Plan with 1 payments",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentFactory.create_batch(1, parent=pp_1)
        pp_2 = PaymentPlanFactory(
            name="Payment Plan with 3 payments",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentFactory.create_batch(3, parent=pp_2)
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "totalHouseholdsCountMin": 2},
        )

    def test_payment_plan_filter_total_households_count_with_valid_phone_no_min_2(self) -> None:
        valid_phone_no = "+48 123 456 987"
        invalid_phone_no = "+48 ABC"
        pp_with_2_valid_numbers = PaymentPlanFactory(
            name="Payment Plan with valid 2 phone numbers",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        hoh_1 = IndividualFactory(household=None, phone_no_valid=True, phone_no_alternative_valid=False)
        hoh_2 = IndividualFactory(
            household=None, phone_no_valid=False, phone_no_alternative_valid=True, phone_no_alternative=valid_phone_no
        )
        household_1 = HouseholdFactory(head_of_household=hoh_1)
        household_2 = HouseholdFactory(head_of_household=hoh_2)
        PaymentFactory(parent=pp_with_2_valid_numbers, household=household_1, head_of_household=hoh_1, currency="PLN")
        PaymentFactory(parent=pp_with_2_valid_numbers, household=household_2, head_of_household=hoh_2, currency="PLN")
        pp_2 = PaymentPlanFactory(
            name="Payment Plan with 2 payments and not valid phone numbers",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        household11 = HouseholdFactory(
            head_of_household=IndividualFactory(
                household=None, phone_no_valid=False, phone_no_alternative_valid=False, phone_no=invalid_phone_no
            )
        )
        household22 = HouseholdFactory(
            head_of_household=IndividualFactory(
                household=None, phone_no_valid=False, phone_no_alternative_valid=False, phone_no=invalid_phone_no
            )
        )
        PaymentFactory(parent=pp_2, household=household11, head_of_household=household11.head_of_household)
        PaymentFactory(parent=pp_2, household=household22, head_of_household=household22.head_of_household)
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "totalHouseholdsCountWithValidPhoneNoMin": 2},
        )

    def test_payment_plan_filter_total_households_count_with_valid_phone_no_max_2(self) -> None:
        valid_phone_no = "+48 123 456 777"
        invalid_phone_no = "+48 TEST"
        pp_with_3_valid_numbers = PaymentPlanFactory(
            name="Payment Plan with valid 3 phone numbers",
            status=PaymentPlan.Status.DRAFT,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        hoh_1 = IndividualFactory(household=None, phone_no_valid=True, phone_no_alternative_valid=False)
        hoh_2 = IndividualFactory(
            household=None, phone_no_valid=False, phone_no_alternative_valid=True, phone_no_alternative=valid_phone_no
        )
        hoh_3 = IndividualFactory(household=None, phone_no_valid=True, phone_no_alternative_valid=False)
        household_1 = HouseholdFactory(head_of_household=hoh_1)
        household_2 = HouseholdFactory(head_of_household=hoh_2)
        household_3 = HouseholdFactory(head_of_household=hoh_3)
        PaymentFactory(parent=pp_with_3_valid_numbers, household=household_1, head_of_household=hoh_1, currency="PLN")
        PaymentFactory(parent=pp_with_3_valid_numbers, household=household_2, head_of_household=hoh_2, currency="PLN")
        PaymentFactory(parent=pp_with_3_valid_numbers, household=household_3, head_of_household=hoh_3, currency="PLN")
        pp_with_2_valid_numbers = PaymentPlanFactory(
            name="Payment Plan with valid 2 phone numbers",
            status=PaymentPlan.Status.TP_LOCKED,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        hoh_4 = IndividualFactory(
            household=None, phone_no_valid=False, phone_no_alternative_valid=True, phone_no_alternative=valid_phone_no
        )
        hoh_5 = IndividualFactory(household=None, phone_no_valid=True, phone_no_alternative_valid=False)
        household_4 = HouseholdFactory(head_of_household=hoh_4)
        household_5 = HouseholdFactory(head_of_household=hoh_5)
        PaymentFactory(parent=pp_with_2_valid_numbers, household=household_4, head_of_household=hoh_4, currency="PLN")
        PaymentFactory(parent=pp_with_2_valid_numbers, household=household_5, head_of_household=hoh_5, currency="PLN")
        pp = PaymentPlanFactory(
            name="Payment Plan just random with invalid phone numbers",
            status=PaymentPlan.Status.TP_PROCESSING,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        household11 = HouseholdFactory(
            head_of_household=IndividualFactory(
                household=None, phone_no_valid=False, phone_no_alternative_valid=False, phone_no=invalid_phone_no
            )
        )
        household22 = HouseholdFactory(
            head_of_household=IndividualFactory(
                household=None, phone_no_valid=False, phone_no_alternative_valid=False, phone_no=invalid_phone_no
            )
        )
        PaymentFactory(parent=pp, household=household11, head_of_household=household11.head_of_household)
        PaymentFactory(parent=pp, household=household22, head_of_household=household22.head_of_household)
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "totalHouseholdsCountWithValidPhoneNoMax": 2},
        )

    def test_payment_plan_filter_not_status(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "statusNot": "OPEN"},
        )

    def test_payment_plan_filter_status_assigned(self) -> None:
        PaymentPlanFactory(
            name="NEW TP OPEN",
            status=PaymentPlan.Status.TP_OPEN,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        PaymentPlanFactory(
            name="TP Processing",
            status=PaymentPlan.Status.TP_PROCESSING,
            program_cycle=self.program_cycle,
            business_area=self.business_area,
            created_by=self.user,
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "program": encode_id_base64(self.pp.program.pk, "Program"),
                "status": ["TP_OPEN", "ASSIGNED"],
            },
        )
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLANS_FILTER_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "program": encode_id_base64(self.pp.program.pk, "Program"),
                "status": ["TP_OPEN"],
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission_api",
                [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE, Permissions.PM_SEND_XLSX_PASSWORD],
                FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            ),
            ("without_permission_api", [], FinancialServiceProvider.COMMUNICATION_CHANNEL_API),
            (
                "with_permission_xlsx",
                [Permissions.PM_DOWNLOAD_FSP_AUTH_CODE, Permissions.PM_SEND_XLSX_PASSWORD],
                FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            ),
            ("without_permission_xlsx", [], FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX),
        ]
    )
    @freeze_time("2020-10-10")
    def test_payment_plans_export_download_properties(
        self, _: Any, permissions: List[Permissions], communication_channel: str
    ) -> None:
        user = UserFactory.create(username="abc")
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        fsp = FinancialServiceProviderFactory(
            communication_channel=communication_channel,
            payment_gateway_id="1243",
        )
        payment_plan = PaymentPlanFactory(
            name="Test Finished PP",
            status=PaymentPlan.Status.FINISHED,
            program_cycle=self.program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=user,
            currency="PLN",
            financial_service_provider=fsp,
            delivery_mechanism=self.cash_dm,
        )

        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY,
            context={"user": user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

    @freeze_time("2020-10-10")
    def test_all_payments_filter_by_household_id(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PAYMENTS_QUERY,
            context={"user": self.user},
            variables={
                "businessArea": "afghanistan",
                "householdId": encode_id_base64(self.p1.household_id, "Household"),
            },
        )

    @freeze_time("2020-10-10")
    def test_payment_plans_with_targeting_criteria(self) -> None:
        payment_plan = PaymentPlanFactory(
            name="Test PP with TargetingCriteria",
            status=PaymentPlan.Status.TP_OPEN,
            program_cycle=self.program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            is_follow_up=False,
            created_by=self.user,
            currency="PLN",
        )
        TargetingCriteriaRuleFactory(
            payment_plan=payment_plan,
            household_ids="HH-1, HH-2",
            individual_ids="IND-01, IND-02",
        )

        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_WITH_TARGETING_CRITERIA,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encode_id_base64(payment_plan.id, "PaymentPlan")},
        )

    @freeze_time("2020-10-10")
    def test_payment_plan_funds_commitments(self) -> None:
        payment_plan = PaymentPlanFactory(
            name="FC TEST",
            status=PaymentPlan.Status.IN_REVIEW,
            program_cycle=self.program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            created_by=self.user,
            currency="PLN",
            total_entitled_quantity=200,
            total_entitled_quantity_usd=100,
        )

        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")

        # 1
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="123",
            funds_commitment_item="001",
            rec_serial_number="0001",
            commitment_amount_local=50,
            commitment_amount_usd=50,
            currency_code="PLN",
        )
        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="123",
            funds_commitment_item="002",
            rec_serial_number="0002",
            commitment_amount_local=160,
            commitment_amount_usd=50,
            currency_code="PLN",
        )
        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="345",
            funds_commitment_item="001",
            rec_serial_number="0003",
            commitment_amount_local=50,
            commitment_amount_usd=50,
            currency_code="UYU",
        )
        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="345",
            funds_commitment_item="002",
            rec_serial_number="0004",
            commitment_amount_local=50,
            commitment_amount_usd=50,
            currency_code="UYU",
        )
        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="678",
            funds_commitment_item="001",
            rec_serial_number="0005",
            commitment_amount_local=50,
            commitment_amount_usd=30,
            currency_code="UYU",
        )
        FundsCommitmentFactory(
            business_area=self.business_area.code,
            funds_commitment_number="678",
            funds_commitment_item="002",
            rec_serial_number="0006",
            commitment_amount_local=50,
            commitment_amount_usd=80,
            currency_code="PLN",
        )

        # 2
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        fc1 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="123", funds_commitment_item="001"
        )
        fc1.payment_plan = payment_plan
        fc1.save()
        # 3 insufficientAmount True, local
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        fc2 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="123", funds_commitment_item="002"
        )
        fc2.payment_plan = payment_plan
        fc2.save()
        # 4 insufficientAmount False, local
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        payment_plan2 = PaymentPlanFactory(
            name="FC TEST2",
            status=PaymentPlan.Status.IN_REVIEW,
            program_cycle=self.program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            created_by=self.user,
            currency="PLN",
            total_entitled_quantity=200,
            total_entitled_quantity_usd=100,
        )
        encoded_payment_plan_id = encode_id_base64(payment_plan2.id, "PaymentPlan")

        fc3 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="345", funds_commitment_item="001"
        )
        fc3.payment_plan = payment_plan2
        fc3.save()
        # 5 insufficientAmount True, currency not match -> usd
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        fc4 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="345", funds_commitment_item="002"
        )
        fc4.payment_plan = payment_plan2
        fc4.save()
        # 6 insufficientAmount False, currency not match -> usd
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        payment_plan3 = PaymentPlanFactory(
            name="FC TEST3",
            status=PaymentPlan.Status.IN_REVIEW,
            program_cycle=self.program_cycle,
            dispersion_start_date=datetime(2020, 8, 10),
            dispersion_end_date=datetime(2020, 12, 10),
            created_by=self.user,
            currency="PLN",
            total_entitled_quantity=200,
            total_entitled_quantity_usd=100,
        )
        encoded_payment_plan_id = encode_id_base64(payment_plan3.id, "PaymentPlan")

        fc5 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="678", funds_commitment_item="001"
        )
        fc5.payment_plan = payment_plan3
        fc5.save()
        # 7 insufficientAmount True, more than 1 currency -> usd
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )

        fc6 = FundsCommitmentItem.objects.get(
            funds_commitment_group__funds_commitment_number="678", funds_commitment_item="002"
        )
        fc6.payment_plan = payment_plan3
        fc6.save()
        # insufficientAmount False, more than 1 currency -> usd
        self.snapshot_graphql_request(
            request_string=self.PAYMENT_PLAN_QUERY_FUNDS_COMMITMENTS_QUERY,
            context={"user": self.user},
            variables={"businessArea": "afghanistan", "id": encoded_payment_plan_id},
        )
