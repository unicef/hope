import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { useDeletePaymentVerificationPlanMutation } from '@generated/graphql';
import { ErrorButton } from '@core/ErrorButton';
import { ErrorButtonContained } from '@core/ErrorButtonContained';
import { usePaymentRefetchQueries } from '@hooks/usePaymentRefetchQueries';
import { useProgramContext } from '../../programContext';

export interface DeleteVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export function DeleteVerificationPlan({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: DeleteVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const [mutate] = useDeletePaymentVerificationPlanMutation();

  const handleDeleteVerificationPlan = async (): Promise<void> => {
    const { errors } = await mutate({
      variables: { paymentVerificationPlanId },
      refetchQueries,
    });
    if (errors) {
      showMessage(t('Error while submitting'));
      return;
    }
    setDeleteDialogOpen(false);
    showMessage(t('Verification plan has been deleted.'));
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setDeleteDialogOpen(true)}
          data-cy="button-delete-plan"
          disabled={!isActiveProgram}
        >
          DELETE
        </ErrorButton>
      </Box>
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Delete Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                {t(
                  'Are you sure you would like to remove this verification plan?',
                )}
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <ErrorButtonContained
              type="submit"
              onClick={() => handleDeleteVerificationPlan()}
              data-cy="button-submit"
            >
              {t('DELETE')}
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
