"""Add individuals to existing households from an xlsx list, one Add Individual ticket per row.

Imitates UI path - creating Add Individual Grievance Ticket, approving it
and closing 1 individual at a time.

Columns are matched against ``core_fields_attributes`` by ``xlsx_field``, so the file may carry any
writable core individual column; anything ending in ``_i_f`` is coerced by its flexible attribute
type and stored as a flex field. A row is skipped when its household already holds at least as many
individuals with the same full name and birth date as the rows seen so far in this run, so an
interrupted run can be repeated and rows sharing one name and birth date are still each created once.

Before any row is processed, every programme name, household id and, when the file carries an
``individual_unicef_id`` column, household member is resolved in bulk. A household must be merged and
not removed in the row's programme, and the member must belong to that household. With ``apply=True``
any such problem stops the run before anything is written. A row whose relationship is ``HEAD`` is
still created, but reported as a warning: closing it makes that individual the head of household and
sets every other member's relationship to unknown. The summary counts the individuals in the listed
households before and after the run and checks the difference against the rows created.

No notifications are sent: the ticket is created and closed below the API layer that emits them.

Run from Django shell, validating first:
    from hope.one_time_scripts.bulk_add_individuals import bulk_add_individuals
    bulk_add_individuals("/tmp/newborns.xlsx", "myanmar", "service.account@unicef.org")
    bulk_add_individuals("/tmp/newborns.xlsx", "myanmar", "service.account@unicef.org", apply=True)
"""

from collections import Counter
import datetime
from typing import Any, Iterator

from django.db import transaction
from django.utils import timezone
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import (
    TYPE_BOOL,
    TYPE_DATE,
    TYPE_DECIMAL,
    TYPE_IMAGE,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    TYPE_SELECT_ONE,
    Scope,
)
from hope.apps.core.utils import serialize_flex_attributes
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.add_individual_service import AddIndividualService
from hope.apps.grievance.services.data_change.utils import verify_flex_fields
from hope.apps.grievance.services.ticket_status_changer_service import TicketStatusChangerService
from hope.apps.grievance.utils import clear_cache
from hope.apps.household.const import HEAD
from hope.models import BusinessArea, Household, Individual, Program, User, log_create
from hope.models.utils import MergeStatusModel

PROGRAM_NAME_COLUMN = "programme_name"
HOUSEHOLD_ID_COLUMN = "unicef_id"
# An existing member of the household named on the row, used only to cross-check the household id.
MEMBER_ID_COLUMN = "individual_unicef_id"
FLEX_FIELD_SUFFIX = "_i_f"
# Set by the closing service itself, so a cell value would clash with it.
SERVICE_OWNED_FIELDS = frozenset({"first_registration_date"})
REQUIRED_FIELDS = ("full_name", "sex", "birth_date", "relationship")
DUPLICATE_KEY_FIELDS = ("full_name", "birth_date")
DEFAULTS: dict[str, Any] = {"estimated_birth_date": False}
TEXT_DATE_FORMAT = "%d/%m/%Y"
TRUE_VALUES = frozenset({"true", "yes", "1", "y"})
FALSE_VALUES = frozenset({"false", "no", "0", "n"})
DEFAULT_DESCRIPTION = "Bulk add individuals"
HEAD_WARNING = "relationship HEAD makes this individual the head of household and sets every other member to UNKNOWN"
# Columns spelled differently in the country office file from the platform name they write.
COLUMN_ALIASES = {"relationship to hh": "relationship_i_c"}


def _clean_text(value: Any) -> str:
    return str(value).strip()


def _parse_date(value: Any) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    text = _clean_text(value)
    if not text:
        raise ValueError(f"unreadable date {value!r}")
    return datetime.datetime.strptime(text, TEXT_DATE_FORMAT).date()


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = _clean_text(value).lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    raise ValueError(f"unreadable boolean {value!r}")


