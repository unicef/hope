import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import AcceptanceProcess from './AcceptanceProcess';

interface PaymentPlanAcceptanceProcessProps {
  paymentPlan: PaymentPlanDetail;
}

/**
 * Read-only view of the plan's approvals, sent with the plan: its group's, or its instruction's for a
 * Follow-Up Instruction child. Approving happens on the group or instruction page.
 */
export function PaymentPlanAcceptanceProcess({
  paymentPlan,
}: PaymentPlanAcceptanceProcessProps): ReactElement {
  const closure =
    paymentPlan.status === PaymentPlanStatusEnum.CLOSED
      ? { closedBy: paymentPlan.closedBy, closedDate: paymentPlan.statusDate }
      : null;

  return (
    <AcceptanceProcess
      approvalProcess={paymentPlan.approvalProcess}
      closure={closure}
    />
  );
}
