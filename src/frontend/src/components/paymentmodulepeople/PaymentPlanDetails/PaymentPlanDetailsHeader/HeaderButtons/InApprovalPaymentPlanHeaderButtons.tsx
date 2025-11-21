import { Box } from '@mui/material';
import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canApprove: boolean;
  canAbort: boolean;
}

export function InApprovalPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canApprove,
  canAbort,
}: InApprovalPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canApprove && <ApprovePaymentPlan paymentPlan={paymentPlan} />}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
