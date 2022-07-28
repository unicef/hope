import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canApprove: boolean;
}

export function InApprovalPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canApprove,
}: InApprovalPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canReject && (
        <Box m={2}>
          <RejectPaymentPlan paymentPlanId='33333' />
        </Box>
      )}
      {canApprove && <ApprovePaymentPlan paymentPlanId='33333' />}
    </div>
  );
}
