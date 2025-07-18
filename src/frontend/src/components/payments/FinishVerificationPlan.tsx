import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { getPercentage, showApiErrorMessages } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { useProgramContext } from '../../programContext';
import { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';

export interface FinishVerificationPlanProps {
  verificationPlan: PaymentVerificationPlanDetails['paymentVerificationPlans'][number];
  cashOrPaymentPlanId: string;
}

export function FinishVerificationPlan({
  verificationPlan,
  cashOrPaymentPlanId,
}: FinishVerificationPlanProps): ReactElement {
  const { t } = useTranslation();
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const finishVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsFinishVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          verificationPlanId: verificationPlan.id,
        },
      ),
  });

  const finish = async (): Promise<void> => {
    try {
      await finishVerificationPlanMutation.mutateAsync();
      setFinishDialogOpen(false);
      showMessage(t('Verification plan has been finished'));
    } catch (error) {
      showApiErrorMessages(error, showMessage);
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
      return beneficiariesFloat < 100
        ? `Only ${beneficiariesPercent()}`
        : 'All';
    }
    return 'None';
  };

  return (
    <>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setFinishDialogOpen(true)}
          data-cy="button-ed-plan"
          disabled={!isActiveProgram}
        >
          {t('Finish')}
        </Button>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Finish Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box>
              {beneficiariesPercent() && (
                <Typography variant="body2" style={{ marginTop: '20px' }}>
                  {generateModalPrefixText()}
                  {t(
                    ' of the beneficiaries have responded to this payment verification.',
                  )}
                </Typography>
              )}
              <Typography variant="body2">
                {t('Are you sure that you want to finish?')}
              </Typography>
              {grievanceTickets() ? (
                <Typography
                  style={{ marginTop: '20px', marginBottom: '20px' }}
                  variant="body2"
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
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => finish()}
              data-cy="button-submit"
            >
              {t('FINISH')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
