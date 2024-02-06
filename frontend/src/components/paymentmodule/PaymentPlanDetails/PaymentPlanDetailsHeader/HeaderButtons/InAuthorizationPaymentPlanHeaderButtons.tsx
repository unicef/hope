import { Box } from '@mui/material';
import React from 'react';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { AuthorizePaymentPlan } from '../AuthorizePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InAuthorizationPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canAuthorize: boolean;
}

export function InAuthorizationPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canAuthorize,
}: InAuthorizationPaymentPlanHeaderButtonsProps): React.ReactElement {
  return (
    <Box display="flex" alignItems="center">
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canAuthorize && <AuthorizePaymentPlan paymentPlan={paymentPlan} />}
    </Box>
  );
}
