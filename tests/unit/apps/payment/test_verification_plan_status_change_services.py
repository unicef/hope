from typing import Dict
from unittest.mock import MagicMock, patch
import uuid

from django.core.cache import cache
import pytest
import requests
from rest_framework.exceptions import ValidationError

from extras.test_utils.old_factories.account import UserFactory
from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.household import (
    EntitlementCardFactory,
    create_household,
)
from extras.test_utils.old_factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.old_factories.program import ProgramFactory
from extras.test_utils.old_factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.payment.services.verification_plan_crud_services import does_payment_record_have_right_hoh_phone_number
from hope.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hope.models import Area, PaymentVerification, PaymentVerificationPlan


@pytest.fixture
def afghanistan():
    return create_afghanistan()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(afghanistan):
    program = ProgramFactory(business_area=afghanistan)
    program.admin_areas.set(Area.objects.order_by("?")[:3])
    return program


@pytest.fixture
def rapidpro_verification_setup(afghanistan, user, program):
    """Setup for RapidPro verification tests - creates 2 records for batching test."""
    payment_record_amount = 2

    payment_plan = PaymentPlanFactory(
        program_cycle=program.cycles.first(),
        business_area=afghanistan,
        created_by=user,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    cash_plan_payment_verification = PaymentVerificationPlanFactory(
        status=PaymentVerificationPlan.STATUS_PENDING,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
        payment_plan=payment_plan,
    )
    individuals = []
    version_key = f":1:afghanistan:1:{program.slug}:registration_data_import_list"
    cache.set(version_key, 1)
    for i in range(payment_record_amount):
        registration_data_import = RegistrationDataImportFactory(
            imported_by=user, business_area=afghanistan, program=program
        )
        household, indivs = create_household(
            {
                "registration_data_import": registration_data_import,
                "admin2": Area.objects.order_by("?").first(),
                "program": program,
            },
            {
                "registration_data_import": registration_data_import,
                "phone_no": f"+48 609 999 {i:03d}",
            },
        )
        individuals.append(indivs[0])

        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            head_of_household=household.head_of_household,
            delivered_quantity_usd=200,
            currency="PLN",
        )

        PaymentVerificationFactory(
            payment_verification_plan=cash_plan_payment_verification,
            payment=payment,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=household)

    # Other program setup
    other_program = ProgramFactory(business_area=afghanistan)
    other_program.admin_areas.set(Area.objects.order_by("?")[:3])

    other_payment_plan = PaymentPlanFactory(
        program_cycle=other_program.cycles.first(),
        business_area=afghanistan,
        created_by=user,
    )
    PaymentVerificationSummaryFactory(payment_plan=other_payment_plan)
    other_payment_plan_payment_verification = PaymentVerificationPlanFactory(
        status=PaymentVerificationPlan.STATUS_PENDING,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
        payment_plan=other_payment_plan,
    )
    other_individuals = []
    for _ in range(payment_record_amount):
        other_registration_data_import = RegistrationDataImportFactory(
            imported_by=user, business_area=afghanistan, program=other_program
        )
        other_household, other_indivs = create_household(
            {
                "registration_data_import": other_registration_data_import,
                "admin2": Area.objects.order_by("?").first(),
                "program": other_program,
            },
            {"registration_data_import": other_registration_data_import},
        )
        other_individuals.append(other_indivs[0])

        other_payment_record = PaymentFactory(
            parent=other_payment_plan,
            household=other_household,
            head_of_household=other_household.head_of_household,
            delivered_quantity_usd=200,
            currency="PLN",
        )

        PaymentVerificationFactory(
            payment_verification_plan=other_payment_plan_payment_verification,
            payment=other_payment_record,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=other_household)

    return {
        "payment_record_amount": payment_record_amount,
        "payment_plan": payment_plan,
        "verification": payment_plan.payment_verification_plans.first(),
        "individuals": individuals,
        "other_payment_plan": other_payment_plan,
        "other_verification": other_payment_plan.payment_verification_plans.first(),
        "other_individuals": other_individuals,
    }


