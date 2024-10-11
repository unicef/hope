import { Button, DialogContent, DialogTitle, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { useFinalizeTpMutation } from '@generated/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from '../../../programContext';

export interface FinalizeTargetPopulationPaymentPlanProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  totalHouseholds: number;
  targetPopulationId: string;
}

export const FinalizeTargetPopulationPaymentPlan = ({
  open,
  setOpen,
  totalHouseholds,
  targetPopulationId,
}: FinalizeTargetPopulationPaymentPlanProps): React.ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const [mutate, { loading }] = useFinalizeTpMutation();
  const { isSocialDctType } = useProgramContext();
  const onSubmit = (id: string): void => {
    mutate({
      variables: {
        id,
      },
    }).then(() => {
      setOpen(false);
      showMessage(t('Target Population Finalized'));
      navigate(`/${baseUrl}/target-population/${id}`);
    });
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <DialogTitleWrapper>
        <DialogTitle>
          <Typography variant="h6">{t('Mark Ready')}</Typography>
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          {t('Are you sure you want to send')} {totalHouseholds}{' '}
          {t(
            (isSocialDctType ? 'individuals' : 'households') +
              ' to HOPE? They will be accessible in Payment Module. Target population will not be editable further.',
          )}
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
          <LoadingButton
            onClick={() => onSubmit(targetPopulationId)}
            color="primary"
            variant="contained"
            loading={loading}
            disabled={loading || !totalHouseholds}
            data-cy="button-target-population-modal-send-to-hope"
          >
            {t('Mark Ready')}
          </LoadingButton>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
