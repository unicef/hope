import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Delete } from '@material-ui/icons';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import {
  PaymentPlanQuery,
  useDeletePpMutation,
} from '../../../../__generated__/graphql';
import { LoadingButton } from '../../../core/LoadingButton';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { useProgramContext } from '../../../../programContext';

export interface DeletePaymentPlanProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const DeletePaymentPlan = ({
  paymentPlan,
}: DeletePaymentPlanProps): React.ReactElement => {
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
      showMessage(t('Payment Plan Deleted'), {
        pathname: `/${baseUrl}/payment-module`,
        historyMethod: 'push',
        dataCy: 'snackbar-payment-plan-remove-success',
      });
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
};
