import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import ClearIcon from '@material-ui/icons/Clear';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useDiscardPaymentVerificationPlanMutation } from '../../__generated__/graphql';
import { ErrorButton } from '../core/ErrorButton';
import { ErrorButtonContained } from '../core/ErrorButtonContained';

export interface DiscardVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export function DiscardVerificationPlan({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: DiscardVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useDiscardPaymentVerificationPlanMutation();

  const discard = async (): Promise<void> => {
    const { errors } = await mutate({
      variables: { paymentVerificationPlanId },
      refetchQueries,
    });
    if (errors) {
      showMessage(t('Error while submitting'));
      return;
    }
    showMessage(t('Verification plan has been discarded.'));
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-discard-plan'
        >
          DISCARD
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
            {t('Discard Verification Plan')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                {t(
                  'Are you sure you would like to delete payment verification records',
                )}
                <br /> {t('and restart the verification process?')}
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
              onClick={() => discard()}
              data-cy='button-submit'
            >
              {t('DISCARD')}
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