def _coerce(value: Any, field_type: str) -> Any:
    if field_type == TYPE_DATE:
        return _parse_date(value)
    if field_type == TYPE_BOOL:
        return _parse_bool(value)
    if field_type == TYPE_INTEGER:
        return int(value)
    if field_type == TYPE_DECIMAL:
        return float(value)
    if field_type == TYPE_SELECT_MANY:
        if isinstance(value, list):
            return value
        return [part.strip() for part in _clean_text(value).split(",") if part.strip()]
    return _clean_text(value)


def _individual_core_attributes() -> dict[str, dict]:
    """Map xlsx column name to the core field attribute it writes, for writable Individual fields.

    Computed attributes such as ``age`` and the document attributes share the scope but are not
    Individual columns; passing one to ``Individual.objects.create`` raises TypeError. Image attributes
    cannot be read from a cell, and ``SERVICE_OWNED_FIELDS`` are filled by the closing service.
    """
    # actually existing columns on Individual model
    concrete = {f.name for f in Individual._meta.get_fields() if getattr(f, "concrete", False)}
    factory = FieldFactory.from_scope(Scope.GLOBAL).associated_with_individual()
    return {
        a["xlsx_field"]: a
        for a in factory
        if a["name"] in concrete and a["name"] not in SERVICE_OWNED_FIELDS and a["type"] != TYPE_IMAGE
    }


def _coerce_core_value(attribute: dict, value: Any) -> Any:
    coerced = _coerce(value, attribute["type"])
    choices = {choice["value"] for choice in attribute.get("choices") or []}
    if attribute["type"] == TYPE_SELECT_ONE and choices and coerced not in choices:
        raise ValueError(f"invalid {coerced!r} for {attribute['xlsx_field']}, expected one of {sorted(choices)}")
    return coerced


def _coerce_flex_value(attribute: dict | None, value: Any) -> Any:
    if attribute is None:
        # unknown name: leave the text for verify_flex_fields to reject
        return _clean_text(value)
    if attribute["type"] == TYPE_DATE:
        return _parse_date(value).isoformat()
    if attribute["type"] == TYPE_DECIMAL:
        # verify_flex_fields expects decimals as text
        return _clean_text(value)
    return _coerce(value, attribute["type"])


def _validate_model_choices(data: dict) -> None:
    """Enforce that selected values correspond to model fields choices"""
    for name, value in data.items():
        if name == "flex_fields" or value in (None, ""):
            continue
        allowed = {choice for choice, _label in getattr(Individual._meta.get_field(name), "choices", None) or []}
        if not allowed:
            continue
        values = value if isinstance(value, list) else [value]
        invalid = [item for item in values if item not in allowed]
        if invalid:
            raise ValueError(f"invalid {invalid[0]!r} for {name}, expected one of {sorted(allowed)}")


def _build_individual_data(row: dict, core_attributes: dict[str, dict], flex_attributes: dict[str, dict]) -> dict:
    data = dict(DEFAULTS)
    for column, value in row.items():
        attribute = core_attributes.get(column)
        if attribute is None or value in (None, ""):
            continue
        data[attribute["name"]] = _coerce_core_value(attribute, value)
    data["flex_fields"] = {
        column: _coerce_flex_value(flex_attributes.get(column), value)
        for column, value in row.items()
        if column and column.endswith(FLEX_FIELD_SUFFIX) and value not in (None, "")
    }
    missing = [name for name in REQUIRED_FIELDS if not data.get(name)]
    if missing:
        raise ValueError(f"missing required {', '.join(missing)}")
    absent = [name for name in DUPLICATE_KEY_FIELDS if name not in data]
    if absent:
        raise ValueError(f"duplicate key field(s) not in the row: {', '.join(absent)}")
    _validate_model_choices(data)
    verify_flex_fields(dict(data["flex_fields"]), "individuals")
    return data


