import os
import re
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Manager
from django.utils import timezone

from hope.apps.core.utils import nested_getattr

if TYPE_CHECKING:
    from hope.models.program import Program

GLOBAL_SEGMENT = "_global"
UNASSIGNED_SEGMENT = "_unassigned"

# Mirrors the max_length declared on every FileField that uploads through this module.
MAX_NAME_LENGTH = 255
# Room for the "_xxxxxxx" suffix FileSystemStorage appends when a name is already taken.
COLLISION_SUFFIX_LENGTH = 8

DEFAULT_PROGRAM_PATH = "program"
DEFAULT_BUSINESS_AREA_SLUG_PATH = "business_area.slug"

# Models whose programme is not reachable as `instance.program`; the value is the path to it.
PROGRAM_PATHS = {
    "grievance.GrievanceDocument": "grievance_ticket.programs",
    "grievance.GrievanceTicket": "programs",
    "household.Document": "individual.program",
    "payment.PaymentPlan": "program_cycle.program",
    "payment.PaymentPlanGroup": "cycle.program",
    "payment.PaymentPlanSupportingDocument": "payment_plan.program_cycle.program",
    "payment.PaymentVerificationPlan": "payment_plan.program_cycle.program",
    "payment.WesternUnionPaymentPlanReport": "payment_plan.program_cycle.program",
    "periodic_data_update.PDUXlsxUpload": "template.program",
}

# Models filed under the programme of the object they are attached to. The value leads to that
# object, which is then resolved like any other instance.
OWNER_PATHS = {"core.FileTemp": "content_object"}

# Models whose business area slug is not reachable as `instance.business_area.slug`; the value
# is the path to it.
BUSINESS_AREA_SLUG_PATHS = {
    "grievance.GrievanceDocument": "grievance_ticket.business_area.slug",
    "registration_data.ImportData": "business_area_slug",
}

_UNSAFE_SEGMENT_CHARS = re.compile(r"[^A-Za-z0-9_-]")


def _clean_segment(value: str | None, fallback: str) -> str:
    """Sanitise one directory segment; return `fallback` when nothing usable is left."""
    cleaned = _UNSAFE_SEGMENT_CHARS.sub("_", value or "")
    return cleaned if cleaned.strip("_") else fallback


def _fit_filename(prefix: str, filename: str) -> str:
    """Trim the filename so `prefix/filename` fits the column, keeping the extension."""
    name = os.path.basename(filename.replace("\\", "/"))
    max_filename_length = max(MAX_NAME_LENGTH - len(prefix) - len("/") - COLLISION_SUFFIX_LENGTH, 1)
    if len(name) <= max_filename_length:
        return name
    root, extension = os.path.splitext(name)
    keep = max_filename_length - len(extension)
    if keep < 1:
        return name[:max_filename_length]
    return f"{root[:keep]}{extension}"


def build_upload_path(
    filename: str,
    *,
    year: int | None = None,
    business_area_slug: str | None = None,
    program_code: str | None = None,
) -> str:
    """Build a `<year>/<business area>/<programme>/<filename>` storage path.

    Falls back to `_unassigned` for the programme segment and to a two-level
    `<year>/_global/` path when there is no business area either.
    """
    directories = [str(year or timezone.localdate().year)]
    if business_area_slug:
        directories.append(_clean_segment(business_area_slug, UNASSIGNED_SEGMENT))
        directories.append(_clean_segment(program_code, UNASSIGNED_SEGMENT))
    else:
        directories.append(GLOBAL_SEGMENT)
    prefix = "/".join(directories)
    return f"{prefix}/{_fit_filename(prefix, filename)}"


def _registered_path(registry: dict[str, str], model: type[Any]) -> str | None:
    """Look up `model` in a registry keyed by `"app_label.ModelName"`.

    Returns the dotted path to follow from an instance, such as `"payment_plan.program_cycle.program"`.
    `None` means nothing is registered and the caller falls back to its default path.

    The model's own label is checked first, then its parents'. `KoboImportData` is not registered
    itself, so it resolves through `ImportData`, the parent it inherits its file field from. A child
    registered directly overrides the parent. A proxy is looked up under the model it proxies.
    """
    meta = model._meta.concrete_model._meta
    for ancestor in (meta.model, *meta.all_parents):
        if path := registry.get(ancestor._meta.label):
            return path
    return None


def get_program(instance: Any) -> "Program | None":
    from hope.models.program import Program

    if instance is None:
        return None
    if isinstance(instance, Program):
        return instance
    if owner_path := _registered_path(OWNER_PATHS, type(instance)):
        try:
            owner = nested_getattr(instance, owner_path, None)
        except (ObjectDoesNotExist, ValidationError, ValueError, TypeError):
            return None
        return get_program(owner)
    program = nested_getattr(instance, _registered_path(PROGRAM_PATHS, type(instance)) or DEFAULT_PROGRAM_PATH, None)
    if isinstance(program, Manager):
        return program.order_by("id").first()
    return program


def get_business_area_slug(instance: Any) -> str | None:
    if instance is None:
        return None
    path = _registered_path(BUSINESS_AREA_SLUG_PATHS, type(instance)) or DEFAULT_BUSINESS_AREA_SLUG_PATH
    return nested_getattr(instance, path, None)


def upload_path(instance: Any, filename: str) -> str:
    """Resolve the storage path of `filename` from the scope of `instance`.

    Files land under `<programme start year>/<business area>/<programme code>/`, or under
    `<upload year>/<business area>/_unassigned/` and `<upload year>/_global/` when `instance`
    reaches no programme or no business area. Set as the `upload_to` of every file field, and
    called the same way before `default_storage.save` wherever a file is written directly.
    """
    program = get_program(instance)
    if program is None:
        return build_upload_path(filename, business_area_slug=get_business_area_slug(instance))
    return build_upload_path(
        filename,
        year=program.start_date.year,
        business_area_slug=program.business_area.slug,
        program_code=program.code,
    )
