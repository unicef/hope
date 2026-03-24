"""Tests for accountability verifiers."""

import pytest
from rest_framework.exceptions import ValidationError

from hope.apps.accountability.services.verifiers import MessageArgumentVerifier
from hope.models import Message


def test_message_argument_verifier_raises_when_no_target_provided():
    service = MessageArgumentVerifier({})
    with pytest.raises(ValidationError) as exc_info:
        service.verify()
    assert "Must provide any one of households, payment_plan or registration_data_import" in str(exc_info.value)


def test_message_argument_verifier_raises_when_multiple_targets_provided():
    service = MessageArgumentVerifier({"households": "1", "payment_plan": "2"})
    with pytest.raises(ValidationError) as exc_info:
        service.verify()
    assert "Must provide only one of households, payment_plan or registration_data_import" in str(exc_info.value)


def test_message_argument_verifier_raises_when_full_list_arguments_missing_for_full_list_sampling():
    service = MessageArgumentVerifier(
        {
            "households": "1",
            "sampling_type": Message.SamplingChoices.FULL_LIST,
        }
    )
    with pytest.raises(ValidationError) as exc_info:
        service.verify()
    assert "Must provide full_list_arguments for FULL_LIST" in str(exc_info.value)


def test_message_argument_verifier_raises_when_full_list_arguments_provided_for_random_sampling():
    service = MessageArgumentVerifier(
        {
            "households": "1",
            "sampling_type": Message.SamplingChoices.RANDOM,
            "full_list_arguments": "abc",
            "random_sampling_arguments": "a",
        }
    )
    with pytest.raises(ValidationError) as exc_info:
        service.verify()
    assert "Must not provide full_list_arguments for RANDOM" in str(exc_info.value)
