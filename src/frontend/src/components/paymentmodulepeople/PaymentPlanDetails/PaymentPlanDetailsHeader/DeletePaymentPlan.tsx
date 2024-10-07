import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Delete } from '@mui/icons-material';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { PaymentPlanQuery, useDeletePpMutation } from '@generated/graphql';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { useProgramContext } from '../../../../programContext';
import { useNavigate } from 'react-router-dom';

export interface DeletePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export function DeletePaymentPlan({
  paymentPlan,
}: DeletePaymentPlanProps): React.ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { baseUrl } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const [mutate, { loading: loadingDelete }] = useDeletePpMutation();
  const { id } = paymentPlan;
  const { isActiveProgram } = useProgramContext();

  const handleDelete = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentPlanId: id,
        },
      });
      showMessage(t('Payment Plan Deleted'));
      navigate(`/${baseUrl}/payment-module/payment-plans`);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };
  return (
    <>
      <Box p={2}>
        <IconButton
          onClick={() => setDeleteDialogOpen(true)}
          disabled={!isActiveProgram}
          data-cy="button-delete-payment-plan"
        >
          <Delete />
        </IconButton>
      </Box>
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Delete Payment Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t('Are you sure you want to remove this Payment Plan?')}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading={loadingDelete}
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => handleDelete()}
              data-cy="button-submit"
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
