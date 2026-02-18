from typing import Any
from unittest.mock import MagicMock, patch
import uuid

from django.core.cache import cache
import pytest
import requests
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    AreaFactory,
    BusinessAreaFactory,
    EntitlementCardFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.payment.services.verification_plan_crud_services import does_payment_record_have_right_hoh_phone_number
from hope.apps.payment.services.verification_plan_status_change_services import VerificationPlanStatusChangeServices
from hope.models import PaymentVerification, PaymentVerificationPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program(business_area: Any) -> Any:
    program = ProgramFactory(business_area=business_area)
    program.admin_areas.set([AreaFactory(), AreaFactory(), AreaFactory()])
    return program


@pytest.fixture
def rapidpro_verification_setup(business_area: Any, user: Any, program: Any) -> dict[str, Any]:
    payment_record_amount = 2

    cycle = ProgramCycleFactory(program=program)
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        created_by=user,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    cash_plan_payment_verification = PaymentVerificationPlanFactory(
        status=PaymentVerificationPlan.STATUS_PENDING,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
        payment_plan=payment_plan,
    )
    individuals = []
    version_key = f":1:{business_area.slug}:1:{program.slug}:registration_data_import_list"
    cache.set(version_key, 1)
    for i in range(payment_record_amount):
        registration_data_import = RegistrationDataImportFactory(
            imported_by=user,
            business_area=business_area,
            program=program,
        )
        household = HouseholdFactory(
            registration_data_import=registration_data_import,
            admin2=AreaFactory(),
            program=program,
            business_area=business_area,
        )
        head = household.head_of_household
        head.phone_no = f"+48 609 999 {i:03d}"
        head.save(update_fields=["phone_no"])
        individuals.append(head)

        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            head_of_household=head,
            collector=head,
            delivered_quantity=200,
            currency="PLN",
        )

        PaymentVerificationFactory(
            payment_verification_plan=cash_plan_payment_verification,
            payment=payment,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=household)

    other_program = ProgramFactory(business_area=business_area)
    other_program.admin_areas.set([AreaFactory(), AreaFactory(), AreaFactory()])
    other_cycle = ProgramCycleFactory(program=other_program)
    other_payment_plan = PaymentPlanFactory(
        program_cycle=other_cycle,
        business_area=business_area,
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
            imported_by=user,
            business_area=business_area,
            program=other_program,
        )
        other_household = HouseholdFactory(
            registration_data_import=other_registration_data_import,
            admin2=AreaFactory(),
            program=other_program,
            business_area=business_area,
        )
        other_individuals.append(other_household.head_of_household)

        other_payment_record = PaymentFactory(
            parent=other_payment_plan,
            household=other_household,
            head_of_household=other_household.head_of_household,
            collector=other_household.head_of_household,
            delivered_quantity=200,
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


def test_failing_rapid_pro_during_cash_plan_payment_verification(
    rapidpro_verification_setup: dict[str, Any],
) -> None:
    verification = rapidpro_verification_setup["verification"]
    other_verification = rapidpro_verification_setup["other_verification"]
    payment_record_amount = rapidpro_verification_setup["payment_record_amount"]

    assert verification.status == PaymentVerification.STATUS_PENDING
    assert verification.error is None
    assert verification.payment_record_verifications.count() == payment_record_amount

    def create_flow_response() -> dict[str, Any]:
        return {
            "uuid": str(uuid.uuid4()),
        }

    first_flow = create_flow_response()

    post_request_mock = MagicMock()
    post_request_mock.side_effect = [first_flow, requests.exceptions.HTTPError("TEST")]

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


def test_does_payment_record_have_right_hoh_phone_number(
    rapidpro_verification_setup: dict[str, Any],
) -> None:
    payment_plan = rapidpro_verification_setup["payment_plan"]
    individuals = rapidpro_verification_setup["individuals"]

    household = HouseholdFactory(
        program=payment_plan.program_cycle.program,
        business_area=payment_plan.business_area,
    )
    payment_without_hoh = PaymentFactory(
        parent=payment_plan,
        household=household,
        head_of_household=None,
        collector=household.head_of_household,
    )

    result = does_payment_record_have_right_hoh_phone_number(payment_without_hoh)
    assert result is False

    hoh = individuals[0]
    assert hoh.phone_no_valid is True
    payment_with_hoh_phone_no_valid = PaymentFactory(
        parent=payment_plan,
        household=HouseholdFactory(
            program=payment_plan.program_cycle.program,
            business_area=payment_plan.business_area,
        ),
        head_of_household=hoh,
        collector=hoh,
    )
    result = does_payment_record_have_right_hoh_phone_number(payment_with_hoh_phone_no_valid)
    assert result is True


def test_export_xlsx_validation_if_no_records(
    business_area: Any,
    user: Any,
    program: Any,
) -> None:
    payment_plan = PaymentPlanFactory(
        program_cycle=ProgramCycleFactory(program=program),
        business_area=business_area,
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

    with pytest.raises(ValidationError) as exc:
        service.export_xlsx(str(user.pk))
    assert "Not possible to export with no records" in str(exc.value)
