import { Box } from '@mui/material';
import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canApprove: boolean;
}

export function InApprovalPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canApprove,
}: InApprovalPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canApprove && <ApprovePaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
