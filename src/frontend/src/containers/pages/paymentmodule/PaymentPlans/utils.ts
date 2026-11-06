import { PaymentPlanDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanDetailBackgroundActionStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import type { PaymentPlanDetail } from './types';

// A payment plan runs one background XLSX action at a time. Export/import may start only
// when the payment plan is idle (status null) or in an error state; the in-progress states
// below block new actions, mirroring the backend `can_start_background_action` gate.
export function isPaymentPlanBackgroundActionBusy(
  paymentPlan: PaymentPlanDetail | null,
): boolean {
  const status = paymentPlan?.backgroundActionStatus;
  return (
    status === 'RECALCULATING' ||
    status === PaymentPlanDetailBackgroundActionStatusEnum.XLSX_EXPORTING ||
    status ===
      PaymentPlanDetailBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION ||
    status ===
      PaymentPlanDetailBackgroundActionStatusEnum.XLSX_IMPORTING_FSP_EXTRA_FIELDS ||
    status === PaymentPlanDetailBackgroundActionStatusEnum.REBUILDING
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

// Untranslated page title for a payment list of the given type; pass the result through t() when rendering.
export function paymentListTitleLabel(
  planType: PlanTypeEnum | undefined,
): string {
  switch (planType) {
    case PlanTypeEnum.FOLLOW_UP:
      return 'Follow-up Payment List';
    case PlanTypeEnum.TOP_UP:
      return 'Top Up Payment List';
    case PlanTypeEnum.TOP_UP_AMENDMENT:
      return 'Top Up Amendment Payment List';
    default:
      return 'Payment List';
  }
}
