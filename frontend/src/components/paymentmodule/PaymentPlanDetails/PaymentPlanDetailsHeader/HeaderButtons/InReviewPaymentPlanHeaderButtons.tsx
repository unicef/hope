import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MarkAsReviewedPaymentPlan } from '../MarkAsReviewedPaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InReviewPaymentPlanHeaderButtonsProps {
  setEditState: Function;
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  setEditState,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InReviewPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canLock && <RejectPaymentPlan paymentPlanId='33333' />}
      {canLock && <MarkAsReviewedPaymentPlan paymentPlanId='33333' />}
    </div>
  );
}
