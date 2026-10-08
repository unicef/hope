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

