import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { AuthorizePaymentPlan } from '../AuthorizePaymentPlan';
import { RejectPaymentPlan } from '../RejectPaymentPlan';

export interface InAuthorizationPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canReject: boolean;
  canAuthorize: boolean;
}

export const InAuthorizationPaymentPlanHeaderButtons = ({
  paymentPlan,
  canReject,
  canAuthorize,
}: InAuthorizationPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canReject && <RejectPaymentPlan paymentPlanId='33333' />}
      {canAuthorize && <AuthorizePaymentPlan paymentPlanId='33333' />}
    </div>
  );
};