@pytest.mark.django_db
class TestPhoneNumberVerification:
    def test_failing_rapid_pro_during_cash_plan_payment_verification(self, rapidpro_verification_setup) -> None:
        setup = rapidpro_verification_setup
        verification = setup["verification"]
        other_verification = setup["other_verification"]
        payment_record_amount = setup["payment_record_amount"]

        assert verification.status == PaymentVerification.STATUS_PENDING
        assert verification.error is None
        assert verification.payment_record_verifications.count() == payment_record_amount

        def create_flow_response() -> Dict:
            return {
                "uuid": str(uuid.uuid4()),
            }

        first_flow = create_flow_response()

        post_request_mock = MagicMock()
        post_request_mock.side_effect = [first_flow, requests.exceptions.HTTPError("TEST")]

        # Patch MAX_URNS_PER_REQUEST to 1 so we test batching with only 2 records
        with (
            patch.object(RapidProAPI, "MAX_URNS_PER_REQUEST", 1),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI._handle_post_request",
                post_request_mock,
            ),
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                VerificationPlanStatusChangeServices(verification).activate()

        verification.refresh_from_db()
        assert verification.status == PaymentVerificationPlan.STATUS_RAPID_PRO_ERROR
        assert verification.error is not None

        # All records should still be pending
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
            ).count()
            == payment_record_amount
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
            ).count()
            == payment_record_amount
        )
        # First batch (1 record) was sent successfully
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count()
            == 1
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count()
            == 0
        )
        # Second batch (1 record) failed
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count()
            == 1
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count()
            == payment_record_amount
        )

        # Now retry - should succeed
        post_request_mock = MagicMock()
        post_request_mock.side_effect = [first_flow, create_flow_response()]
        with (
            patch.object(RapidProAPI, "MAX_URNS_PER_REQUEST", 1),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
                MagicMock(return_value=None),
            ),
            patch(
                "hope.apps.core.services.rapid_pro.api.RapidProAPI._handle_post_request",
                post_request_mock,
            ),
        ):
            VerificationPlanStatusChangeServices(verification).activate()

        verification.refresh_from_db()
        assert verification.status == PaymentVerificationPlan.STATUS_ACTIVE
        assert verification.error is None

        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
            ).count()
            == payment_record_amount
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
            ).count()
            == payment_record_amount
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count()
            == payment_record_amount
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count()
            == 0
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count()
            == 0
        )
        assert (
            PaymentVerification.objects.filter(
                payment_verification_plan=other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count()
            == payment_record_amount
        )

    def test_does_payment_record_have_right_hoh_phone_number(self, rapidpro_verification_setup) -> None:
        setup = rapidpro_verification_setup
        payment_plan = setup["payment_plan"]
        individuals = setup["individuals"]

        payment_without_hoh = PaymentFactory(
            parent=payment_plan,
            head_of_household=None,
        )

        result = does_payment_record_have_right_hoh_phone_number(payment_without_hoh)
        assert result is False

        hoh = individuals[0]
        assert hoh.phone_no_valid is True
        payment_with_hoh_phone_no_valid = PaymentFactory(
            parent=payment_plan,
            head_of_household=hoh,
        )
        result = does_payment_record_have_right_hoh_phone_number(payment_with_hoh_phone_no_valid)
        assert result is True

    def test_export_xlsx_validation_if_no_records(self, afghanistan, user, program) -> None:
        """Test that export fails gracefully when there are no records to export."""
        payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            business_area=afghanistan,
            created_by=user,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        pvp = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_ACTIVE,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_XLSX,
            payment_plan=payment_plan,
        )
        assert pvp.payment_record_verifications.count() == 0
        service = VerificationPlanStatusChangeServices(pvp)

        with pytest.raises(ValidationError) as e:
            service.export_xlsx(str(user.pk))
        assert "Not possible to export with no records" in str(e.value)
