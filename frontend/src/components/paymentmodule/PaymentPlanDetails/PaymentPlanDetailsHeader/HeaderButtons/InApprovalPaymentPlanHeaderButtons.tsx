import { Box } from '@material-ui/core';
import React from 'react';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canApprove: boolean;
}

export const InApprovalPaymentPlanHeaderButtons = ({
  paymentPlan,
  canReject,
  canApprove,
}: InApprovalPaymentPlanHeaderButtonsProps): React.ReactElement => {
  return (
    <Box display='flex' alignItems='center'>
      {canReject && (
        <Box m={2}>
          <RejectPaymentPlan paymentPlanId={paymentPlan.id} />
        </Box>
      )}
      {canApprove && <ApprovePaymentPlan paymentPlanId={paymentPlan.id} />}
    </Box>
  );
};
