import { Button, DialogContent, DialogTitle } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { useLockTpMutation } from '@generated/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';

export interface LockTargetPopulationDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const LockTargetPopulationDialog = ({
  open,
  setOpen,
  targetPopulationId,
}: LockTargetPopulationDialogProps): React.ReactElement => {
  const history = useHistory();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useLockTpMutation();
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
              loading={loading}
              onClick={() => {
                mutate({
                  variables: { id: targetPopulationId },
                }).then(() => {
                  setOpen(false);
                  showMessage(t('Target Population Locked'));
                  history.push(
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
