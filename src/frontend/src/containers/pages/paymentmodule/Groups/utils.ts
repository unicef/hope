import { PaymentPlanGroupDeliveryExportPlanTypeEnum } from '@restgenerated/models/PaymentPlanGroupDeliveryExportPlanTypeEnum';
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

// Untranslated label for a plan type — pass the result through t() when rendering.
export function planTypeDisplayLabel(planType: string | undefined): string {
  switch (planType) {
    case 'REGULAR':
      return 'Regular';
    case 'FOLLOW_UP':
      return 'Follow Up';
    case 'TOP_UP':
      return 'Top Up';
    case 'TOP_UP_AMENDMENT':
      return 'Top Up Amendment';
    default:
      return '';
  }
}

// Untranslated label shown next to a batch name; empty for regular batches.
export function batchPlanTypeLabel(planType: string | undefined): string {
  if (planType === 'REGULAR') return '';
  return planTypeDisplayLabel(planType);
}

export interface GroupExportPlanTypeOption {
  value: PaymentPlanGroupDeliveryExportPlanTypeEnum;
  label: string;
}

// Plan types the group can currently export, as translated dialog options.
export function exportablePlanTypeOptions(
  group: PaymentPlanGroupDetail | null,
  t: (key: string) => string,
): GroupExportPlanTypeOption[] {
  const flagged: Array<
    [boolean | undefined, PaymentPlanGroupDeliveryExportPlanTypeEnum]
  > = [
    [group?.canExportRegular, PaymentPlanGroupDeliveryExportPlanTypeEnum.REGULAR],
    [
      group?.canExportFollowUp,
      PaymentPlanGroupDeliveryExportPlanTypeEnum.FOLLOW_UP,
    ],
    [group?.canExportTopUp, PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP],
    [
      group?.canExportTopUpAmendment,
      PaymentPlanGroupDeliveryExportPlanTypeEnum.TOP_UP_AMENDMENT,
    ],
  ];
  return flagged
    .filter(([canExport]) => canExport)
    .map(([, value]) => ({ value, label: t(planTypeDisplayLabel(value)) }));
}
