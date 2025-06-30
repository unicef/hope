import { Box } from '@mui/material';
import { MarkAsReleasedPaymentPlan } from '../MarkAsReleasedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canMarkAsReleased: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canMarkAsReleased,
}: InReviewPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canMarkAsReleased && (
        <MarkAsReleasedPaymentPlan paymentPlan={paymentPlan} />
      )}
    </Box>
  );
}
