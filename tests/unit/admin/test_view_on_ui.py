from types import SimpleNamespace
from typing import Any

from django.conf import settings
from django.contrib.admin import site
import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    CommunicationMessageFactory,
    DataCollectingTypeFactory,
    FeedbackFactory,
    FollowUpInstructionFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PDUOnlineEditFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SurveyFactory,
)
from hope.admin.utils import ViewOnUiMixin
from hope.apps.grievance.models import GrievanceTicket
from hope.models import (
    DataCollectingType,
    Feedback,
    FollowUpInstruction,
    Household,
    Individual,
    Message,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
    PaymentVerification,
    PaymentVerificationPlan,
    PDUOnlineEdit,
    Program,
    ProgramCycle,
    RegistrationDataImport,
    Survey,
)

pytestmark = pytest.mark.unit


def _button(original: Any) -> SimpleNamespace:
    return SimpleNamespace(original=original, href=None)


def _handler(model: Any) -> Any:
    ma = site._registry[model]
    ma.get_urls()
    return ma.extra_button_handlers["view_on_ui"]


@pytest.fixture
def program():
    def factory(**kwargs: Any) -> Program:
        return ProgramFactory.create(code="TEST", business_area=BusinessAreaFactory(name="AFG"), **kwargs)

    return factory


@pytest.fixture
def cycle():
    def factory(program: Program) -> ProgramCycle:
        return ProgramCycleFactory.create(program=program)

    return factory


@pytest.mark.django_db
def test_frontend_url_program(program):
    assert site._registry[Program].frontend_url(program()) == "/afg/programs/TEST/details/TEST"


@pytest.mark.django_db
def test_frontend_url_household(program):
    program = program()
    household = HouseholdFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[Household].frontend_url(household) == f"/afg/programs/TEST/population/household/{household.id}"
    )


@pytest.mark.django_db
def test_frontend_url_individual(program):
    program = program()
    individual = IndividualFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[Individual].frontend_url(individual)
        == f"/afg/programs/TEST/population/individuals/{individual.id}"
    )


