"""Read-only report of the Payment Plan Groups that the Payment Plan Groups release cannot migrate as they are.

Run on production before deploying the release that makes the group the Payment Plan. It changes nothing.

Blocking: the data migrations refuse to run while any group is listed here.
Review: the migrations run and change data in these groups.

Follow-Up Instruction plans leave their group and follow-up / top-up plans move into new linked groups, so they are
compared with the plans they end up with, not with their current group.

Usage:
    ./manage.py check_payment_plan_groups_before_release
    ./manage.py check_payment_plan_groups_before_release --business-area <slug>
"""

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Count

from hope.contrib.vision.choices import VisionStatus
from hope.models import ApprovalProcess, PaymentPlan, PaymentPlanGroup

# A plan before the FSP lock belongs to an OPEN group; the FSP lock is the group lock.
PRE_LOCK_PLAN_STATUSES = frozenset(
    {
        PaymentPlan.Status.TP_OPEN,
        PaymentPlan.Status.TP_LOCKED,
        PaymentPlan.Status.TP_STEFICON_WAIT,
        PaymentPlan.Status.TP_STEFICON_RUN,
        PaymentPlan.Status.TP_STEFICON_COMPLETED,
        PaymentPlan.Status.TP_STEFICON_ERROR,
        PaymentPlan.Status.DRAFT,
        PaymentPlan.Status.OPEN,
        PaymentPlan.Status.LOCKED,
    }
)
MID_APPROVAL_STATUSES = frozenset(
    {PaymentPlan.Status.IN_APPROVAL, PaymentPlan.Status.IN_AUTHORIZATION, PaymentPlan.Status.IN_REVIEW}
)
VISION_SETTLED_STATUSES = frozenset({VisionStatus.NOT_SENT.value, VisionStatus.RELEASED.value})


def group_status_for_plan_status(plan_status: str) -> str:
    if plan_status in PRE_LOCK_PLAN_STATUSES:
        return "OPEN"
    if plan_status == PaymentPlan.Status.LOCKED_FSP:
        return "LOCKED"
    return plan_status


@dataclass
class Plan:
    id: Any
    unicef_id: str | None
    group_id: Any
    status: str
    plan_type: str
    follow_up_instruction_id: Any
    follow_up_instruction_unicef_id: str | None
    fsp_id: Any
    currency_id: Any
    use_payment_gateway: bool
    exchange_rate: Decimal | None
    custom_exchange_rate: bool
    dispersion_dates: tuple[Any, Any]
    vision_status: str

    @property
    def is_regular_component(self) -> bool:
        """A plan that stays in its group: not a legacy follow-up / top-up and not an instruction child."""
        return self.plan_type == PaymentPlan.PlanType.REGULAR and self.follow_up_instruction_id is None

    @property
    def owner(self) -> tuple:
        """What the plan belongs to after the release: its instruction, a linked group, or its own group."""
        if self.follow_up_instruction_id is not None:
            return ("instruction", self.follow_up_instruction_id)
        if self.plan_type != PaymentPlan.PlanType.REGULAR:
            return ("linked", self.group_id, self.plan_type, group_status_for_plan_status(self.status))
        return ("group", self.group_id)


@dataclass
class Section:
    title: str
    explanation: str
    lines: list[str] = field(default_factory=list)


