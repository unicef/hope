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
import { LoadingButton } from '@core/LoadingButton';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

export interface LockFspPaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
}

export function LockFspPaymentPlan({
  paymentPlan,
  permissions,
}: LockFspPaymentPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const { mutatePaymentPlanAction: lock, loading: loadingLock } =
    usePaymentPlanAction(
      Action.LockFsp,
      paymentPlan.id,
      () => showMessage(t('Payment Plan FSPs are locked.')),
      () => setLockDialogOpen(false),
    );

  const canLockFsp =
    paymentPlan.deliveryMechanisms.length > 0 &&
    hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions);

  return (
    <>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setLockDialogOpen(true)}
          data-cy="button-lock-plan"
          disabled={!canLockFsp || !isActiveProgram}
        >
          {t('Lock FSP')}
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
          <DialogTitle>{t('Lock FSP')}</DialogTitle>
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
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => lock()}
              data-cy="button-submit"
            >
              {t('Lock FSP')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
