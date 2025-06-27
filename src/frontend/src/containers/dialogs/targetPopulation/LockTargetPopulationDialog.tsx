import { Button, DialogContent, DialogTitle } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { Action } from '@generated/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';
import { ReactElement } from 'react';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';

export interface LockTargetPopulationDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const LockTargetPopulationDialog = ({
  open,
  setOpen,
  targetPopulationId,
}: LockTargetPopulationDialogProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const { showMessage } = useSnackbar();
  const { mutatePaymentPlanAction: lock, loading: loadingLock } =
    usePaymentPlanAction(Action.TpLock, targetPopulationId, () =>
      showMessage(t('Payment Plan has been locked.')),
    );
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle>{t('Lock Target Population')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t(
              'After you lock this Target Population, the selected criteria will no longer accept new households that may get merged to Population in the future.',
            )}
          </DialogDescription>
          <DialogDescription>
            {t(
              'Note: You may duplicate the Programme Population target criteria at any time.',
            )}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              color="primary"
              variant="contained"
              loading={loadingLock}
              onClick={() => {
                lock().then(() => {
                  setOpen(false);
                  showMessage(t('Target Population Locked'));
                  navigate(
                    `/${baseUrl}/target-population/${targetPopulationId}`,
                  );
                });
              }}
              data-cy="button-target-population-modal-lock"
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
};
