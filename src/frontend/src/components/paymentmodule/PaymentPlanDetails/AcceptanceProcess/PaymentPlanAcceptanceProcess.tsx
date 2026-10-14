import type { ReactElement } from 'react';
import { usePaymentPlanGroup } from '@hooks/usePaymentPlanGroup';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import AcceptanceProcess from './AcceptanceProcess';

interface PaymentPlanAcceptanceProcessProps {
  paymentPlan: PaymentPlanDetail;
}

/** Read-only view of the plan's group approvals; approving happens on the group page. */
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
      approvalProcess={group?.approvalProcess}
      closure={closure}
    />
  );
}
