import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { usePaymentPlanAction } from '../../../../../hooks/usePaymentPlanAction';
import { useSnackbar } from '../../../../../hooks/useSnackBar';
import { Action, PaymentPlanQuery } from '../../../../../__generated__/graphql';
import { LoadingButton } from '../../../../core/LoadingButton';

export interface LockedFspPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canUnlock: boolean;
  canSendForApproval: boolean;
}

export const LockedFspPaymentPlanHeaderButtons = ({
  paymentPlan,
  canUnlock,
  canSendForApproval,
}: LockedFspPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = paymentPlan;
  const { showMessage } = useSnackbar();
  const {
    mutatePaymentPlanAction: unlock,
    loading: loadingUnlock,
  } = usePaymentPlanAction(
    Action.UnlockFsp,
    id,
    () => showMessage(t('Payment Plan FSPs have been unlocked.')),
    () => showMessage(t('Error during unlocking Payment Plan.')),
  );
  const {
    mutatePaymentPlanAction: sendForApproval,
    loading: loadingSendForApproval,
  } = usePaymentPlanAction(
    Action.SendForApproval,
    id,
    () => showMessage(t('Payment Plan has been sent for approval.')),
    () => showMessage(t('Error during sending Payment Plan for approval.')),
  );

  return (
    <Box display='flex' alignItems='center'>
      {canUnlock && (
        <Box m={2}>
          <LoadingButton
            loading={loadingUnlock}
            variant='outlined'
            color='primary'
            onClick={() => unlock()}
          >
            {t('Unlock FSP')}
          </LoadingButton>
        </Box>
      )}
      {canSendForApproval && (
        <Box m={2}>
          <LoadingButton
            loading={loadingSendForApproval}
            variant='contained'
            color='primary'
            onClick={() => sendForApproval()}
          >
            {t('Send For Approval')}
          </LoadingButton>
        </Box>
      )}
    </Box>
  );
};
