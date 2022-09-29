import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import ClearIcon from '@material-ui/icons/Clear';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useDeletePaymentVerificationPlanMutation } from '../../__generated__/graphql';
import { ErrorButton } from '../core/ErrorButton';
import { ErrorButtonContained } from '../core/ErrorButtonContained';

export interface DeleteVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashPlanId: string;
}

export function DeleteVerificationPlan({
  paymentVerificationPlanId,
  cashPlanId,
}: DeleteVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashPlanId);
  const { t } = useTranslation();
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
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
    showMessage(t('Verification plan has been deleted.'));
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-delete-plan'
        >
          DELETE
        </ErrorButton>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Delete Verification Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                {t(
                  'Are you sure you would like to delete this verification plan?',
                )}
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <ErrorButtonContained
              type='submit'
              onClick={() => handleDeleteVerificationPlan()}
              data-cy='button-submit'
            >
              {t('DELETE')}
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
