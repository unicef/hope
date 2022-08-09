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
import { GreyText } from '../../../core/GreyText';
import { LoadingButton } from '../../../core/LoadingButton';
import { Missing } from '../../../core/Missing';

export interface LockPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const LockPaymentPlan = ({
  paymentPlan,
}: LockPaymentPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const {
    mutatePaymentPlanAction: lock,
    loading: loadingLock,
  } = usePaymentPlanAction(
    Action.Lock,
    paymentPlan.id,
    () => showMessage(t('Payment Plan has been locked.')),
    () => showMessage(t('Error during locking Payment Plan.')),
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
          {t('Lock')}
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
          <DialogTitle id='scroll-dialog-title'>
            {t('Lock Payment Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'After you lock this Payment Plan, you will be able to run entitlement formula for selected target population.',
              )}
            </Box>
            <Box p={5}>
              <GreyText>
                {t('Note:')} {t('There are')}{' '}
                {/* {paymentPlan.paymentsConflictsCount}{' '} */}
                <Missing />
                {t('households that will be ignored in this Payment Plan.')}
              </GreyText>
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
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
