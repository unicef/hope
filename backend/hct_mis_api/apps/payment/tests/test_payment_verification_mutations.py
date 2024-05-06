from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.utils import timezone

from graphql import GraphQLError
from graphql.execution.base import ResolveInfo
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestPaymentVerificationMutations(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        payment_record_amount = 1
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.user = UserFactory()
        cls.create_user_role_with_permissions(
            cls.user,
            Permissions,
            cls.business_area,
        )
        program = ProgramFactory(business_area=cls.business_area)
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=cls.user, targeting_criteria=targeting_criteria, business_area=cls.business_area
        )
        cash_plan = CashPlanFactory(program=program, business_area=cls.business_area)
        cash_plan.save()
        payment_verification_plan = PaymentVerificationPlanFactory(
            generic_fk_obj=cash_plan, verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL
        )
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=cls.user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                parent=cash_plan,
                household=household,
                head_of_household=household.head_of_household,
                target_population=target_population,
                entitlement_quantity="21.36",
                delivered_quantity="21.36",
                currency="PLN",
            )

            PaymentVerificationFactory(
                generic_fk_obj=payment_record,
                payment_verification_plan=payment_verification_plan,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.payment_verification_plan.first()
        VerificationPlanStatusChangeServices(payment_verification_plan).activate()
        info = ResolveInfo(None, None, None, None, None, None, None, None, None, None)
        request = RequestFactory().get("/api/graphql")
        request.user = cls.user
        info.context = request
        cls.info = info

    @parameterized.expand(
        [
            ("21.36", True, PaymentVerification.STATUS_RECEIVED),
            ("21.35", True, PaymentVerification.STATUS_RECEIVED_WITH_ISSUES),
            ("0", False, PaymentVerification.STATUS_NOT_RECEIVED),
        ]
    )
    def test_update_payment_verification_received_and_received_amount(
        self, received_amount: str, received: bool, status: str
    ) -> None:
        from hct_mis_api.apps.payment.mutations import (
            UpdatePaymentVerificationReceivedAndReceivedAmount,
        )

        payment_verification = self.verification.payment_record_verifications.first()
        self.assertIsNone(payment_verification.received_amount)
        self.assertEqual(payment_verification.status, PaymentVerification.STATUS_PENDING)
        payment_verification_id = encode_id_base64_required(payment_verification.id, "PaymentVerification")
        UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
            None, self.info, payment_verification_id, received_amount=Decimal(received_amount), received=received
        )
        payment_verification.refresh_from_db()
        self.assertEqual(payment_verification.received_amount, Decimal(received_amount))
        self.assertEqual(payment_verification.status, status)

    def test_update_payment_verification_received_and_received_amount_update_time_restricted(self) -> None:
        from hct_mis_api.apps.payment.mutations import (
            UpdatePaymentVerificationReceivedAndReceivedAmount,
        )

        payment_verification = self.verification.payment_record_verifications.first()
        payment_verification_id = encode_id_base64_required(payment_verification.id, "PaymentVerification")
        payment_verification.status = PaymentVerification.STATUS_RECEIVED
        payment_verification.status_date = timezone.now() - timedelta(minutes=11)
        payment_verification.save()
        with self.assertRaisesMessage(GraphQLError, "You can only edit payment verification in first 10 minutes"):
            UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
                None,
                self.info,
                payment_verification_id,
                received_amount=Decimal(21.36),
                received=True,
            )
        payment_verification.status_date = timezone.now() - timedelta(minutes=9)
        payment_verification.save()
        UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
            None,
            self.info,
            payment_verification_id,
            received_amount=Decimal(21.36),
            received=True,
        )

    def test_update_payment_verification_received_and_received_amount_payment_status(self) -> None:
        from hct_mis_api.apps.payment.mutations import (
            UpdatePaymentVerificationReceivedAndReceivedAmount,
        )

        payment_verification = self.verification.payment_record_verifications.first()
        payment_verification_id = encode_id_base64_required(payment_verification.id, "PaymentVerification")
        self.verification.status = PaymentVerificationPlan.STATUS_FINISHED
        self.verification.save()
        with self.assertRaisesMessage(
            GraphQLError, "You can only update status of payment verification for ACTIVE cash plan verification"
        ):
            UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
                None,
                self.info,
                payment_verification_id,
                received_amount=Decimal(21.36),
                received=True,
            )

    @parameterized.expand(
        [
            ("21.36", False, "If received_amount(21.36) is not 0, you should set received to YES"),
            ("0", True, "If 'Amount Received' equals to 0, please set status as 'Not Received'"),
        ]
    )
    def test_update_payment_verification_received_and_received_amount_incorrect_arguments(
        self, received_amount: str, received: bool, message: str
    ) -> None:
        from hct_mis_api.apps.payment.mutations import (
            UpdatePaymentVerificationReceivedAndReceivedAmount,
        )

        payment_verification = self.verification.payment_record_verifications.first()
        payment_verification_id = encode_id_base64_required(payment_verification.id, "PaymentVerification")
        with self.assertRaisesMessage(GraphQLError, message):
            UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
                None,
                self.info,
                payment_verification_id,
                received_amount=Decimal(received_amount),
                received=received,
            )

    def test_permissions(self) -> None:
        from hct_mis_api.apps.payment.mutations import (
            UpdatePaymentVerificationReceivedAndReceivedAmount,
        )

        info = ResolveInfo(None, None, None, None, None, None, None, None, None, None)
        request = RequestFactory().get("/api/graphql")
        request.user = UserFactory()
        info.context = request
        payment_verification = self.verification.payment_record_verifications.first()
        payment_verification_id = encode_id_base64_required(payment_verification.id, "PaymentVerification")
        with self.assertRaises(PermissionDenied):
            UpdatePaymentVerificationReceivedAndReceivedAmount().mutate(
                None, info, payment_verification_id, received_amount=Decimal(21.36), received=True
            )
