from datetime import date
from io import BytesIO
from typing import NamedTuple

from django.core.files.base import ContentFile
from PIL import Image

from extras.test_utils.factories import (
    DocumentFactory,
    DocumentTypeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import Area, BusinessArea, Household, Individual, Program, RegistrationDataImport


class DemoContext(NamedTuple):
    program: Program
    ba: BusinessArea
    rdi: RegistrationDataImport | None
    admin2: Area | None


def _fake_photo(color: str) -> ContentFile:
    buffer = BytesIO()
    Image.new("RGB", (200, 200), color).save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue(), name="photo.jpg")


def _make_individual(ctx: DemoContext, attrs: dict) -> Individual:
    """Create a household + individual with fully controlled fields.

    The Needs-Adjudication comparison panel highlights a row when the two
    individuals' values differ, so callers set contrasting ``attrs`` to exercise it.
    ``attrs`` keys: full_name, sex, birth_date, village, doc_key, doc_label,
    doc_number, photo_color.
    """
    household = HouseholdFactory(
        program=ctx.program,
        business_area=ctx.ba,
        registration_data_import=ctx.rdi,
        village=attrs["village"],
    )
    individual = IndividualFactory(
        household=household,
        program=ctx.program,
        business_area=ctx.ba,
        registration_data_import=ctx.rdi,
        full_name=attrs["full_name"],
        sex=attrs["sex"],
        birth_date=attrs["birth_date"],
    )
    household.head_of_household = individual
    household.save()
    _attach_identity(ctx, individual, attrs)
    return individual


def _attach_identity(ctx: DemoContext, individual: Individual, attrs: dict) -> None:
    """Give the individual a document and a photo so the comparison panel has content."""
    doc_type = DocumentTypeFactory(key=attrs["doc_key"], label=attrs["doc_label"])
    DocumentFactory(individual=individual, program=ctx.program, type=doc_type, document_number=attrs["doc_number"])
    individual.photo.save(f"{attrs['doc_key']}.jpg", _fake_photo(attrs["photo_color"]), save=True)


def _create_dedup_ticket(
    ctx: DemoContext,
    golden_attrs: dict,
    duplicate_attrs: dict,
    score: float = 8.5,
) -> None:
    """Build a Needs-Adjudication ticket comparing two distinct individuals.

    ``golden_attrs``/``duplicate_attrs`` are passed straight to
    :func:`_make_individual`; set them to differing values so every comparison row
    on the NA Tickets Management panel is flagged as different (highlighted).
    """
    golden = _make_individual(ctx, golden_attrs)
    duplicate = _make_individual(ctx, duplicate_attrs)
    _create_na_ticket(ctx, golden, duplicate, score)


