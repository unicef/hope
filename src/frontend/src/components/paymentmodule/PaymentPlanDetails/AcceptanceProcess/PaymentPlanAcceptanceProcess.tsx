import type { ReactElement } from 'react';
import { usePaymentPlanGroup } from '@hooks/usePaymentPlanGroup';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import AcceptanceProcess from './AcceptanceProcess';

interface PaymentPlanAcceptanceProcessProps {
  paymentPlan: PaymentPlanDetail;
}

/**
 * Read-only view of the plan's approvals: its group's for a grouped plan, its instruction's for a
 * Follow-Up Instruction child (sent with the plan). Approving happens on the group or instruction page.
 */
export function PaymentPlanAcceptanceProcess({
  paymentPlan,
}: PaymentPlanAcceptanceProcessProps): ReactElement {
  const { data: group } = usePaymentPlanGroup(paymentPlan.paymentPlanGroup?.id);
  const closure =
    paymentPlan.status === PaymentPlanStatusEnum.CLOSED
      ? { closedBy: paymentPlan.closedBy, closedDate: paymentPlan.statusDate }
      : null;

  return (
    <AcceptanceProcess
      approvalProcess={
        paymentPlan.isInstructionManaged
          ? paymentPlan.approvalProcess
          : group?.approvalProcess
      }
      closure={closure}
    />
  );
}
