import { Button, DialogContent, DialogTitle } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useLockTpMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

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
  const { baseUrl } = useBaseUrl();

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
              color='primary'
              variant='contained'
              loading={loading}
              onClick={() => {
                mutate({
                  variables: { id: targetPopulationId },
                }).then(() => {
                  setOpen(false);
                  showMessage(t('Target Population Locked'), {
                    pathname: `/${baseUrl}/target-population/${targetPopulationId}`,
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
