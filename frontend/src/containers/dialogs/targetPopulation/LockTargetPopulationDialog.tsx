import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useLockTpMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface ApproveCandidateListPropTypes {
  open: boolean;
  setOpen: Function;
}

export function LockTargetPopulationDialog({
  open,
  setOpen,
  targetPopulationId,
}): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useLockTpMutation();
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>{t('Lock Target Population')}</Typography>
          </DialogTitle>
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
              color='primary'
              variant='contained'
              loading={loading}
              onClick={() => {
                mutate({
                  variables: { id: targetPopulationId },
                }).then(() => {
                  setOpen(false);
                  showMessage(t('Target Population Locked'), {
                    pathname: `/${businessArea}/target-population/${targetPopulationId}`,
                  });
                });
              }}
              data-cy='button-target-population-modal-lock'
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
}
