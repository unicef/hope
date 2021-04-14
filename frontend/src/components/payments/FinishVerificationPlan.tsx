import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Button,
  DialogContent,
  DialogTitle,
  Box,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  useFinishCashPlanPaymentVerificationMutation,
  useCashPlanQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { getPercentage } from '../../utils/utils';

export interface Props {
  cashPlanVerificationId: string;
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

export function FinishVerificationPlan({
  cashPlanVerificationId,
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
  const verificationPlan = cashPlan?.verifications?.edges?.length
    ? cashPlan.verifications.edges[0].node
    : null;

  const finish = async (): Promise<void> => {
    const { errors } = await mutate({
      variables: { cashPlanVerificationId },
    });
    if (errors) {
      showMessage('Error while submitting');
      return;
    }
    showMessage('Verification plan has been finished');
  };

  const beneficiariesPercent = (): string => {
    const responded = verificationPlan?.respondedCount || 0;
    const sampleSize = verificationPlan?.sampleSize;
    if (sampleSize) {
      return getPercentage(responded, sampleSize);
    }
    return null;
  };

  const grievanceTickets = (): number => {
    const notReceivedCount = verificationPlan?.notReceivedCount || 0;
    const receivedWithProblemsCount =
      verificationPlan?.receivedWithProblemsCount || 0;
    const sampleSize = verificationPlan?.sampleSize;
    const responded = verificationPlan?.respondedCount || 0;

    if (sampleSize) {
      return (
        notReceivedCount + receivedWithProblemsCount + (sampleSize - responded)
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
            <Box>
              {beneficiariesPercent() && (
                <Typography variant='body2' style={{ marginTop: '20px' }}>
                  Only {beneficiariesPercent()} of the beneficiaries have
                  responded to this payment verification.
                </Typography>
              )}
              <Typography variant='body2'>
                Are you sure that you want to finish?
              </Typography>
              {grievanceTickets() ? (
                <Typography
                  style={{ marginTop: '20px', marginBottom: '20px' }}
                  variant='body2'
                >
                  Closing this verification will generate {grievanceTickets()}{' '}
                  grievance tickets.
                </Typography>
              ) : null}
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