def _create_na_ticket(
    ctx: DemoContext,
    golden: Individual,
    duplicate: Individual,
    score: float = 8.5,
    description: str = "Test description",
) -> None:
    """Wire two existing individuals into a Needs-Adjudication ticket.

    ``unicef_id`` is deliberately not settable: a DB trigger assigns it on insert and
    ``UnicefIdentifiedModel.save()`` refreshes the field, so any value passed in is discarded.
    """
    grievance = GrievanceTicketFactory(
        status=1,
        category=8,
        issue_type=23,
        description=description,
        admin2=ctx.admin2,
        consent=True,
        business_area=ctx.ba,
        registration_data_import=ctx.rdi,
        extras={},
        ignored=False,
        household_unicef_id=golden.household.unicef_id,
    )
    grievance.programs.set([ctx.program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        # person2 in the panel resolves to ``possible_duplicate`` first, so point it
        # at the genuinely-different individual (not the golden one) to render a diff.
        possible_duplicate=duplicate,
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [
                {
                    "dob": duplicate.birth_date.isoformat(),
                    "score": score,
                    "hit_id": str(duplicate.pk),
                    "location": duplicate.household.village,
                    "full_name": duplicate.full_name,
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": golden.birth_date.isoformat(),
                    "score": score,
                    "hit_id": str(golden.pk),
                    "location": golden.household.village,
                    "full_name": golden.full_name,
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
        },
        score_min=score,
        score_max=score,
    )
    ticket_details.possible_duplicates.set([duplicate])


def _make_household_with_members(
    ctx: DemoContext,
    village: str,
    members: list[dict],
    head_index: int = 0,
) -> tuple[Household, list[Individual]]:
    """Build a household whose roster is exactly ``members``, with no collector roles.

    ``create_role=False`` keeps the factory from silently granting PRIMARY to the head —
    every scenario below assigns roles explicitly. ``HouseholdFactory`` always generates
    one member of its own, so that individual is reused as ``members[0]`` rather than
    left in place, otherwise ``active_individuals_count`` would be off by one and the
    sole-member scenario could not be built at all.
    """
    household = HouseholdFactory(
        program=ctx.program,
        business_area=ctx.ba,
        registration_data_import=ctx.rdi,
        village=village,
        create_role=False,
    )
    individuals = [household.head_of_household]
    for field, value in members[0].items():
        setattr(individuals[0], field, value)
    individuals[0].save()
    individuals.extend(
        IndividualFactory(
            household=household,
            program=ctx.program,
            business_area=ctx.ba,
            registration_data_import=ctx.rdi,
            **attrs,
        )
        for attrs in members[1:]
    )
    household.head_of_household = individuals[head_index]
    household.save()
    return household, individuals


_SCENARIO_TAG = "[NA role reassignment]"


def _person(full_name: str, sex: str, birth_date: date) -> dict:
    return {"full_name": full_name, "sex": sex, "birth_date": birth_date}


# Filler members exist only to keep a household above the sole-member threshold and to
# give the reassign modal someone to hand the role to.
_FILLERS = [
    _person("Nadia Rahimi", "FEMALE", date(1991, 4, 2)),
    _person("Bilal Sarwar", "MALE", date(1986, 9, 17)),
]


def _make_golden(ctx: DemoContext, attrs: dict) -> Individual:
    """Person 1 of the comparison: always role-free, so only person 2 drives reassignment.

    ``head_index=1`` hands headship to the filler — otherwise person 1 would pick up the
    synthetic HEAD role and demand a reassignment of its own when withdrawn.
    """
    _, individuals = _make_household_with_members(
        ctx,
        village="Kandahar",
        members=[_person(attrs["full_name"], attrs["sex"], attrs["birth_date"]), _FILLERS[0]],
        head_index=1,
    )
    _attach_identity(ctx, individuals[0], attrs)
    return individuals[0]


def generate_role_reassignment_scenarios(ctx: DemoContext) -> None:
    """Needs-Adjudication tickets covering every branch of ``getRequiredReassignments``.

    In each ticket person 1 holds no roles and person 2 is the role holder, so the tester
    always clicks *Withdraw person 2* and only the reassignment section differs. Expected
    rows are noted per scenario; HEAD and PRIMARY require a handover, ALTERNATE does not,
    and a household with a single active member is skipped because withdrawing its last
    member withdraws the household outright.

    ``GrievanceTicket.save()`` regenerates ``unicef_id`` from a per-business-area sequence,
    so the ids passed below are labels only — the description carries the marker that makes
    this function re-runnable and tells the tester what each ticket is for.
    """
    if GrievanceTicket.objects.filter(description__startswith=_SCENARIO_TAG).exists():
        return

    def duplicate_attrs(name: str, key: str, number: str, color: str) -> dict:
        return {
            "full_name": name,
            "doc_key": key,
            "doc_label": "Passport",
            "doc_number": number,
            "photo_color": color,
        }

    # 1 row: HEAD. The replacement must come from the same household.
    household, members = _make_household_with_members(
        ctx,
        village="Herat",
        members=[_person("Farid Ahmadzai", "MALE", date(1980, 3, 4)), *_FILLERS],
    )
    _attach_identity(ctx, members[0], duplicate_attrs("Farid Ahmadzai", "na_head_doc", "PSP-5001", "indianred"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Zahra Karimi",
                "sex": "FEMALE",
                "birth_date": date(1984, 7, 21),
                "doc_key": "na_head_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5001",
                "photo_color": "steelblue",
            },
        ),
        members[0],
        description=f"{_SCENARIO_TAG} HEAD only - expect 1 row; replacement must be in the same household",
    )

    # 1 row: PRIMARY. The duplicate is a plain member, so no HEAD row is expected.
    household, members = _make_household_with_members(
        ctx,
        village="Mazar",
        members=[*_FILLERS, _person("Jamil Noorzai", "MALE", date(1977, 12, 9))],
        head_index=0,
    )
    IndividualRoleInHouseholdFactory(household=household, individual=members[2], role=ROLE_PRIMARY)
    _attach_identity(ctx, members[2], duplicate_attrs("Jamil Noorzai", "na_prim_doc", "PSP-5002", "goldenrod"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Laila Sadat",
                "sex": "FEMALE",
                "birth_date": date(1990, 1, 15),
                "doc_key": "na_prim_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5002",
                "photo_color": "darkseagreen",
            },
        ),
        members[2],
        description=f"{_SCENARIO_TAG} PRIMARY only - expect 1 row; replacement may be outside the household",
    )

    # 2 rows: HEAD and PRIMARY, both on the same individual and the same household.
    household, members = _make_household_with_members(
        ctx,
        village="Kabul",
        members=[_person("Rashid Wardak", "MALE", date(1975, 6, 30)), *_FILLERS],
    )
    IndividualRoleInHouseholdFactory(household=household, individual=members[0], role=ROLE_PRIMARY)
    _attach_identity(ctx, members[0], duplicate_attrs("Rashid Wardak", "na_both_doc", "PSP-5003", "mediumpurple"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Nasrin Popal",
                "sex": "FEMALE",
                "birth_date": date(1983, 10, 5),
                "doc_key": "na_both_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5003",
                "photo_color": "steelblue",
            },
        ),
        members[0],
        description=f"{_SCENARIO_TAG} HEAD + PRIMARY on one person - expect 2 rows",
    )

    # 0 rows: ALTERNATE is never blocking. Head and PRIMARY sit on other members.
    household, members = _make_household_with_members(
        ctx,
        village="Jalalabad",
        members=[*_FILLERS, _person("Yusuf Barakzai", "MALE", date(1989, 2, 11))],
        head_index=0,
    )
    IndividualRoleInHouseholdFactory(household=household, individual=members[1], role=ROLE_PRIMARY)
    IndividualRoleInHouseholdFactory(household=household, individual=members[2], role=ROLE_ALTERNATE)
    _attach_identity(ctx, members[2], duplicate_attrs("Yusuf Barakzai", "na_alt_doc", "PSP-5004", "indianred"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Marwa Hakimi",
                "sex": "FEMALE",
                "birth_date": date(1992, 8, 23),
                "doc_key": "na_alt_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5004",
                "photo_color": "darkseagreen",
            },
        ),
        members[2],
        description=f"{_SCENARIO_TAG} ALTERNATE only - expect 0 rows; withdrawal allowed straight away",
    )

    # 0 rows: head of a sole-member household, skipped by the activeIndividualsCount rule.
    household, members = _make_household_with_members(
        ctx,
        village="Ghazni",
        members=[_person("Sami Faizi", "MALE", date(1981, 5, 19))],
    )
    _attach_identity(ctx, members[0], duplicate_attrs("Sami Faizi", "na_solo_doc", "PSP-5005", "goldenrod"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Hoda Amiri",
                "sex": "FEMALE",
                "birth_date": date(1987, 11, 28),
                "doc_key": "na_solo_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5005",
                "photo_color": "steelblue",
            },
        ),
        members[0],
        description=f"{_SCENARIO_TAG} HEAD of a sole-member household - expect 0 rows (active-members rule)",
    )

    # 2 rows: PRIMARY in two households. A primary collector need not live in the
    # household they collect for, so the second role is granted from outside.
    # Both rows key to the role name in buildExecutePayload, so this is also the
    # scenario that surfaces the known role_reassign_data key collision.
    household, members = _make_household_with_members(
        ctx,
        village="Kunduz",
        members=[*_FILLERS, _person("Idris Safi", "MALE", date(1978, 4, 14))],
        head_index=0,
    )
    IndividualRoleInHouseholdFactory(household=household, individual=members[2], role=ROLE_PRIMARY)
    other_household, _ = _make_household_with_members(
        ctx,
        village="Bamyan",
        members=[
            _person("Shirin Ayubi", "FEMALE", date(1993, 3, 8)),
            _person("Tariq Mohmand", "MALE", date(1985, 7, 2)),
        ],
    )
    IndividualRoleInHouseholdFactory(household=other_household, individual=members[2], role=ROLE_PRIMARY)
    _attach_identity(ctx, members[2], duplicate_attrs("Idris Safi", "na_2hh_doc", "PSP-5006", "mediumpurple"))
    _create_na_ticket(
        ctx,
        _make_golden(
            ctx,
            {
                "full_name": "Parwin Nazari",
                "sex": "FEMALE",
                "birth_date": date(1994, 9, 12),
                "doc_key": "na_2hh_golden_doc",
                "doc_label": "National ID",
                "doc_number": "NID-5006",
                "photo_color": "darkseagreen",
            },
        ),
        members[2],
        description=f"{_SCENARIO_TAG} PRIMARY in two households - expect 2 rows; role-name keys drop one",
    )


