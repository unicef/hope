"""Tests for FeedbackCrudServices."""

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FeedbackFactory,
    ProgramFactory,
)
from hope.apps.accountability.services.feedback_crud_services import FeedbackCrudServices
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture
def program_active(business_area):
    return ProgramFactory(name="Test Active Program", business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def program_new(business_area):
    return ProgramFactory(name="New Program", business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def feedback(program_active, business_area):
    return FeedbackFactory(
        program=program_active,
        business_area=business_area,
    )


def test_feedback_update_changes_program_to_new_program(feedback, program_active, program_new):
    assert feedback.program == program_active

    updated_feedback = FeedbackCrudServices.update(feedback, {"program": str(program_new.pk)})

    assert updated_feedback.program == program_new