def _load_programs(rows: list[tuple[int, dict]], business_area: BusinessArea) -> dict[str, Program]:
    names = {_clean_text(row.get(PROGRAM_NAME_COLUMN) or "") for _row_number, row in rows}
    return {program.name: program for program in Program.objects.filter(business_area=business_area, name__in=names)}


def _load_households(
    rows: list[tuple[int, dict]], programs: dict[str, Program]
) -> tuple[dict[tuple[str, Any], Household], dict[tuple[str, Any], str]]:
    """Usable households keyed by (unicef_id, program pk), and why the other matching ones are not."""
    unicef_ids = {_clean_text(row.get(HOUSEHOLD_ID_COLUMN) or "") for _row_number, row in rows}
    program_ids = [program.pk for program in programs.values()]
    households = {
        (household.unicef_id, household.program_id): household
        for household in Household.objects.filter(program_id__in=program_ids, unicef_id__in=unicef_ids)
    }
    unusable = {
        (unicef_id, program_id): "removed" if is_removed else "not merged"
        for unicef_id, program_id, is_removed in Household.all_objects.filter(
            program_id__in=program_ids, unicef_id__in=unicef_ids
        )
        .exclude(is_removed=False, rdi_merge_status=MergeStatusModel.MERGED)
        .values_list("unicef_id", "program_id", "is_removed")
    }
    return households, unusable


def _load_members(rows: list[tuple[int, dict]], programs: dict[str, Program]) -> dict[tuple[str, Any], str | None]:
    """Household unicef_id of every referenced member, keyed by (member unicef_id, program pk)."""
    member_ids = {_clean_text(row.get(MEMBER_ID_COLUMN) or "") for _row_number, row in rows} - {""}
    if not member_ids:
        return {}
    program_ids = [program.pk for program in programs.values()]
    return {
        (unicef_id, program_id): household_unicef_id
        for unicef_id, program_id, household_unicef_id in Individual.objects.filter(
            program_id__in=program_ids, unicef_id__in=member_ids
        ).values_list("unicef_id", "program_id", "household__unicef_id")
    }


def _count_individuals(households: dict[tuple[str, Any], Household]) -> int:
    return Individual.objects.filter(household_id__in=[household.pk for household in households.values()]).count()


def _resolve_program(row: dict, programs: dict[str, Program]) -> Program:
    name = _clean_text(row.get(PROGRAM_NAME_COLUMN) or "")
    if not name:
        raise ValueError(f"missing {PROGRAM_NAME_COLUMN}")
    if name not in programs:
        raise ValueError(f"programme {name!r} not found")
    return programs[name]


def _resolve_household(
    row: dict,
    program: Program,
    households: dict[tuple[str, Any], Household],
    unusable: dict[tuple[str, Any], str],
) -> Household:
    unicef_id = _clean_text(row.get(HOUSEHOLD_ID_COLUMN) or "")
    if not unicef_id:
        raise ValueError(f"missing {HOUSEHOLD_ID_COLUMN}")
    household = households.get((unicef_id, program.pk))
    if household is None:
        state = unusable.get((unicef_id, program.pk), "not found")
        raise ValueError(f"household {unicef_id} {state} in programme {program.name}")
    return household


def _check_member(
    row: dict,
    program: Program,
    household: Household,
    members: dict[tuple[str, Any], str | None],
) -> None:
    member_id = _clean_text(row.get(MEMBER_ID_COLUMN) or "")
    if not member_id:
        return
    if (member_id, program.pk) not in members:
        raise ValueError(f"individual {member_id} not found in programme {program.name}")
    member_household = members[(member_id, program.pk)]
    if member_household != household.unicef_id:
        raise ValueError(f"individual {member_id} belongs to {member_household}, not {household.unicef_id}")


