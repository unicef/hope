import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../hooks/useSnackBar';
import { ProgramStatus, useActivatePaymentVerificationPlanMutation } from '../../__generated__/graphql';
import { useProgramContext } from "../../programContext";

export interface ActivateVerificationPlanProps {
  paymentVerificationPlanId: string;
}

export const ActivateVerificationPlan = ({
  paymentVerificationPlanId,
}: ActivateVerificationPlanProps): React.ReactElement => {
  const { t } = useTranslation();
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);
  const { selectedProgram } = useProgramContext();

  const { showMessage } = useSnackbar();
  const [mutate] = useActivatePaymentVerificationPlanMutation();
  const activate = async (): Promise<void> => {
    try {
      await mutate({
        variables: { paymentVerificationPlanId },
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
    setActivateDialogOpen(false);
    showMessage(t('Verification plan has been activated.'));
  };
  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setActivateDialogOpen(true)}
          data-cy='button-activate-plan'
          disabled={selectedProgram?.status !== ProgramStatus.Active}
        >
          {t('ACTIVATE')}
        </Button>
      </Box>
      <Dialog
        open={activateDialogOpen}
        onClose={() => setActivateDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Activate Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'Are you sure you want to activate the Verification Plan for this Payment Plan?',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setActivateDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => activate()}
              data-cy='button-submit'
            >
              {t('ACTIVATE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
