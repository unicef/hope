import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { MarkAsReviewedPaymentPlan } from '../MarkAsReviewedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InReviewPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canMarkAsReviewed: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  paymentPlan,
  canReject,
  canMarkAsReviewed,
}: InReviewPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canReject && <RejectPaymentPlan paymentPlanId='33333' />}
      {canMarkAsReviewed && <MarkAsReviewedPaymentPlan paymentPlanId='33333' />}
    </Box>
  );
}
