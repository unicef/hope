import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import ClearIcon from '@material-ui/icons/Clear';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useDiscardPaymentVerificationPlanMutation } from '../../__generated__/graphql';
import { ErrorButton } from '../core/ErrorButton';
import { ErrorButtonContained } from '../core/ErrorButtonContained';

export interface DiscardVerificationPlanProps {
  paymentVerificationPlanId: string;
}

export function DiscardVerificationPlan({
  paymentVerificationPlanId,
}: DiscardVerificationPlanProps): React.ReactElement {
  const { t } = useTranslation();
  const [discardDialogOpen, setDiscardDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useDiscardPaymentVerificationPlanMutation();

  const discard = async (): Promise<void> => {
    try {
      await mutate({
        variables: { paymentVerificationPlanId },
      });
      setDiscardDialogOpen(false);
      showMessage(t('Verification plan has been discarded.'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setDiscardDialogOpen(true)}
          data-cy='button-discard-plan'
        >
          DISCARD
        </ErrorButton>
      </Box>
      <Dialog
        open={discardDialogOpen}
        onClose={() => setDiscardDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Discard Verification Plan')}</DialogTitle>
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
            <Button onClick={() => setDiscardDialogOpen(false)}>
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
