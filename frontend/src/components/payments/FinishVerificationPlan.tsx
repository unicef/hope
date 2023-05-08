import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { getPercentage } from '../../utils/utils';
import {
  PaymentPlanQuery,
  useFinishPaymentVerificationPlanMutation,
} from '../../__generated__/graphql';

export interface FinishVerificationPlanProps {
  verificationPlan: PaymentPlanQuery['paymentPlan']['verificationPlans']['edges'][0]['node'];
  cashOrPaymentPlanId: string;
}

export function FinishVerificationPlan({
  verificationPlan,
  cashOrPaymentPlanId,
}: FinishVerificationPlanProps): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useFinishPaymentVerificationPlanMutation();

  const finish = async (): Promise<void> => {
    try {
      await mutate({
        variables: { paymentVerificationPlanId: verificationPlan.id },
        refetchQueries,
      });
      showMessage(t('Verification plan has been finished'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
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
    if (verificationPlan?.sampleSize) {
      const notReceivedTicketsCount = verificationPlan?.notReceivedCount;
      const receivedWithProblemsTicketsCount =
        verificationPlan?.receivedWithProblemsCount;

      return notReceivedTicketsCount + receivedWithProblemsTicketsCount;
    }
    return null;
  };

  const generateModalPrefixText = (): string => {
    const beneficiariesFloat = parseFloat(beneficiariesPercent());
    if (beneficiariesFloat) {
      return beneficiariesFloat < 100 ? `Only ${beneficiariesPercent()}` : "All"
    }
    return "None"
  }

  return (
    <>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-ed-plan'
        >
          {t('Finish')}
        </Button>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Finish Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box>
              {beneficiariesPercent() && (
                <Typography variant='body2' style={{ marginTop: '20px' }}>
                  {generateModalPrefixText()}
                  {t(
                    ' of the beneficiaries have responded to this payment verification.',
                  )}
                </Typography>
              )}
              <Typography variant='body2'>
                {t('Are you sure that you want to finish?')}
              </Typography>
              {grievanceTickets() ? (
                <Typography
                  style={{ marginTop: '20px', marginBottom: '20px' }}
                  variant='body2'
                >
                  {t('Closing this verification will generate')}{' '}
                  {grievanceTickets()} {t('grievance tickets')}.
                </Typography>
              ) : null}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => finish()}
              data-cy='button-submit'
            >
              {t('FINISH')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
