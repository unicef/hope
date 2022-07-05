import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ApprovePaymentPlan } from '../ApprovePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InApprovalPaymentPlanHeaderButtonsProps {
  setEditState: Function;
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function InApprovalPaymentPlanHeaderButtons({
  setEditState,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InApprovalPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canLock && (
        <Box m={2}>
          <RejectPaymentPlan paymentPlanId='33333' />
        </Box>
      )}
      {canLock && <ApprovePaymentPlan paymentPlanId='33333' />}
    </div>
  );
}
