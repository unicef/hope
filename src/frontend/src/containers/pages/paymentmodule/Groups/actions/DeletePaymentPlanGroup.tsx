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
import { useMutation } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { PaymentPlanGroupDetail } from '../types';

interface DeletePaymentPlanGroupProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeletePaymentPlanGroup({
  group,
}: DeletePaymentPlanGroupProps): ReactElement | null {
  const { t } = useTranslation();
  const { businessArea, baseUrl } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const navigate = useNavigate();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // Only show delete button when group has no payment plans
  if (!group || group.paymentPlansCount > 0) return null;

  const { mutateAsync: deleteGroup, isPending: loadingDelete } = useMutation({
    mutationFn: async () => {
      // TODO: RestService.restBusinessAreasPaymentPlanGroupsDestroy({ businessAreaSlug: businessArea, id: group.id })
      // Endpoint: DELETE /api/rest/business-areas/{ba_slug}/payment-plan-groups/{id}/
      throw new Error('Delete endpoint not yet available');
    },
  });

  const handleDelete = async (): Promise<void> => {
    try {
      await deleteGroup();
      showMessage(t('Group Deleted'));
      navigate(`/${baseUrl}/payment-module/groups`);
    } catch (e: any) {
      showMessage(e?.message ?? t('Delete failed'));
    }
  };

  return (
    <>
      <Box p={2}>
        <IconButton
          onClick={() => setDeleteDialogOpen(true)}
          data-cy="button-delete-group"
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
          <DialogTitle>{t('Delete Group')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t('Are you sure you want to remove this Group?')}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
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
