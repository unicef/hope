import type { ReactElement } from 'react';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import AcceptanceProcess from './AcceptanceProcess';

interface PaymentListAcceptanceProcessProps {
  paymentList: PaymentListDetail;
}

/**
 * Read-only view of the payment list's approvals, sent with the payment list: its payment plan's, or its
 * instruction's for a Follow-Up Instruction child. Approving happens on the payment plan or instruction page.
 */
export function PaymentListAcceptanceProcess({
  paymentList,
}: PaymentListAcceptanceProcessProps): ReactElement {
  const closure =
    paymentList.status === PaymentListStatusEnum.CLOSED
      ? { closedBy: paymentList.closedBy, closedDate: paymentList.statusDate }
      : null;

  return (
    <AcceptanceProcess
      approvalProcess={paymentList.approvalProcess}
      closure={closure}
    />
  );
}
