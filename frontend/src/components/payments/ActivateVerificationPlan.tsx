import React, { useState } from 'react';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import styled from 'styled-components';
import { useSnackbar } from '../../hooks/useSnackBar';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useActivateCashPlanPaymentVerificationMutation } from '../../__generated__/graphql';
import { CashPlan } from '../../apollo/queries/CashPlan';

export interface Props {
  cashPlanVerificationId: string;
  cashPlanId: string;
}

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogContainer = styled.div`
  width: 700px;
`;

export function ActivateVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: Props): React.ReactElement {
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);

  const { showMessage } = useSnackbar();
  const [mutate] = useActivateCashPlanPaymentVerificationMutation();
  const activate = async (): Promise<void> => {
    const { errors } = await mutate({
      variables: { cashPlanVerificationId },
      refetchQueries: () => [
        { query: CashPlan, variables: { id: cashPlanId } },
      ],
    });
    if (errors) {
      showMessage('Error while submitting');
      return;
    }
    showMessage('Verification plan has been activated.');
  };
  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setActivateDialogOpen(true)}
          data-cy='button-activate-plan'
        >
          ACTIVATE
        </Button>
      </Box>
      <Dialog
        open={activateDialogOpen}
        onClose={() => setActivateDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Activate Verification Plan
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              Are you sure you want to activate the Verification Plan for this
              Cash Plan?
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
              ACTIVATE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
