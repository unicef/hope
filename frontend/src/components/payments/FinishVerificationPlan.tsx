import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import CheckRoundedIcon from '@material-ui/icons/CheckRounded';
import styled from 'styled-components';

import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  useFinishCashPlanPaymentVerificationMutation,
  useCashPlanQuery,
} from '../../__generated__/graphql';
import { CashPlan } from '../../apollo/queries/CashPlan';
import { LoadingComponent } from '../LoadingComponent';

export interface Props {
  cashPlanVerificationId: string;
  cashPlanId: string;
}
export function FinishVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: Props): React.ReactElement {
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useFinishCashPlanPaymentVerificationMutation();
  const { id } = useParams();
  const { data, loading } = useCashPlanQuery({
    variables: { id },
  });
  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }
  const { cashPlan } = data;
  const verificationPlan =
    cashPlan && cashPlan.verifications && cashPlan.verifications.edges.length
      ? cashPlan.verifications.edges[0].node
      : null;

  const finish = async (): Promise<void> => {
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
    showMessage('Verification plan has been finished');
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

  const beneficiariesPercent = () => {
    if (verificationPlan?.respondedCount && verificationPlan?.sampleSize !== 0)
      return (
        (verificationPlan?.respondedCount / verificationPlan?.sampleSize) * 100
      );
    return null;
  };

  const grievanceTickets = () => {
    if (
      verificationPlan?.notReceivedCount &&
      verificationPlan?.sampleSize &&
      verificationPlan?.respondedCount
    ) {
      return (
        verificationPlan?.notReceivedCount +
        (verificationPlan?.sampleSize - verificationPlan?.respondedCount) +
        verificationPlan?.receivedWithProblemsCount
      );
    }
    return null;
  };

  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-ed-plan'
        >
          Finish
        </Button>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Finish Verification Plan
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {beneficiariesPercent() && (
                <div>
                  Only
                  {beneficiariesPercent()} % of the beneficiaries have responded
                  to this payment verification.
                </div>
              )}
              <div>Are you sure that you want to finish?</div>
              {grievanceTickets() && (
                <div>
                  Closing this verification will generate {grievanceTickets()}
                  grievance tickets.
                </div>
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => finish()}
              data-cy='button-submit'
            >
              FINISH
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
