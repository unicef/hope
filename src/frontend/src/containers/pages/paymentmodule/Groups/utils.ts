import { PaymentPlanGroupDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanGroupDetailBackgroundActionStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import type { PaymentPlanGroupDetail } from './types';

// A group runs one background XLSX action at a time. Export/import may start only
// when the group is idle (status null) or in an error state; the in-progress states
// below block new actions, mirroring the backend `can_start_background_action` gate.
export function isGroupBackgroundActionBusy(
  group: PaymentPlanGroupDetail | null,
): boolean {
  const status = group?.backgroundActionStatus;
  return (
    status ===
      PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_EXPORTING ||
    status ===
      PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION
  );
}

// Untranslated label for a plan type — pass the result through t() when rendering.
export function planTypeDisplayLabel(
  planType: PlanTypeEnum | undefined,
): string {
  switch (planType) {
    case PlanTypeEnum.REGULAR:
      return 'Regular';
    case PlanTypeEnum.FOLLOW_UP:
      return 'Follow Up';
    case PlanTypeEnum.TOP_UP:
      return 'Top Up';
    case PlanTypeEnum.TOP_UP_AMENDMENT:
      return 'Top Up Amendment';
    default:
      return '';
  }
}

// Untranslated label shown next to a batch name; empty for regular batches.
export function batchPlanTypeLabel(planType: PlanTypeEnum | undefined): string {
  if (planType === PlanTypeEnum.REGULAR) return '';
  return planTypeDisplayLabel(planType);
}

export interface GroupExportPlanTypeOption {
  value: PlanTypeEnum;
  label: string;
}

// Plan types the group can currently export, as translated dialog options.
export function exportablePlanTypeOptions(
  group: PaymentPlanGroupDetail | null,
  t: (key: string) => string,
): GroupExportPlanTypeOption[] {
  const flagged: Array<[boolean | undefined, PlanTypeEnum]> = [
    [group?.canExportRegular, PlanTypeEnum.REGULAR],
    [group?.canExportFollowUp, PlanTypeEnum.FOLLOW_UP],
    [group?.canExportTopUp, PlanTypeEnum.TOP_UP],
    [group?.canExportTopUpAmendment, PlanTypeEnum.TOP_UP_AMENDMENT],
  ];
  return flagged
    .filter(([canExport]) => canExport)
    .map(([, value]) => ({ value, label: t(planTypeDisplayLabel(value)) }));
}
