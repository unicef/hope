import React, { useState } from 'react';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import styled from 'styled-components';
import ClearIcon from '@material-ui/icons/Clear';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { ErrorButtonContained } from '../ErrorButtonContained';
import { ErrorButton } from '../ErrorButton';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useDiscardCashPlanPaymentVerificationMutation } from '../../__generated__/graphql';
import { CashPlan } from '../../apollo/queries/CashPlan';

export interface Props {
  cashPlanVerificationId: string;
  cashPlanId: string;
}
export function DiscardVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: Props): React.ReactElement {
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useDiscardCashPlanPaymentVerificationMutation();

  const discard = async (): Promise<void> => {
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
    showMessage('Verification plan has been discarded.');
  };

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
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Discard Verification Plan
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                Are you sure you would like to delete payment verification
                records <br /> and restart the verification process?
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>CANCEL</Button>
            <ErrorButtonContained
              type='submit'
              onClick={() => discard()}
              data-cy='button-submit'
            >
              DISCARD
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
