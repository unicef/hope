import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { useDeletePaymentPMutation } from '@generated/graphql';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useNavigate } from 'react-router-dom';
import { ReactElement } from 'react';

export interface DeleteTargetPopulationProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const DeleteTargetPopulation = ({
  open,
  setOpen,
  targetPopulationId,
}: DeleteTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const [mutate, { loading: loadingDelete }] = useDeletePaymentPMutation();

  const handleDelete = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentPlanId: targetPopulationId,
        },
      });
      showMessage(t('Target Population Deleted'));
      navigate(`/${baseUrl}/payment-module/payment-plans`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle>{t('Delete Target Population')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to remove this Target Population?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              color="primary"
              variant="contained"
              loading={loadingDelete}
              onClick={() => handleDelete()}
              data-cy="button-delete"
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
};
