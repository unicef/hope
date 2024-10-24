import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';
import { useSnackbar } from '@hooks/useSnackBar';
import { Action, PaymentPlanQuery } from '@generated/graphql';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';

export interface LockPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function LockPaymentPlan({
  paymentPlan,
}: LockPaymentPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const { mutatePaymentPlanAction: lock, loading: loadingLock } =
    usePaymentPlanAction(
      Action.Lock,
      paymentPlan.id,
      () => showMessage(t('Payment Plan has been locked.')),
      () => setLockDialogOpen(false),
    );

  return (
    <>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setLockDialogOpen(true)}
          data-cy="button-lock-plan"
        >
          {t('Lock')}
        </Button>
      </Box>
      <Dialog
        open={lockDialogOpen}
        onClose={() => setLockDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Lock Payment Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'After you lock this Payment Plan, you will be able to run entitlement formula for selected target population.',
              )}
            </Box>
            {paymentPlan.paymentsConflictsCount > 0 && (
              <Box p={5}>
                <GreyText>
                  {t('Note:')}{' '}
                  {paymentPlan.paymentsConflictsCount === 1
                    ? t('There is')
                    : t('There are')}{' '}
                  {paymentPlan.paymentsConflictsCount}{' '}
                  {paymentPlan.paymentsConflictsCount === 1
                    ? t('household')
                    : t('households')}{' '}
                  {t('that will be ignored in this Payment Plan.')}
                </GreyText>
              </Box>
            )}
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLockDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading={loadingLock}
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => lock()}
              data-cy="button-submit"
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
