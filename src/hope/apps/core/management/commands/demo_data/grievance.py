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
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.models import Area, BusinessArea, Individual, Program, RegistrationDataImport


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
    doc_type = DocumentTypeFactory(key=attrs["doc_key"], label=attrs["doc_label"])
    DocumentFactory(individual=individual, program=ctx.program, type=doc_type, document_number=attrs["doc_number"])
    individual.photo.save(f"{attrs['doc_key']}.jpg", _fake_photo(attrs["photo_color"]), save=True)
    return individual


def _create_dedup_ticket(
    ctx: DemoContext,
    unicef_id: str,
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

    grievance = GrievanceTicketFactory(
        unicef_id=unicef_id,
        status=1,
        category=8,
        issue_type=23,
        description="Test description",
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
        unicef_id="GRV-0000002",
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
        unicef_id="GRV-0000003",
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