def _reference_problems(
    rows: list[tuple[int, dict]],
    programs: dict[str, Program],
    households: dict[tuple[str, Any], Household],
    unusable: dict[tuple[str, Any], str],
    members: dict[tuple[str, Any], str | None],
) -> list[tuple[int, str]]:
    problems = []
    for row_number, row in rows:
        try:
            program = _resolve_program(row, programs)
            household = _resolve_household(row, program, households, unusable)
            _check_member(row, program, household, members)
        except ValueError as error:
            problems.append((row_number, str(error)))
    return problems


def _already_present(household: Household, individual_data: dict, seen: Counter) -> bool:
    """True when the household holds more individuals matching DUPLICATE_KEY_FIELDS than this run
    has already accounted for.

    Counting rather than testing existence lets several rows share one name and birth date (eg twins)
    while a repeated run still skips what an earlier run wrote.
    """
    fingerprint = (household.pk, *(individual_data[name] for name in DUPLICATE_KEY_FIELDS))
    lookup = {name: individual_data[name] for name in DUPLICATE_KEY_FIELDS}
    existing = Individual.objects.filter(household=household, **lookup).count()
    present = existing > seen[fingerprint]
    seen[fingerprint] += 1
    return present


def _add_individual(
    household: Household,
    individual_data: dict,
    business_area: BusinessArea,
    user: User,
    description: str,
) -> GrievanceTicket:
    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        business_area=business_area,
        admin2=household.admin2,
        area=household.village or "",
        description=description,
        created_by=user,
        assigned_to=user,
        assigned_by=user,
        assigned_at=timezone.now(),
        user_modified=timezone.now(),
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )
    ticket.programs.add(household.program)
    extras = {
        "issue_type": {
            "add_individual_issue_type_extras": {
                "household": household,
                "individual_data": individual_data,
            }
        }
    }
    AddIndividualService(ticket, extras).save()
    details = ticket.add_individual_ticket_details
    details.approve_status = True
    details.save(update_fields=["approve_status"])
    TicketStatusChangerService(ticket, user).change_status(GrievanceTicket.STATUS_CLOSED)
    log_create(
        GrievanceTicket.ACTIVITY_LOG_MAPPING,
        "business_area",
        user,
        ticket.programs.all(),
        old_object=None,
        new_object=ticket,
    )
    return ticket


def _open_sheet(path: str, sheet_name: str | None) -> Worksheet:
    workbook = openpyxl.load_workbook(path, data_only=True)
    if sheet_name:
        return workbook[sheet_name]
    return workbook.worksheets[0]


def _sheet_columns(worksheet: Worksheet) -> tuple[list, dict]:
    """Header with the file's own names mapped onto expected column names."""
    raw_headers = [_clean_text(cell.value) if cell.value is not None else None for cell in worksheet[1]]
    aligned_headers = [COLUMN_ALIASES.get(name, name) if name is not None else None for name in raw_headers]
    return aligned_headers, {k: v for k, v in COLUMN_ALIASES.items() if k in raw_headers}


def _ignored_columns(header: list, core_attributes: dict[str, dict]) -> list[str]:
    known = {PROGRAM_NAME_COLUMN, HOUSEHOLD_ID_COLUMN, MEMBER_ID_COLUMN, *core_attributes}
    return [column for column in header if column and column not in known and not column.endswith(FLEX_FIELD_SUFFIX)]


def _read_rows(worksheet: Worksheet, header: list) -> Iterator[tuple[int, dict]]:
    for row_number, values in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
        if all(v is None or (isinstance(v, str) and not v.strip()) for v in values):
            continue
        yield row_number, dict(zip(header, values, strict=False))


