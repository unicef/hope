import { PaymentPlanBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanBackgroundActionStatusEnum';
import { PaymentPlanGroupDetail } from './types';

// A group runs one background XLSX action at a time. Export/import may start only
// when the group is idle (status null) or in an error state; the in-progress states
// below block new actions, mirroring the backend `can_start_background_action` gate.
export function isGroupBackgroundActionBusy(
  group: PaymentPlanGroupDetail | null,
): boolean {
  const status = group?.backgroundActionStatus;
  return (
    status === PaymentPlanBackgroundActionStatusEnum.XLSX_EXPORTING ||
    status === PaymentPlanBackgroundActionStatusEnum.XLSX_IMPORTING_RECONCILIATION
  );
}
