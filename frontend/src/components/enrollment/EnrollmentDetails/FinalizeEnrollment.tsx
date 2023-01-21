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
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useFinalizeTpMutation } from '../../../__generated__/graphql';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';

export interface FinalizeEnrollmentProps {
  open: boolean;
  setOpen: Function;
  targetPopulationId: string;
  totalHouseholds: number;
}

export const FinalizeEnrollment = ({
  open,
  setOpen,
  totalHouseholds,
  targetPopulationId,
}: FinalizeEnrollmentProps): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, { loading }] = useFinalizeTpMutation();
  const onSubmit = (id: string): void => {
    mutate({
      variables: {
        id,
      },
    }).then(() => {
      setOpen(false);
      showMessage(t('Target Population Finalized'), {
        pathname: `/${businessArea}/target-population/${id}`,
      });
    });
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <DialogTitleWrapper>
        <DialogTitle>{t('Send to Cash Assist')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          {t('Are you sure you want to sent')} {totalHouseholds}{' '}
          {t(
            'households to Payment Module? Enrollment will not be editable further.',
          )}
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
          <LoadingButton
            onClick={() => onSubmit(targetPopulationId)}
            color='primary'
            variant='contained'
            loading={loading}
            disabled={loading || !totalHouseholds}
            data-cy='button-enrollment-send-to-payment-module'
          >
            {t('Send to Payment Module')}
          </LoadingButton>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
