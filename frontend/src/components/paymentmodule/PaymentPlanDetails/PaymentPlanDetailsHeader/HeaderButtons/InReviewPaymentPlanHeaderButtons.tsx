import { Box } from '@material-ui/core';
import React from 'react';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { MarkAsReviewedPaymentPlan } from '../MarkAsReviewedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canMarkAsReviewed: boolean;
}

export const InReviewPaymentPlanHeaderButtons = ({
  paymentPlan,
  canReject,
  canMarkAsReviewed,
}: InReviewPaymentPlanHeaderButtonsProps): React.ReactElement => {
  return (
    <Box display='flex' alignItems='center'>
      {canReject && <RejectPaymentPlan paymentPlanId={paymentPlan.id} />}
      {canMarkAsReviewed && (
        <MarkAsReviewedPaymentPlan paymentPlan={paymentPlan} />
      )}
    </Box>
  );
};
