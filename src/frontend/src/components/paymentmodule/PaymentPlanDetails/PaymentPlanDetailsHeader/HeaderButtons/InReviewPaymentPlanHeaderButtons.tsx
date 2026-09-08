import { Box } from '@mui/material';
import { MarkAsReleasedPaymentPlan } from '../MarkAsReleasedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canMarkAsReleased: boolean;
  canAbort: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canMarkAsReleased,
  canAbort,
}: InReviewPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canMarkAsReleased && !paymentPlan.visionManaged && (
        <MarkAsReleasedPaymentPlan paymentPlan={paymentPlan} />
      )}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
