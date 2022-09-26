import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import { usePaymentPlanAction } from '../../../../hooks/usePaymentPlanAction';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { Action, PaymentPlanQuery } from '../../../../__generated__/graphql';
import { LoadingButton } from '../../../core/LoadingButton';

export interface LockFspPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const LockFspPaymentPlan = ({
  paymentPlan,
}: LockFspPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const {
    mutatePaymentPlanAction: lock,
    loading: loadingLock,
  } = usePaymentPlanAction(
    Action.LockFsp,
    paymentPlan.id,
    () => showMessage(t('Payment Plan FSPs are locked.')),
    () => setLockDialogOpen(false),
  );

  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setLockDialogOpen(true)}
          data-cy='button-lock-plan'
        >
          {t('Lock FSP')}
        </Button>
      </Box>
      <Dialog
        open={lockDialogOpen}
        onClose={() => setLockDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>{t('Lock FSP')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'After you lock the FSP in this Payment Plan, you will be able to send the Payment Plan for approval.',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLockDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading={loadingLock}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => lock()}
              data-cy='button-submit'
            >
              {t('Lock FSP')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
