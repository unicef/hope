import { Button, DialogContent, DialogTitle, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from '../../../programContext';
import { ReactElement } from 'react';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';

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
}: FinalizeTargetPopulationPaymentPlanProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();

  const { mutateAsync: markReady, isPending: loadingFinish } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsMarkReadyRetrieve({
        businessAreaSlug: businessArea,
        id: targetPopulationId,
        programSlug: programId,
      }),
    onSuccess: () => {
      showMessage(t('Target Population Finalized'));
      setOpen(false);
      navigate(`/${baseUrl}/target-population/${targetPopulationId}`);
    },
    onError: (error) => {
      showMessage(
        error.message ||
          t('An error occurred while marking target population as ready.'),
      );
    },
  });

  const { isSocialDctType } = useProgramContext();

  const onSubmit = (): void => {
    markReady();
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
            onClick={() => onSubmit()}
            color="primary"
            variant="contained"
            loading={loadingFinish}
            disabled={loadingFinish || !totalHouseholds}
            data-cy="button-target-population-modal-send-to-hope"
          >
            {t('Mark Ready')}
          </LoadingButton>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
