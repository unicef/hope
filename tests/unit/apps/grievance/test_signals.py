from typing import Any
from unittest.mock import patch
from uuid import uuid4

from django.core.cache import cache
import pytest

from extras.test_utils.factories import BusinessAreaFactory, GrievanceTicketFactory, ProgramFactory
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.signals import (
    increment_grievance_ticket_version_cache,
    increment_grievance_ticket_version_cache_for_ticket_ids,
    increment_grievance_ticket_version_cache_on_program_change,
    increment_grievance_ticket_version_cache_on_save,
)
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug=f"business-area-{uuid4().hex}", code=f"BA-{uuid4().hex[:6]}")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_2(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def ticket(business_area: BusinessArea) -> GrievanceTicket:
    return GrievanceTicketFactory(business_area=business_area)


def test_increment_grievance_ticket_version_cache() -> None:
    business_area_slug = f"business-area-{uuid4().hex}"
    program_slug_1 = f"program-{uuid4().hex}"
    program_slug_2 = f"program-{uuid4().hex}"

    increment_grievance_ticket_version_cache(business_area_slug, {program_slug_1, program_slug_2})

    assert cache.get(f"{business_area_slug}:1:{program_slug_1}:grievance_ticket_list") == 1
    assert cache.get(f"{business_area_slug}:1:{program_slug_2}:grievance_ticket_list") == 1

    increment_grievance_ticket_version_cache(business_area_slug, {program_slug_1})

    assert cache.get(f"{business_area_slug}:1:{program_slug_1}:grievance_ticket_list") == 2
    assert cache.get(f"{business_area_slug}:1:{program_slug_2}:grievance_ticket_list") == 1


def test_increment_grievance_ticket_version_cache_for_ticket_ids(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    ticket.programs.add(program, program_2)

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_for_ticket_ids(ticket.business_area.slug, [str(ticket.id)])

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


def test_increment_grievance_ticket_version_cache_for_ticket_ids_without_programs(
    ticket: GrievanceTicket,
) -> None:
    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_for_ticket_ids(ticket.business_area.slug, [str(ticket.id)])

    mocked_increment.assert_not_called()


def test_increment_grievance_ticket_version_cache_on_save(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    ticket.programs.add(program, program_2)

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_save(sender=GrievanceTicket, instance=ticket)

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


def test_increment_grievance_ticket_version_cache_on_delete(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    ticket.programs.add(program, program_2)

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_save(sender=GrievanceTicket, instance=ticket, signal="pre_delete")

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


def test_increment_grievance_ticket_version_cache_on_save_without_programs(
    ticket: GrievanceTicket,
) -> None:
    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_save(sender=GrievanceTicket, instance=ticket)

    mocked_increment.assert_not_called()


def test_increment_grievance_ticket_version_cache_on_program_change_post_add(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_program_change(
            sender=GrievanceTicket.programs.through,
            instance=ticket,
            action="post_add",
            reverse=False,
            model=Program,
            pk_set={program.pk, program_2.pk},
        )

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


def test_increment_grievance_ticket_version_cache_on_program_change_post_remove(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_program_change(
            sender=GrievanceTicket.programs.through,
            instance=ticket,
            action="post_remove",
            reverse=False,
            model=Program,
            pk_set={program.pk, program_2.pk},
        )

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


def test_increment_grievance_ticket_version_cache_on_program_change_pre_clear(
    ticket: GrievanceTicket,
    program: Program,
    program_2: Program,
) -> None:
    ticket.programs.add(program, program_2)

    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        increment_grievance_ticket_version_cache_on_program_change(
            sender=GrievanceTicket.programs.through,
            instance=ticket,
            action="pre_clear",
            reverse=False,
        )

    mocked_increment.assert_called_once_with(ticket.business_area.slug, {program.slug, program_2.slug})


@pytest.mark.parametrize(
    ("action", "reverse", "pk_set"),
    [
        ("post_add", True, {1}),
        ("post_remove", False, set()),
        ("post_clear", False, None),
    ],
)
def test_increment_grievance_ticket_version_cache_on_program_change_noop(
    ticket: GrievanceTicket,
    action: str,
    reverse: bool,
    pk_set: set[int] | None,
) -> None:
    with patch("hope.apps.grievance.signals.increment_grievance_ticket_version_cache") as mocked_increment:
        kwargs: dict[str, Any] = {}
        if pk_set is not None:
            kwargs["model"] = Program
            kwargs["pk_set"] = pk_set
        increment_grievance_ticket_version_cache_on_program_change(
            sender=GrievanceTicket.programs.through,
            instance=ticket,
            action=action,
            reverse=reverse,
            **kwargs,
        )

    mocked_increment.assert_not_called()
