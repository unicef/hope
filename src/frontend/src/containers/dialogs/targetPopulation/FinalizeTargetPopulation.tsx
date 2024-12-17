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

export interface FinalizeTargetPopulationPropTypes {
  open: boolean;
  setOpen: (open: boolean) => void;
  totalHouseholds: number;
  targetPopulationId: string;
}

export const FinalizeTargetPopulation = ({
  open,
  setOpen,
  totalHouseholds,
  targetPopulationId,
}: FinalizeTargetPopulationPropTypes): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const { mutatePaymentPlanAction: finalizeAction, loading: loadingFinalize } =
    usePaymentPlanAction(Action.Finish, targetPopulationId, () => {
      showMessage(t('Target Population Finalized'));
      navigate(`/${baseUrl}/target-population/`);
    });

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <DialogTitleWrapper>
        <DialogTitle>{t('Send to Cash Assist')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          {t('Are you sure you want to push')} {totalHouseholds}{' '}
          {t(
            'households to CashAssist? Target population will not be editable further.',
          )}
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
          <LoadingButton
            onClick={() => finalizeAction(targetPopulationId)}
            color="primary"
            variant="contained"
            loading={loadingFinalize}
            disabled={loadingFinalize || !totalHouseholds}
            data-cy="button-target-population-send-to-cash-assist"
          >
            {t('Send to cash assist')}
          </LoadingButton>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