class Command(BaseCommand):
    help = "Report Payment Plan Groups that need fixing before the Payment Plan Groups release (read-only)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--business-area", help="Only check this business area (slug).")

    def handle(self, *args: Any, **options: Any) -> None:
        groups = PaymentPlanGroup.objects.select_related("cycle__program__business_area")
        if business_area := options.get("business_area"):
            groups = groups.filter(cycle__program__business_area__slug=business_area)
        self.groups = {group.id: group for group in groups}
        self.plans_by_group = self._plans_by_group(self.groups.keys())
        self.plans_by_owner: dict[tuple, list[Plan]] = defaultdict(list)
        for plans in self.plans_by_group.values():
            for plan in plans:
                self.plans_by_owner[plan.owner].append(plan)

        blocking = [
            self._mixed_statuses(),
            self._mixed_values("fsp_id", "FSP"),
            self._mixed_values("currency_id", "currency"),
            self._mixed_payment_gateway_flag(),
            self._mixed_exchange_rates(),
            self._mixed_vision_statuses(),
            self._vision_in_progress(),
        ]
        review = [
            self._several_plans_mid_approval(),
            self._instruction_children_in_different_groups(),
            self._mixed_dispersion_dates(),
        ]

        self.stdout.write(f"Checked {len(self.groups)} groups, {sum(map(len, self.plans_by_group.values()))} plans.\n")
        for heading, sections in (("BLOCKING", blocking), ("REVIEW", review)):
            self._write(heading, sections)
        blocking_count = sum(len(section.lines) for section in blocking)
        self.stdout.write(f"\nBlocking findings: {blocking_count}")

    @staticmethod
    def _plans_by_group(group_ids: Iterable) -> dict[Any, list[Plan]]:
        rows = PaymentPlan.all_objects.filter(is_removed=False, payment_plan_group_id__in=list(group_ids)).values_list(
            "id",
            "unicef_id",
            "payment_plan_group_id",
            "status",
            "plan_type",
            "follow_up_instruction_id",
            "follow_up_instruction__unicef_id",
            "financial_service_provider_id",
            "currency_id",
            "use_payment_gateway",
            "exchange_rate",
            "custom_exchange_rate",
            "dispersion_start_date",
            "dispersion_end_date",
            "internal_data__vision__status",
        )
        plans_by_group: dict[Any, list[Plan]] = defaultdict(list)
        for row in rows.order_by("created_at"):
            plans_by_group[row[2]].append(
                Plan(
                    id=row[0],
                    unicef_id=row[1],
                    group_id=row[2],
                    status=row[3],
                    plan_type=row[4],
                    follow_up_instruction_id=row[5],
                    follow_up_instruction_unicef_id=row[6],
                    fsp_id=row[7],
                    currency_id=row[8],
                    use_payment_gateway=row[9],
                    exchange_rate=row[10],
                    custom_exchange_rate=row[11],
                    dispersion_dates=(row[12], row[13]),
                    vision_status=row[14] or VisionStatus.NOT_SENT.value,
                )
            )
        return plans_by_group

    def _label(self, group_id: Any) -> str:
        group = self.groups[group_id]
        program = group.cycle.program
        return f"{program.business_area.slug} | {program.name} | {group.cycle.title} | {group.unicef_id} '{group.name}'"

    def _owner_label(self, owner: tuple, plans: list[Plan]) -> str:
        if owner[0] == "instruction":
            return f"{self._label(plans[0].group_id)} | instruction {plans[0].follow_up_instruction_unicef_id}"
        if owner[0] == "linked":
            _, group_id, plan_type, status = owner
            return f"{self._label(group_id)} | new linked {plan_type} group ({status})"
        return self._label(owner[1])

    @staticmethod
    def _plan_list(plans: Iterable[Plan], value: Any) -> str:
        return ", ".join(f"{plan.unicef_id}={value(plan)}" for plan in plans)

    def _mixed_statuses(self) -> Section:
        section = Section(
            "Plans in different statuses",
            "The group gets one status. Statuses before the FSP lock count as one.",
        )
        for group_id, plans in self.plans_by_group.items():
            components = [plan for plan in plans if plan.is_regular_component]
            if len({group_status_for_plan_status(plan.status) for plan in components}) > 1:
                section.lines.append(f"{self._label(group_id)}: {self._plan_list(components, lambda p: p.status)}")
        return section

    def _mixed_values(self, attribute: str, label: str) -> Section:
        section = Section(
            f"Plans with different {label}",
            f"The group gets one {label}.",
        )
        for group_id, plans in self.plans_by_group.items():
            values = {getattr(plan, attribute) for plan in plans} - {None}
            if len(values) > 1:
                section.lines.append(
                    f"{self._label(group_id)}: {self._plan_list(plans, lambda p: getattr(p, attribute))}"
                )
        return section

    def _several_plans_mid_approval(self) -> Section:
        section = Section(
            "Several plans mid-approval in one group",
            "Only the newest approval process stays active. Approvals on the other plans no longer count.",
        )
        mid_approval = {
            group_id: [plan for plan in plans if plan.is_regular_component and plan.status in MID_APPROVAL_STATUSES]
            for group_id, plans in self.plans_by_group.items()
        }
        mid_approval = {group_id: plans for group_id, plans in mid_approval.items() if len(plans) > 1}
        approvals_by_plan = self._approvals_on_latest_process(
            plan.id for plans in mid_approval.values() for plan in plans
        )
        for group_id, plans in mid_approval.items():
            section.lines.append(
                f"{self._label(group_id)}: "
                + self._plan_list(plans, lambda p: f"{p.status} ({approvals_by_plan.get(p.id, 0)} approvals)")
            )
        return section

    @staticmethod
    def _approvals_on_latest_process(plan_ids: Iterable) -> dict[Any, int]:
        processes = (
            ApprovalProcess.objects.filter(payment_plan_id__in=list(plan_ids))
            .annotate(approvals_count=Count("approvals"))
            .order_by("payment_plan_id", "-created_at")
            .values_list("payment_plan_id", "approvals_count")
        )
        approvals: dict[Any, int] = {}
        for plan_id, approvals_count in processes:
            approvals.setdefault(plan_id, approvals_count)
        return approvals

    def _instruction_children_in_different_groups(self) -> Section:
        section = Section(
            "Follow-Up Instructions whose plans sit in groups with different FSP or currency",
            "The instruction takes the FSP and currency of its first plan's group.",
        )
        group_values = {
            group_id: frozenset((plan.fsp_id, plan.currency_id) for plan in plans)
            for group_id, plans in self.plans_by_group.items()
        }
        groups_by_instruction: dict[Any, set] = defaultdict(set)
        for group_id, plans in self.plans_by_group.items():
            for plan in plans:
                if plan.follow_up_instruction_id is not None:
                    groups_by_instruction[plan.follow_up_instruction_id].add(group_id)
        for instruction_id, group_ids in groups_by_instruction.items():
            values = set().union(*(group_values[group_id] for group_id in group_ids))
            if len({fsp_id for fsp_id, _ in values} - {None}) > 1 or len({cur for _, cur in values} - {None}) > 1:
                group_labels = sorted(str(self.groups[group_id].unicef_id) for group_id in group_ids)
                instruction_unicef_id = next(
                    plan.follow_up_instruction_unicef_id
                    for plan in self.plans_by_group[next(iter(group_ids))]
                    if plan.follow_up_instruction_id == instruction_id
                )
                section.lines.append(f"instruction {instruction_unicef_id}: groups {', '.join(group_labels)}")
        return section

    def _mixed_payment_gateway_flag(self) -> Section:
        section = Section(
            "Plans with different use_payment_gateway flag",
            "Every group and Follow-Up Instruction gets one flag.",
        )
        for owner, plans in self.plans_by_owner.items():
            if len({plan.use_payment_gateway for plan in plans}) > 1:
                section.lines.append(
                    f"{self._owner_label(owner, plans)}: {self._plan_list(plans, lambda p: p.use_payment_gateway)}"
                )
        return section

    def _mixed_exchange_rates(self) -> Section:
        section = Section(
            "Plans with different exchange rates",
            "The group gets one exchange rate.",
        )
        for owner, plans in self.plans_by_owner.items():
            rated = [plan for plan in plans if plan.exchange_rate is not None]
            if len({(plan.exchange_rate, plan.custom_exchange_rate) for plan in rated}) > 1:
                section.lines.append(
                    f"{self._owner_label(owner, plans)}: "
                    + self._plan_list(
                        rated, lambda p: f"{p.exchange_rate}{' custom' if p.custom_exchange_rate else ''}"
                    )
                )
        return section

    def _mixed_dispersion_dates(self) -> Section:
        section = Section(
            "Plans with different dispersion dates",
            "Every group and Follow-Up Instruction gets the earliest start and the latest end of its plans.",
        )
        for owner, plans in self.plans_by_owner.items():
            dated = [plan for plan in plans if any(plan.dispersion_dates)]
            if len({plan.dispersion_dates for plan in dated}) > 1:
                section.lines.append(
                    f"{self._owner_label(owner, plans)}: "
                    + self._plan_list(dated, lambda p: f"{p.dispersion_dates[0]}..{p.dispersion_dates[1]}")
                )
        return section

    def _mixed_vision_statuses(self) -> Section:
        section = Section(
            "Plans with different Vision status",
            "The group gets one Vision status.",
        )
        for owner, plans in self.plans_by_owner.items():
            if len({plan.vision_status for plan in plans}) > 1:
                section.lines.append(
                    f"{self._owner_label(owner, plans)}: {self._plan_list(plans, lambda p: p.vision_status)}"
                )
        return section

    def _vision_in_progress(self) -> Section:
        section = Section(
            "Plans in the middle of the Vision flow",
            "Vision knows these plans by the plan id; after the release it uses the group id.",
        )
        for owner, plans in self.plans_by_owner.items():
            in_progress = [plan for plan in plans if plan.vision_status not in VISION_SETTLED_STATUSES]
            if in_progress:
                section.lines.append(
                    f"{self._owner_label(owner, plans)}: {self._plan_list(in_progress, lambda p: p.vision_status)}"
                )
        return section

    def _write(self, heading: str, sections: list[Section]) -> None:
        self.stdout.write(f"\n===== {heading} =====")
        for section in sections:
            self.stdout.write(f"\n--- {section.title}: {len(section.lines)} ---")
            self.stdout.write(section.explanation)
            for line in section.lines:
                self.stdout.write(f"  {line}")
