import { Box } from '@mui/material';
import { AuthorizePaymentPlan } from '../AuthorizePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { AbortPaymentPlan } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader/AbortPaymentPlan';

export interface InAuthorizationPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanDetail;
  canReject: boolean;
  canAuthorize: boolean;
  canAbort: boolean;
}

export function InAuthorizationPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canAuthorize,
  canAbort,
}: InAuthorizationPaymentPlanHeaderButtonsProps): ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canAuthorize && <AuthorizePaymentPlan paymentPlan={paymentPlan} />}
      {canAbort && <AbortPaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