def bulk_add_individuals(
    xlsx_path: str,
    business_area_slug: str,
    user_email: str,
    sheet_name: str | None = None,
    description: str = DEFAULT_DESCRIPTION,
    apply: bool = False,
) -> dict[str, list]:
    business_area = BusinessArea.objects.get(slug=business_area_slug)
    user = User.objects.get(email=user_email)
    core_attributes = _individual_core_attributes()
    flex_attributes = serialize_flex_attributes()["individuals"]
    worksheet = _open_sheet(xlsx_path, sheet_name)
    header, applied_aliases = _sheet_columns(worksheet)
    ignored_columns = _ignored_columns(header, core_attributes)

    rows = list(_read_rows(worksheet, header))
    programs = _load_programs(rows, business_area)
    households, unusable = _load_households(rows, programs)
    members = _load_members(rows, programs)
    problems = _reference_problems(rows, programs, households, unusable, members)
    before = _count_individuals(households)
    seen: Counter = Counter()
    created: list[int] = []
    skipped: list[tuple[int, str]] = []
    failed: list[tuple[int, str]] = []
    warnings: list[tuple[int, str]] = []
    last_details = None

    print(f"file           : {xlsx_path}")
    print(f"sheet          : {worksheet.title}")
    print(f"business area  : {business_area.name}")
    print(f"acting as      : {user.email}")
    print(f"postpone dedup : {business_area.postpone_deduplication}")
    print(f"mode           : {'APPLY' if apply else 'validate only'}")
    print(f"references     : {len(problems)} problem(s)")
    print(f"individuals    : {before} in the listed households")
    if applied_aliases:
        print(f"column aliases : {applied_aliases}")
    if ignored_columns:
        print(f"ignored columns: {ignored_columns}")
    if not business_area.postpone_deduplication:
        print("WARNING: postpone_deduplication is False - close() queues one dedup task per individual")
    if problems and apply:
        for row_number, detail in problems:
            print(f"    FAIL row {row_number}: {detail}")
        print("  nothing was written - fix the references above, then repeat with apply=True")
        return {
            "created": [],
            "skipped": [],
            "failed": problems,
            "warnings": [],
            "individuals_before": before,
            "individuals_after": before,
        }

    for row_number, row in rows:
        try:
            program = _resolve_program(row, programs)
            household = _resolve_household(row, program, households, unusable)
            _check_member(row, program, household, members)
            individual_data = _build_individual_data(row, core_attributes, flex_attributes)
            if _already_present(household, individual_data, seen):
                skipped.append((row_number, f"{individual_data['full_name']} already in {household.unicef_id}"))
                continue
            if individual_data["relationship"] == HEAD:
                warnings.append((row_number, HEAD_WARNING))
            if apply:
                with transaction.atomic():
                    ticket = _add_individual(household, individual_data, business_area, user, description)
                last_details = ticket.add_individual_ticket_details
            created.append(row_number)
        except ValueError as error:
            failed.append((row_number, str(error)))
        except Exception as error:  # noqa: BLE001 - one bad row must not stop the run
            failed.append((row_number, f"{type(error).__name__}: {error}"))

    # clear_cache deletes by pattern, so one call wipes the same key set every closed ticket would.
    if last_details is not None:
        clear_cache(last_details, business_area.slug)

    if apply:
        after = _count_individuals(households)
        delta = after - before
        status = "OK" if delta == len(created) else "MISMATCH"
        print(f"\n  individuals: {before} before, {after} after, +{delta} ({status}, {len(created)} rows created)")
    else:
        after = before
        print(f"\n  individuals: {before} before, +{len(created)} to create")
    print(f"  skipped  : {len(skipped)}")
    print(f"  failed   : {len(failed)}")
    print(f"  warnings : {len(warnings)}")
    for row_number, detail in skipped:
        print(f"    SKIP row {row_number}: {detail}")
    for row_number, detail in failed:
        print(f"    FAIL row {row_number}: {detail}")
    for row_number, detail in warnings:
        print(f"    WARN row {row_number}: {detail}")
    if not apply:
        print("  nothing was written - resolve every FAIL, then repeat with apply=True")
    return {
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "warnings": warnings,
        "individuals_before": before,
        "individuals_after": after,
    }
