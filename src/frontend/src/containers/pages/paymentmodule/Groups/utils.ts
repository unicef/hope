import { PaymentPlanGroupDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanGroupDetailBackgroundActionStatusEnum';
import { PaymentPlanGroupDetail } from './types';

// A group runs one background XLSX action at a time. Export/import may start only
// when the group is idle (status null) or in an error state; the in-progress states
// below block new actions, mirroring the backend `can_start_background_action` gate.
export function isGroupBackgroundActionBusy(
  group: PaymentPlanGroupDetail | null,
): boolean {
  const status = group?.backgroundActionStatus;
  return (
    status === PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_EXPORTING ||
    status === PaymentPlanGroupDetailBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION
  );
}

export function planTypeDisplayLabel(planType: string | undefined): string {
  switch (planType) {
    case 'REGULAR':
      return 'Regular';
    case 'FOLLOW_UP':
      return 'Follow Up';
    case 'TOP_UP':
      return 'Top Up';
    default:
      return '';
  }
}

// Suffix shown next to a batch name for non-regular batches, e.g. " Follow Up".
export function batchPlanTypeLabel(planType: string | undefined): string {
  if (planType === undefined || planType === 'REGULAR') return '';
  const label = planTypeDisplayLabel(planType);
  return label ? ` ${label}` : '';
}
