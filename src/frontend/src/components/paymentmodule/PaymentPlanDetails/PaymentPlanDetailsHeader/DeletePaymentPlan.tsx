import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Delete } from '@mui/icons-material';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from '../../../../programContext';

export interface DeletePaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function DeletePaymentPlan({
  paymentPlan,
}: DeletePaymentPlanProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { baseUrl } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { mutateAsync: deletePaymentPlan, isPending: loadingDelete } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansDestroy({
          businessAreaSlug,
          id,
          programSlug,
        }),
    });
  const { id } = paymentPlan;
  const { isActiveProgram } = useProgramContext();

  const handleDelete = async (): Promise<void> => {
    try {
      await deletePaymentPlan({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id,
      });
      showMessage(t('Payment Plan Deleted'));
      navigate(`/${baseUrl}/payment-module/payment-plans`);
    } catch (e) {
      showMessage(e);
    }
  };

  return (
    <>
      <Box p={2}>
        <IconButton
          onClick={() => setDeleteDialogOpen(true)}
          disabled={!isActiveProgram}
          data-cy="button-delete-pp"
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
