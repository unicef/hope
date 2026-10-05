import { Box } from '@mui/material';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';

export interface InAcceptancePaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canAbort: boolean;
}

/** In approval, authorization or review; the acceptance actions live on the group page. */
export function InAcceptancePaymentPlanHeaderButtons({
  paymentPlan,
  canAbort,
}: InAcceptancePaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