def generate_fake_grievances() -> None:
    program = Program.objects.get(name="Test Program")
    admin2 = Area.objects.filter(area_type__area_level=2).first()
    ind_qs = Individual.objects.filter(household__program=program)
    golden_records_individual = ind_qs[0]
    jan1 = ind_qs[1]
    jan2 = ind_qs[2]
    golden_records_individual.photo.save("golden.jpg", _fake_photo("steelblue"), save=True)
    jan1.photo.save("jan1.jpg", _fake_photo("indianred"), save=True)
    jan2.photo.save("jan2.jpg", _fake_photo("darkseagreen"), save=True)
    ba = program.business_area
    rdi = RegistrationDataImport.objects.filter(business_area=ba).first()
    grievance = GrievanceTicketFactory(
        unicef_id="GRV-0000001",
        status=1,
        category=8,
        issue_type=23,
        description="Test description",
        admin2=admin2,
        consent=True,
        business_area=ba,
        registration_data_import=rdi,
        extras={},
        ignored=False,
        household_unicef_id="HH-20-0000.0014",
    )
    grievance.programs.set([program])

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden_records_individual,
        is_multiple_duplicates_version=True,
        possible_duplicate=golden_records_individual,
        selected_individual=None,
        role_reassign_data={},
        extra_data={
            "golden_records": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": False,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan1.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak1",
                    "proximity_to_score": 3.0,
                    "duplicate": True,
                    "distinct": False,
                },
                {
                    "dob": "1923-01-01",
                    "score": 9.0,
                    "hit_id": str(jan2.pk),
                    "location": "Abband",
                    "full_name": "Jan Romaniak2",
                    "proximity_to_score": 3.0,
                    "duplicate": False,
                    "distinct": True,
                },
            ],
        },
        score_min=9.0,
        score_max=9.0,
    )
    ticket_details.possible_duplicates.set([jan1, jan2])
    ticket_details.selected_individuals.set([jan2])
    ticket_details.selected_distinct.set([golden_records_individual])

    # Additional tickets whose two individuals differ across every comparison row,
    # so the NA Tickets Management panel actually highlights the differences.
    ctx = DemoContext(program=program, ba=ba, rdi=rdi, admin2=admin2)
    _create_dedup_ticket(
        ctx,
        golden_attrs={
            "full_name": "Amina Yusuf",
            "sex": "FEMALE",
            "birth_date": date(1988, 5, 12),
            "village": "Kandahar",
            "doc_key": "grv2_golden_doc",
            "doc_label": "National ID",
            "doc_number": "NID-1001",
            "photo_color": "steelblue",
        },
        duplicate_attrs={
            "full_name": "Karim Noor",
            "sex": "MALE",
            "birth_date": date(1979, 11, 3),
            "village": "Herat",
            "doc_key": "grv2_dup_doc",
            "doc_label": "Passport",
            "doc_number": "PSP-2002",
            "photo_color": "indianred",
        },
    )
    _create_dedup_ticket(
        ctx,
        golden_attrs={
            "full_name": "Sara Ahmadi",
            "sex": "FEMALE",
            "birth_date": date(1995, 2, 20),
            "village": "Mazar",
            "doc_key": "grv3_golden_doc",
            "doc_label": "National ID",
            "doc_number": "NID-3003",
            "photo_color": "darkseagreen",
        },
        duplicate_attrs={
            "full_name": "Omar Hassan",
            "sex": "MALE",
            "birth_date": date(1982, 8, 7),
            "village": "Kabul",
            "doc_key": "grv3_dup_doc",
            "doc_label": "Passport",
            "doc_number": "PSP-4004",
            "photo_color": "goldenrod",
        },
    )
    generate_role_reassignment_scenarios(ctx)
