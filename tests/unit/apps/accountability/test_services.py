from django.core.exceptions import ValidationError

import pytest

from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.accountability.services.verifiers import MessageArgumentVerifier

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
            {"households": "1", "sampling_type": Message.SamplingChoices.RANDOM, "full_list_arguments": "abc"}
        )
        with pytest.raises(ValidationError) as e:
            service.verify()
        assert "Must provide random_sampling_arguments for RANDOM" in str(e.value)
