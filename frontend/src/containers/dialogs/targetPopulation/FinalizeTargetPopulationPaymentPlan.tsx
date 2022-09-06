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
import { useFinalizeTpMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface FinalizeTargetPopulationPaymentPlanProps {
  open: boolean;
  setOpen: Function;
  totalHouseholds: number;
  targetPopulationId: string;
}

export const FinalizeTargetPopulationPaymentPlan = ({
  open,
  setOpen,
  totalHouseholds,
  targetPopulationId,
}: FinalizeTargetPopulationPaymentPlanProps): React.ReactElement => {
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
        <DialogTitle id='scroll-dialog-title'>
          <Typography variant='h6'>{t('Send to HOPE')}</Typography>
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          {t('Are you sure you want to send')} {totalHouseholds}{' '}
          {t(
            'households to HOPE? They will be accessible in Payment Module. Target population will not be editable further.',
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
            data-cy='button-target-population-modal-send-to-hope'
          >
            {t('Send to Hope')}
          </LoadingButton>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
