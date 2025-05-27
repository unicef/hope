import pytest
from django.core.exceptions import ValidationError

from hct_mis_api.apps.accountability.fixtures import FeedbackFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.accountability.services.feedback_crud_services import \
    FeedbackCrudServices
from hct_mis_api.apps.accountability.services.verifiers import \
    MessageArgumentVerifier
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestMessageArgumentVerifier:
    def test_verify_validation_errors(self) -> None:
        service = MessageArgumentVerifier({})
        with pytest.raises(ValidationError) as e:
            service.verify()
        assert "Must provide any one of households, payment_plan or registration_data_import" in str(e.value)

        service = MessageArgumentVerifier({"households": "1", "payment_plan": "2"})
        with pytest.raises(ValidationError) as e:
            service.verify()
        assert "Must provide only one of households, payment_plan or registration_data_import" in str(e.value)

        service = MessageArgumentVerifier({"households": "1", "sampling_type": Message.SamplingChoices.FULL_LIST})
        with pytest.raises(ValidationError) as e:
            service.verify()
        assert "Must provide full_list_arguments for FULL_LIST" in str(e.value)

        service = MessageArgumentVerifier(
            {
                "households": "1",
                "sampling_type": Message.SamplingChoices.RANDOM,
                "full_list_arguments": "abc",
                "random_sampling_arguments": "a",
            }
        )
        with pytest.raises(ValidationError) as e:
            service.verify()
        assert "Must not provide full_list_arguments for RANDOM" in str(e.value)


class TestFeedbackCrudServices:
    def test_feedback_update_program(self) -> None:
        afghanistan = create_afghanistan()
        program_active = ProgramFactory(name="Test Active Program", business_area=afghanistan, status=Program.ACTIVE)
        feedback = FeedbackFactory(
            program=program_active,
        )
        assert feedback.program == program_active
        program_new = ProgramFactory(name="New Program", business_area=afghanistan, status=Program.ACTIVE)
        f = FeedbackCrudServices.update(feedback, {"program": str(program_new.pk)})
        assert f.program == program_new
