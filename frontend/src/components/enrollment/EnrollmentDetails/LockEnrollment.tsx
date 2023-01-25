import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '../../core/LoadingButton';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useLockTpMutation } from '../../../__generated__/graphql';
import { Missing } from '../../core/Missing';

export interface LockEnrollmentProps {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
}

export const LockEnrollment = ({
  open,
  setOpen,
  targetPopulationId,
}: LockEnrollmentProps): React.ReactElement => {
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
          <DialogTitle>{t('Lock Enrollment')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <Missing />
          </DialogDescription>
          <DialogDescription>
            <Missing />
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
                  showMessage(t('Enrollment Locked'), {
                    pathname: `/${businessArea}/enrollment/${targetPopulationId}`,
                  });
                });
              }}
              data-cy='button-enrollment-lock'
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
};
