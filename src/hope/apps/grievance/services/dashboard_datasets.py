"""The four charts of the grievance dashboard, each folded from the same grouped rows."""

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict
from uuid import UUID

from django.db.models import Count, F, Q, QuerySet, Sum
from django.db.models.functions import Extract
from django.utils.encoding import force_str

from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area


def choice_labels(choices: tuple) -> dict[Any, str]:
    return {value: force_str(label) for value, label in choices}


TICKET_ORDERING_CODES = (
    GrievanceTicket.CATEGORY_DATA_CHANGE,
    GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
    GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
    GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
    GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
    GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
    GrievanceTicket.CATEGORY_REFERRAL,
    GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
    GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
    GrievanceTicket.CATEGORY_BENEFICIARY,
)


class Series(TypedDict):
    index: int
    label: str


_CATEGORY_LABELS = choice_labels(GrievanceTicket.CATEGORY_CHOICES)

TICKET_SERIES: dict[int, Series] = {
    code: Series(index=index, label=_CATEGORY_LABELS[code]) for index, code in enumerate(TICKET_ORDERING_CODES)
}


class TicketGroup(TypedDict):
    category: int
    status: int
    issue_type: int | None
    admin2: UUID | None
    ticket_count: int
    resolution_days: int | None


def transform_to_chart_dataset(rows: Iterable[tuple[Any, Any]]) -> dict[str, Any]:
    labels, data = [], []
    for row in rows:
        label: Any
        value: Any
        label, value = row
        labels.append(label)
        data.append(value)

    return {"labels": labels, "datasets": [{"data": data}]}


def is_user_generated(category: int, issue_type: int | None) -> bool:
    return category in GrievanceTicket.MANUAL_CATEGORY_CODES and issue_type not in GrievanceTicket.SYSTEM_ISSUE_TYPES


def is_system_generated(category: int, issue_type: int | None) -> bool:
    return category in GrievanceTicket.SYSTEM_CATEGORY_CODES or issue_type in GrievanceTicket.SYSTEM_ISSUE_TYPES


def average_resolution(total_days: Any, closed_count: int) -> float:
    """Mean resolution in days; 0.00 when nothing is closed."""
    if not closed_count:
        return 0.00
    return round(float(total_days) / closed_count, 2)


class DashboardDataset(ABC):
    """One chart on the grievance dashboard, accumulated group by group.

    Every dataset processes each group once in `fold_groups`, so a new chart is a subclass plus one
    entry in `build_dashboard_data`
    """

    @abstractmethod
    def add(self, group: TicketGroup) -> None:
        """Fold one group into this dataset."""

    @abstractmethod
    def result(self) -> dict[str, Any]:
        """Return the chart payload, shaped for `GrievanceDashboardSerializer`."""


@dataclass
class TicketsByType(DashboardDataset):
    """Counts and mean resolution time, split into user and system-generated tickets.

    The two predicates are independent, so a group can land in both halves or neither.
    """

    user_generated_count: int = 0
    system_generated_count: int = 0
    closed_user_generated_count: int = 0
    closed_system_generated_count: int = 0
    user_generated_days: float = 0.0
    system_generated_days: float = 0.0

    def add(self, group: TicketGroup) -> None:
        category, issue_type, count = group["category"], group["issue_type"], group["ticket_count"]
        closed = group["status"] == GrievanceTicket.STATUS_CLOSED
        resolution_days = float(group["resolution_days"] or 0)

        if is_user_generated(category, issue_type):
            self.user_generated_count += count
            if closed:
                self.closed_user_generated_count += count
                self.user_generated_days += resolution_days

        if is_system_generated(category, issue_type):
            self.system_generated_count += count
            if closed:
                self.closed_system_generated_count += count
                self.system_generated_days += resolution_days

    def result(self) -> dict[str, Any]:
        return {
            "user_generated_count": self.user_generated_count,
            "system_generated_count": self.system_generated_count,
            "closed_user_generated_count": self.closed_user_generated_count,
            "closed_system_generated_count": self.closed_system_generated_count,
            "user_generated_avg_resolution": average_resolution(
                self.user_generated_days, self.closed_user_generated_count
            ),
            "system_generated_avg_resolution": average_resolution(
                self.system_generated_days, self.closed_system_generated_count
            ),
        }


@dataclass
class TicketsByChoice(DashboardDataset):
    """One bar per distinct value of a choice field, biggest first, ties broken on the label."""

    key: Literal["category", "status"]
    choices: tuple
    counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    labels: dict[Any, str] = field(init=False)

    def __post_init__(self) -> None:
        self.labels = choice_labels(self.choices)

    def add(self, group: TicketGroup) -> None:
        self.counts[self.labels.get(group[self.key])] += group["ticket_count"]

    def result(self) -> dict[str, Any]:
        return transform_to_chart_dataset(sorted(self.counts.items(), key=lambda item: (-item[1], item[0] or "")))


@dataclass
class TicketsByLocationAndCategory(DashboardDataset):
    """Per-admin2 category breakdown, one row per area name and one series per category."""

    per_area: dict[Any, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0] * len(TICKET_SERIES)))

    def add(self, group: TicketGroup) -> None:
        admin2, category = group["admin2"], group["category"]

        if admin2 is None:
            return

        category_index = TICKET_SERIES[category]["index"]
        self.per_area[admin2][category_index] += group["ticket_count"]

    def result(self) -> dict[str, Any]:
        rows: dict[str, list[int]] = {}
        for name, area_id in Area.objects.filter(id__in=list(self.per_area)).order_by("name").values_list("name", "id"):
            row = rows.setdefault(name, [0] * len(TICKET_SERIES))
            for index, count in enumerate(self.per_area[area_id]):
                row[index] += count

        if not rows:
            return {"labels": [], "datasets": []}

        columns = zip(*rows.values(), strict=True)
        return {
            "labels": list(rows),
            "datasets": [
                {"label": series["label"], "data": list(column)}
                for series, column in zip(TICKET_SERIES.values(), columns, strict=True)
            ],
        }


def fold_groups(groups: Iterable[TicketGroup], datasets: Mapping[str, DashboardDataset]) -> dict[str, dict]:
    """Feed every group to every dataset once, and collect the finished chart payloads."""
    for group in groups:
        for dataset in datasets.values():
            dataset.add(group)
    return {name: dataset.result() for name, dataset in datasets.items()}


def build_dashboard_data(base_queryset: QuerySet) -> dict[str, Any]:
    """Every chart on the grievance dashboard, from one grouped pass over `base_queryset`."""
    datasets: dict[str, DashboardDataset] = {
        "tickets_by_type": TicketsByType(),
        "tickets_by_status": TicketsByChoice("status", GrievanceTicket.STATUS_CHOICES),
        "tickets_by_category": TicketsByChoice("category", GrievanceTicket.CATEGORY_CHOICES),
        "tickets_by_location_and_category": TicketsByLocationAndCategory(),
    }
    groups: QuerySet[GrievanceTicket, TicketGroup] = (
        base_queryset.values("category", "status", "issue_type", "admin2")
        .annotate(
            ticket_count=Count("id"),
            resolution_days=Sum(
                Extract(F("updated_at") - F("created_at"), "days"),
                filter=Q(status=GrievanceTicket.STATUS_CLOSED),
            ),
        )
        .order_by()
    )
    return fold_groups(groups, datasets)
