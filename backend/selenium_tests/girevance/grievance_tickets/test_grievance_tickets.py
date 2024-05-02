from typing import Generator

from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.grievance.feedback import Feedback
from pytest_django import DjangoDbBlocker

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_feedbacks(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_households(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    return


@pytest.fixture
def create_programs(django_db_setup: Generator[None, None, None], django_db_blocker: DjangoDbBlocker) -> None:
    with django_db_blocker.unblock():
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestSmokeGrievanceTickets:
    def test_check_grievance_tickets_page(
        self,
        pageFeedback: Feedback,
    ) -> None:
        """
        Go to Grievance page
        Go to Feedback page
        Check if all elements on page exist
        """
        # Go to Grievance Tickets
        pageFeedback.getNavGrievance().click()