@pytest.mark.django_db
def test_frontend_url_individual_social(program):
    program = program(
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL),
        beneficiary_group=BeneficiaryGroupFactory(master_detail=False),
    )
    individual = IndividualFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[Individual].frontend_url(individual) == f"/afg/programs/TEST/population/people/{individual.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment_plan(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()))
    assert (
        site._registry[PaymentPlan].frontend_url(plan) == f"/afg/programs/TEST/payment-module/payment-plans/{plan.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment_plan_pre_payment_status(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()), status=PaymentPlan.Status.TP_OPEN)
    assert site._registry[PaymentPlan].frontend_url(plan) == f"/afg/programs/TEST/target-population/{plan.id}"


@pytest.mark.django_db
def test_frontend_url_payment_plan_follow_up(program, cycle):
    plan = PaymentPlanFactory(
        program_cycle=cycle(program()),
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    assert (
        site._registry[PaymentPlan].frontend_url(plan)
        == f"/afg/programs/TEST/payment-module/followup-payment-plans/{plan.id}"
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "plan_type",
    [PaymentPlan.PlanType.TOP_UP, PaymentPlan.PlanType.TOP_UP_AMENDMENT],
)
def test_frontend_url_payment_plan_top_up(plan_type, program, cycle):
    plan = PaymentPlanFactory(
        program_cycle=cycle(program()),
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=plan_type,
    )
    assert (
        site._registry[PaymentPlan].frontend_url(plan)
        == f"/afg/programs/TEST/payment-module/top-up-payment-plans/{plan.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment(program, cycle):
    program = program()
    plan = PaymentPlanFactory(program_cycle=cycle(program))
    payment = PaymentFactory(parent=plan, program=program)
    assert site._registry[Payment].frontend_url(payment) == f"/afg/programs/TEST/payment-module/payments/{payment.id}"


@pytest.mark.django_db
def test_frontend_url_payment_plan_group(program, cycle):
    group = PaymentPlanGroupFactory(cycle=cycle(program()))
    assert (
        site._registry[PaymentPlanGroup].frontend_url(group) == f"/afg/programs/TEST/payment-module/groups/{group.id}"
    )


@pytest.mark.django_db
def test_frontend_url_program_cycle(program, cycle):
    cycle = cycle(program())
    assert (
        site._registry[ProgramCycle].frontend_url(cycle)
        == f"/afg/programs/TEST/payment-module/program-cycles/{cycle.id}"
    )


@pytest.mark.django_db
def test_frontend_url_registration_data_import(program):
    program = program()
    rdi = RegistrationDataImportFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[RegistrationDataImport].frontend_url(rdi)
        == f"/afg/programs/TEST/registration-data-import/{rdi.id}"
    )


@pytest.mark.django_db
def test_frontend_url_survey(program):
    program = program()
    survey = SurveyFactory(program=program, business_area=program.business_area)
    assert site._registry[Survey].frontend_url(survey) == f"/afg/programs/TEST/accountability/surveys/{survey.id}"


@pytest.mark.django_db
def test_frontend_url_message(program):
    program = program()
    message = CommunicationMessageFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[Message].frontend_url(message) == f"/afg/programs/TEST/accountability/communication/{message.id}"
    )


@pytest.mark.django_db
def test_frontend_url_grievance_ticket(program):
    program = program()
    ticket = GrievanceTicketFactory(business_area=program.business_area)
    ticket.programs.add(program)
    assert (
        site._registry[GrievanceTicket].frontend_url(ticket)
        == f"/afg/programs/TEST/grievance/tickets/user-generated/{ticket.id}"
    )


@pytest.mark.django_db
def test_frontend_url_grievance_ticket_system_generated(program):
    program = program()
    ticket = GrievanceTicketFactory(
        business_area=program.business_area,
        category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        issue_type=None,
    )
    ticket.programs.add(program)
    assert (
        site._registry[GrievanceTicket].frontend_url(ticket)
        == f"/afg/programs/TEST/grievance/tickets/system-generated/{ticket.id}"
    )


@pytest.mark.django_db
def test_frontend_url_grievance_ticket_without_program():
    ticket = GrievanceTicketFactory(business_area=BusinessAreaFactory(name="AFG"))
    assert (
        site._registry[GrievanceTicket].frontend_url(ticket)
        == f"/afg/programs/all/grievance/tickets/user-generated/{ticket.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment_verification_plan(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()), status=PaymentPlan.Status.FINISHED)
    verification_plan = PaymentVerificationPlanFactory(payment_plan=plan)
    assert (
        site._registry[PaymentVerificationPlan].frontend_url(verification_plan)
        == f"/afg/programs/TEST/payment-verification/payment-plan/{plan.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment_without_program(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()))
    payment = PaymentFactory(parent=plan)
    assert site._registry[Payment].frontend_url(payment) is None


@pytest.mark.django_db
def test_frontend_url_rdi_without_program(program):
    program = program()
    rdi = RegistrationDataImportFactory(program=program, business_area=program.business_area)
    rdi.program = None
    assert site._registry[RegistrationDataImport].frontend_url(rdi) is None


@pytest.mark.django_db
def test_frontend_url_survey_without_program(program):
    program = program()
    survey = SurveyFactory(program=None, business_area=program.business_area)
    assert site._registry[Survey].frontend_url(survey) is None


@pytest.mark.django_db
def test_frontend_url_message_without_program(program):
    program = program()
    message = CommunicationMessageFactory(program=None, business_area=program.business_area)
    assert site._registry[Message].frontend_url(message) is None


def test_frontend_url_base_not_implemented():
    with pytest.raises(NotImplementedError):
        ViewOnUiMixin().frontend_url(object())


@pytest.mark.django_db
def test_view_on_ui_sets_href(program):
    btn = _button(program())
    _handler(Program).func(site._registry[Program], btn)
    protocol = "https" if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS else "http"
    assert btn.href == f"{protocol}://{settings.FRONTEND_HOST}/afg/programs/TEST/details/TEST"


@pytest.mark.django_db
def test_view_on_ui_without_original():
    btn = _button(None)
    _handler(Program).func(site._registry[Program], btn)
    assert btn.href is None


@pytest.mark.django_db
def test_view_on_ui_without_frontend_url(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()))
    payment = PaymentFactory(parent=plan)
    btn = _button(payment)
    _handler(Payment).func(site._registry[Payment], btn)
    assert btn.href is None


@pytest.mark.django_db
def test_frontend_url_feedback(program):
    program = program()
    feedback = FeedbackFactory(program=program, business_area=program.business_area)
    assert site._registry[Feedback].frontend_url(feedback) == f"/afg/programs/TEST/grievance/feedback/{feedback.id}"


@pytest.mark.django_db
def test_frontend_url_feedback_without_program():
    feedback = FeedbackFactory(business_area=BusinessAreaFactory(name="AFG"))
    assert site._registry[Feedback].frontend_url(feedback) is None


@pytest.mark.django_db
def test_frontend_url_follow_up_instruction(program):
    program = program()
    instruction = FollowUpInstructionFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[FollowUpInstruction].frontend_url(instruction)
        == f"/afg/programs/TEST/payment-module/follow-up-instructions/{instruction.id}"
    )


@pytest.mark.django_db
def test_frontend_url_pdu_online_edit(program):
    program = program()
    edit = PDUOnlineEditFactory(program=program, business_area=program.business_area)
    assert (
        site._registry[PDUOnlineEdit].frontend_url(edit)
        == f"/afg/programs/TEST/population/individuals/online-templates/{edit.id}"
    )


@pytest.mark.django_db
def test_frontend_url_payment_verification(program, cycle):
    plan = PaymentPlanFactory(program_cycle=cycle(program()), status=PaymentPlan.Status.FINISHED)
    verification_plan = PaymentVerificationPlanFactory(payment_plan=plan)
    verification = PaymentVerificationFactory(payment_verification_plan=verification_plan)
    assert (
        site._registry[PaymentVerification].frontend_url(verification)
        == f"/afg/programs/TEST/payment-verification/payment-plan/{plan.id}/verification/payment/{verification.id}"
    )
